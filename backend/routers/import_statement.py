"""
Imports router — parses CSV/XLSX/XLS/PDF statements and ingests confirmed rows
into Expenses/Income.

Supported formats:
  - eSewa XLS wallet statement: Dr./Cr. columns, multi-row metadata header
  - Khalti XLSX: Amount(-) Rs / Amount(+) Rs columns, clean headers
  - Sajilo eBanking PDF: text-based Debit/Credit layout (no extractable table)
  - Generic CSV/XLSX: falls back to title-keyword direction inference
"""

import io
import re
from datetime import date, datetime
import pandas as pd
import pdfplumber
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from JWT_Authentication.auth import get_current_user
from sql_Alchemy_db_model.expense_models import Expenses
from sql_Alchemy_db_model.income_model import Income
from category_rules import suggest_category
from datetime import date as date_today
from sqlalchemy import func
from sql_Alchemy_db_model.budget_model import Budget
from sql_Alchemy_db_model.user_models import Users
from routers.email_notifications import send_budget_exceeded_email


router_imports = APIRouter()

REQUIRED_COLUMNS = {"date", "title", "amount"}

INCOME_INDICATORS = [
    "transferred from",
    "received from",
    "salary",
    "deposit",
    "credit",
    "refund",
    "cashback",
    "load",
    "int.pd",       # bank interest payment
    "wd:",          # wallet deposit prefix used by some banks
    "cips",         # interbank transfer credit
]

DATE_KEYWORDS = {"date", "date time", "transaction date", "value date"}


class ParsedTransaction(BaseModel):
    date: date
    title: str
    category: str
    description: str
    amount: float   # negative = expense, positive = income


class ConfirmIngestionInput(BaseModel):
    transactions: list[ParsedTransaction]


# ---------------------------------------------------------------------------
# File readers
# ---------------------------------------------------------------------------

def _parse_csv(file_bytes: bytes) -> pd.DataFrame:
    """
    Read a CSV file into a DataFrame.

    Args:
        file_bytes (bytes): Raw CSV file content.

    Returns:
        pd.DataFrame: Parsed rows.
    """
    return pd.read_csv(io.BytesIO(file_bytes))


def _parse_xlsx(file_bytes: bytes) -> pd.DataFrame:
    """
    Read an XLSX file into a DataFrame.

    Args:
        file_bytes (bytes): Raw XLSX file content.

    Returns:
        pd.DataFrame: Parsed rows.
    """
    return pd.read_excel(io.BytesIO(file_bytes))


def _parse_xls(file_bytes: bytes) -> pd.DataFrame:
    """
    Read a legacy XLS file, handling multi-row metadata headers common in
    Nepali wallet/bank exports (e.g. eSewa statement).

    Scans rows until it finds one containing a date-like column keyword, uses
    that row as the header, and drops trailing summary/totals rows by filtering
    out any row where the date column cannot be parsed.

    Args:
        file_bytes (bytes): Raw XLS file content.

    Returns:
        pd.DataFrame: Parsed rows with real column headers.

    Raises:
        HTTPException: 422 if no recognizable header row is found.
    """
    raw = pd.read_excel(io.BytesIO(file_bytes), engine="xlrd", header=None)

    header_row_idx = None
    for i, row in raw.iterrows():
        cells = {str(v).strip().lower() for v in row.values if pd.notna(v)}
        if cells & DATE_KEYWORDS:
            header_row_idx = i
            break

    if header_row_idx is None:
        raise HTTPException(
            status_code=422,
            detail="Could not find a header row in this XLS file. "
                   "Expected a row containing a 'Date' or 'Date Time' column.",
        )

    df = pd.read_excel(
        io.BytesIO(file_bytes),
        engine="xlrd",
        header=header_row_idx,
    )

    # Drop trailing totals/summary rows.
    date_col = next(
        (c for c in df.columns if str(c).strip().lower() in DATE_KEYWORDS), None
    )
    if date_col:
        df = df[
            pd.to_datetime(df[date_col], errors="coerce").notna()
        ].reset_index(drop=True)

    return df


def _parse_pdf(file_bytes: bytes) -> list[dict]:
    """
    Parse a Sajilo eBanking-style PDF statement by reading raw text and
    extracting transaction rows with a regex pattern.

    The PDF uses a multi-column text layout that pdfplumber cannot extract
    as a table, so this function reads the raw text across all pages and
    matches lines of the form:
        DD-MM-YYYY  <description>  <debit|->  <credit|->  <balance>

    Rows without a parseable date (e.g. opening balance, closing balance,
    summary lines) are skipped automatically.

    Args:
        file_bytes (bytes): Raw PDF file content.

    Returns:
        list[dict]: Pre-normalized transaction dicts with keys:
            date, title, amount (signed float).

    Raises:
        HTTPException: 422 if no transaction rows are found.
    """
    full_text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    # Match lines starting with a date in DD-MM-YYYY format.
    # Capture: date, description (anything up to the debit/credit amounts), debit, credit.
    # Debit or credit may be '-' (meaning zero).
    pattern = re.compile(
        r"(\d{2}-\d{2}-\d{4})\s+(.+?)\s+([\d,]+\.\d{2}|-)\s+([\d,]+\.\d{2}|-)\s+([\d,]+\.\d{2})",
        re.MULTILINE,
    )

    transactions = []
    for match in pattern.finditer(full_text):
        raw_date, description, debit_str, credit_str, _ = match.groups()
        description = description.strip()

        try:
            parsed_date = datetime.strptime(raw_date, "%d-%m-%Y").date()
        except ValueError:
            continue

        debit = 0.0 if debit_str == "-" else float(debit_str.replace(",", ""))
        credit = 0.0 if credit_str == "-" else float(credit_str.replace(",", ""))

        if credit > 0 and debit == 0:
            signed_amount = abs(credit)
        else:
            signed_amount = -abs(debit)

        transactions.append({
            "date": parsed_date,
            "title": description,
            "amount": round(signed_amount, 2),
        })

    if not transactions:
        raise HTTPException(
            status_code=422,
            detail="Could not extract any transactions from this PDF. "
                   "Try CSV or XLSX instead.",
        )

    return transactions


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

def _resolve_direction_from_title(title: str) -> str:
    """
    Infer transaction direction from title keywords as a last-resort fallback.

    Args:
        title (str): The transaction title or narration.

    Returns:
        str: 'income' or 'expense'.
    """
    lower = title.lower()
    if any(kw in lower for kw in INCOME_INDICATORS):
        return "income"
    return "expense"


def _apply_category_and_description(transactions: list[dict]) -> list[dict]:
    """
    Apply auto-categorization and description fallback to a list of transaction dicts.

    Args:
        transactions (list[dict]): Dicts with at least 'title' key.

    Returns:
        list[dict]: Same dicts with 'category' and 'description' added.
    """
    for tx in transactions:
        tx["category"] = suggest_category(tx["title"]) or "Uncategorized"
        tx.setdefault("description", tx["title"])
    return transactions


def _normalize(df: pd.DataFrame) -> list[dict]:
    """
    Normalize a raw bank/wallet export DataFrame into standardized transaction dicts.

    Handles three debit/credit column patterns in order of preference:
      1. Dr. / Cr. columns (eSewa XLS wallet statement)
      2. Amount(-) Rs / Amount(+) Rs columns (Khalti XLSX)
      3. Debit / Credit columns (generic bank XLSX/CSV)
      4. Single signed amount column or title-keyword inference (generic fallback)

    Skips FAILED, PENDING, and CANCELED rows if a status column is present.

    Args:
        df (pd.DataFrame): Raw parsed DataFrame from any spreadsheet format.

    Returns:
        list[dict]: Normalized transactions with date, title, category,
            description, and signed amount (negative=expense, positive=income).

    Raises:
        HTTPException: 422 if required columns cannot be resolved.
    """
    col_lower = {str(c).strip().lower(): c for c in df.columns}

    # Status filtering.
    status_col = next(
        (col_lower[k] for k in ("status", "transaction state") if k in col_lower),
        None,
    )
    if status_col:
        completed_values = {"complete", "completed"}
        df = df[
            df[status_col].astype(str).str.strip().str.lower().isin(completed_values)
        ].reset_index(drop=True)

    # Date column.
    date_col = next(
        (col_lower[k] for k in DATE_KEYWORDS if k in col_lower), None
    )
    if not date_col:
        raise HTTPException(status_code=422, detail="Could not find a date column.")

    # Title column.
    title_col = next(
        (col_lower[k] for k in ("description", "title", "narration", "particulars") if k in col_lower),
        None,
    )
    if not title_col:
        raise HTTPException(status_code=422, detail="Could not find a title/description column.")

    # Amount/direction column detection — in priority order.
    dr_col = next((col_lower[k] for k in ("dr.", "dr") if k in col_lower), None)
    cr_col = next((col_lower[k] for k in ("cr.", "cr") if k in col_lower), None)
    debit_rs_col = col_lower.get("amount(-) rs")
    credit_rs_col = col_lower.get("amount(+) rs")
    debit_col = next((col_lower[k] for k in ("debit",) if k in col_lower), None)
    credit_col = next((col_lower[k] for k in ("credit",) if k in col_lower), None)
    amount_col = next(
        (col_lower[k] for k in ("amount", "transaction amount") if k in col_lower),
        None,
    )

    transactions = []
    for _, row in df.iterrows():
        try:
            title = str(row[title_col]).strip()
            parsed_date = pd.to_datetime(row[date_col]).date()

            if dr_col and cr_col:
                # Pattern 1: eSewa XLS — Dr./Cr. split.
                dr = float(row[dr_col] or 0)
                cr = float(row[cr_col] or 0)
                signed_amount = abs(cr) if (cr > 0 and dr == 0) else -abs(dr)

            elif debit_rs_col and credit_rs_col:
                # Pattern 2: Khalti XLSX — Amount(-)/Amount(+) split.
                debit = 0.0 if pd.isna(row[debit_rs_col]) else float(row[debit_rs_col])
                credit = 0.0 if pd.isna(row[credit_rs_col]) else float(row[credit_rs_col])
                signed_amount = abs(credit) if (credit > 0 and debit == 0) else -abs(debit)

            elif debit_col and credit_col:
                # Pattern 3: Generic bank — Debit/Credit split.
                raw_debit = str(row[debit_col]).strip()
                raw_credit = str(row[credit_col]).strip()
                debit = 0.0 if raw_debit in ("-", "", "nan") else float(raw_debit.replace(",", ""))
                credit = 0.0 if raw_credit in ("-", "", "nan") else float(raw_credit.replace(",", ""))
                signed_amount = abs(credit) if (credit > 0 and debit == 0) else -abs(debit)

            elif amount_col:
                # Pattern 4: Single amount column — infer direction from title.
                raw = float(row[amount_col])
                if raw < 0:
                    signed_amount = raw
                else:
                    direction = _resolve_direction_from_title(title)
                    signed_amount = abs(raw) if direction == "income" else -abs(raw)

            else:
                raise HTTPException(
                    status_code=422,
                    detail=f"Could not find an amount column. "
                           f"Available columns: {list(df.columns)}",
                )

            transactions.append({
                "date": parsed_date,
                "title": title,
                "amount": round(signed_amount, 2),
            })

        except HTTPException:
            raise
        except (ValueError, TypeError) as e:
            raise HTTPException(
                status_code=422,
                detail=f"Could not parse row: {row.to_dict()} — {e}",
            )

    return _apply_category_and_description(transactions)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router_imports.post(
    "/parse",
    summary="Parse an uploaded statement",
    description=(
        "Accepts CSV, XLSX, XLS, or PDF. Returns a preview without saving. "
        "Supports eSewa XLS, Khalti XLSX, Sajilo eBanking PDF, and generic CSV formats. "
        "FAILED/PENDING rows are skipped automatically."
    ),
)
async def parse_statement(
    file: UploadFile = File(...), current_user: dict = Depends(get_current_user)
):
    """
    Parse an uploaded statement file into a transaction preview.

    Args:
        file (UploadFile): The uploaded CSV, XLSX, XLS, or PDF statement.
        current_user (dict): The current authenticated user.

    Returns:
        list[dict]: Parsed transactions — date, title, category, description,
            signed amount (negative=expense, positive=income).

    Raises:
        HTTPException: 400 for unsupported file types, 422 for parsing failures.
    """
    file_bytes = await file.read()
    filename = file.filename.lower()

    if filename.endswith(".csv"):
        df = _parse_csv(file_bytes)
        return _normalize(df)
    elif filename.endswith(".xlsx"):
        df = _parse_xlsx(file_bytes)
        return _normalize(df)
    elif filename.endswith(".xls"):
        df = _parse_xls(file_bytes)
        return _normalize(df)
    elif filename.endswith(".pdf"):
        transactions = _parse_pdf(file_bytes)
        return _apply_category_and_description(transactions)
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Use CSV, XLSX, XLS, or PDF.",
        )


@router_imports.post(
    "/confirm",
    status_code=201,
    summary="Confirm ingestion of parsed transactions",
    description="Saves confirmed transactions — negative amount → Expenses, positive → Income. Triggers budget exceeded email if monthly limit is breached.",
)
def confirm_ingestion(
    payload: ConfirmIngestionInput,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Save confirmed parsed transactions into Expenses or Income based on amount sign.
    Triggers a budget exceeded email if the monthly total crosses the limit after import.

    Args:
        payload (ConfirmIngestionInput): Confirmed transactions with date, title,
            category, description, and signed amount.
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Returns:
        dict: Counts of expense and income rows created.
    """


    user_id = current_user["user_id"]
    expense_count = income_count = 0

    for tx in payload.transactions:
        if tx.amount < 0:
            db.add(Expenses(
                user_id=user_id,
                title=tx.title,
                category=tx.category,
                description=tx.description,
                date=tx.date,
                amount=abs(tx.amount),
            ))
            expense_count += 1
        else:
            db.add(Income(
                user_id=user_id,
                title=tx.title,
                received_from=tx.category,
                description=tx.description,
                date=tx.date,
                amount=tx.amount,
            ))
            income_count += 1

    db.commit()

    # Check budget after all rows committed — trigger email if limit breached.
    if expense_count > 0:
        budget = db.query(Budget).filter(Budget.user_id == user_id).first()
        if budget:
            month_start = date_today.today().replace(day=1)
            current_month_total = db.query(func.sum(Expenses.amount)).filter(
                Expenses.user_id == user_id,
                Expenses.date >= month_start,
            ).scalar() or 0

            if current_month_total > budget.monthly_limit:
                user = db.query(Users).filter(Users.id == user_id).first()
                background_tasks.add_task(
                    send_budget_exceeded_email,
                    to_email=user.email,
                    full_name=user.full_name,
                    monthly_limit=float(budget.monthly_limit),
                    current_total=round(float(current_month_total), 2),
                )

    return {
        "message": "Ingestion complete",
        "expenses_created": expense_count,
        "income_created": income_count,
    }