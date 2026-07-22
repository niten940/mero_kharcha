"""
Imports router — parses CSV/XLSX/PDF statements and ingests confirmed rows into Expenses/Income.
"""
import io
from datetime import date
import pandas as pd
import pdfplumber
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from JWT_Authentication.auth import get_current_user
from sqlAlchemy.expense_models import Expenses
from sqlAlchemy.income_model import Income

router_imports = APIRouter()

REQUIRED_COLUMNS = {"date", "title", "category", "description", "amount"}

class ParsedTransaction(BaseModel):
    date: date
    title: str
    category: str
    description: str
    amount: float

class ConfirmIngestionInput(BaseModel):
    transactions: list[ParsedTransaction]


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


def _parse_pdf(file_bytes: bytes) -> pd.DataFrame:
    """
    Extract the first table found across all pages of a PDF into a DataFrame.

    Args:
        file_bytes (bytes): Raw PDF file content.

    Returns:
        pd.DataFrame: Extracted rows, using the first table's first row as header.

    Raises:
        HTTPException: 422 if no extractable table is found.
    """
    header = None
    rows = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if not table:
                continue
            if header is None:
                header = [str(c).strip().lower() for c in table[0]]
                rows.extend(table[1:])
            else:
                rows.extend(table[1:])

    if header is None:
        raise HTTPException(status_code=422, detail="Could not extract a table from this PDF. Try CSV or XLSX instead.")

    return pd.DataFrame(rows, columns=header)


def _normalize(df: pd.DataFrame) -> list[dict]:
    """
    Validate required columns and convert a DataFrame into normalized transaction dicts.

    Args:
        df (pd.DataFrame): Raw parsed data from any supported file type.

    Returns:
        list[dict]: Transactions with date, title, category, description, amount.

    Raises:
        HTTPException: 422 if required columns are missing or a row fails to parse.
    """
    df.columns = [str(c).strip().lower() for c in df.columns]
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing required columns: {', '.join(missing)}")

    transactions = []
    for _, row in df.iterrows():
        try:
            transactions.append({
                "date": pd.to_datetime(row["date"]).date(),
                "title": str(row["title"]),
                "category": str(row["category"]),
                "description": str(row.get("description") or ""),
                "amount": round(float(row["amount"]), 2),
            })
        except (ValueError, TypeError):
            raise HTTPException(status_code=422, detail=f"Could not parse row: {row.to_dict()}")

    return transactions


@router_imports.post("/parse", summary="Parse an uploaded statement", description="Accepts a CSV, XLSX, or PDF file and returns a preview of parsed transactions without saving them.")
async def parse_statement(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """
    Parse an uploaded statement file into a transaction preview.

    Args:
        file (UploadFile): The uploaded CSV, XLSX, or PDF file.
        current_user (dict): The current authenticated user.

    Returns:
        list[dict]: Parsed transactions for the "Confirm Ingestion" step.

    Raises:
        HTTPException: 400 for unsupported file types, 422 for parsing failures.
    """
    file_bytes = await file.read()
    filename = file.filename.lower()

    if filename.endswith(".csv"):
        df = _parse_csv(file_bytes)
    elif filename.endswith(".xlsx"):
        df = _parse_xlsx(file_bytes)
    elif filename.endswith(".pdf"):
        df = _parse_pdf(file_bytes)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use CSV, XLSX, or PDF.")

    return _normalize(df)


@router_imports.post("/confirm", status_code=201, summary="Confirm ingestion of parsed transactions", description="Saves confirmed transactions into Expenses (negative amount) or Income (positive amount).")
def confirm_ingestion(payload: ConfirmIngestionInput, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Save confirmed parsed transactions into Expenses or Income based on amount sign.

    Args:
        payload (ConfirmIngestionInput): The list of transactions the user confirmed.
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Returns:
        dict: Counts of expenses and income rows created.
    """
    user_id = current_user["user_id"]
    expense_count = income_count = 0

    for tx in payload.transactions:
        if tx.amount < 0:
            db.add(Expenses(user_id=user_id, title=tx.title, category=tx.category,
                             description=tx.description, date=tx.date, amount=abs(tx.amount)))
            expense_count += 1
        else:
            db.add(Income(user_id=user_id, title=tx.title, received_from=tx.category,
                           description=tx.description, date=tx.date, amount=tx.amount))
            income_count += 1

    db.commit()
    return {"message": "Ingestion complete", "expenses_created": expense_count, "income_created": income_count}