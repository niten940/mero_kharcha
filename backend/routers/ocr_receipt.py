"""
OCR receipt scanning — two backends:
  - /ocr/scan: pytesseract (offline, good for printed text)
  - /ocr/scan-ai: Gemini vision (online, handles handwritten Devanagari and PDFs)
"""

import io
import re
import os
from datetime import date, datetime
import pytesseract
from PIL import Image
import google.generativeai as genai
import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from JWT_Authentication.auth import get_current_user
from category_rules import suggest_category
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

router_ocr = APIRouter()

AMOUNT_PATTERN = re.compile(r"(?:rs\.?|npr)?\s*([\d,]+\.\d{2})", re.IGNORECASE)
DATE_PATTERNS = [
    (re.compile(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})"), "%Y-%m-%d"),
    (re.compile(r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})"), "%d-%m-%Y"),
]


def _extract_amount(text: str) -> float | None:
    """
    Find the largest currency-formatted number in the OCR text, assumed to be the total.

    Args:
        text (str): Raw OCR-extracted text from the receipt.

    Returns:
        float | None: The largest matched amount, or None if no amount pattern matched.
    """
    matches = AMOUNT_PATTERN.findall(text)
    if not matches:
        return None
    amounts = [float(m.replace(",", "")) for m in matches]
    return max(amounts)


def _extract_date(text: str) -> date | None:
    """
    Find the first recognizable date in the OCR text.

    Args:
        text (str): Raw OCR-extracted text from the receipt.

    Returns:
        date | None: The parsed date, or None if no date pattern matched.
    """
    for pattern, _fmt in DATE_PATTERNS:
        match = pattern.search(text)
        if match:
            try:
                y, m, d = (
                    match.groups() if len(match.group(1)) == 4 else match.groups()[::-1]
                )
                return date(int(y), int(m), int(d))
            except ValueError:
                continue
    return None


def _extract_title(text: str) -> str:
    """
    Use the first non-empty line of OCR text as the merchant/title guess.

    Args:
        text (str): Raw OCR-extracted text from the receipt.

    Returns:
        str: The first non-empty line, or a fallback label if the text is empty.
    """
    for line in text.splitlines():
        cleaned = line.strip()
        if cleaned:
            return cleaned[:100]
    return "Unlabeled Receipt"


@router_ocr.post(
    "/scan",
    summary="Extract transaction details from a receipt using Tesseract OCR",
    description=(
        "Runs offline OCR on an uploaded receipt image. Works well for printed text. "
        "For handwritten Devanagari or PDFs, use /ocr/scan-ai instead."
    ),
)
async def scan_receipt(
    file: UploadFile = File(...), current_user: dict = Depends(get_current_user)
):
    """
    Extract transaction fields from a receipt image using pytesseract.

    Args:
        file (UploadFile): The uploaded receipt image (JPG/PNG).
        current_user (dict): The current authenticated user.

    Raises:
        HTTPException: 400 for unsupported file types, 422 if OCR yields no readable text.

    Returns:
        dict: Best-guess title, amount, date, suggested_category, and raw OCR text.
    """
    filename = file.filename.lower()
    if not filename.endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(
            status_code=400, detail="Unsupported file type. Use JPG or PNG."
        )

    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))
    raw_text = pytesseract.image_to_string(image)

    if not raw_text.strip():
        raise HTTPException(
            status_code=422,
            detail="Could not read any text from this image. Try a clearer photo.",
        )

    title = _extract_title(raw_text)
    amount = _extract_amount(raw_text)
    parsed_date = _extract_date(raw_text)

    return {
        "title": title,
        "amount": amount,
        "date": parsed_date.isoformat() if parsed_date else None,
        "suggested_category": suggest_category(title),
        "raw_text": raw_text,
    }


@router_ocr.post(
    "/scan-ai",
    summary="Extract transaction details from a receipt using Gemini AI",
    description=(
        "Sends the uploaded receipt image or PDF to Gemini vision for intelligent extraction. "
        "Handles handwritten Devanagari, mixed scripts, and PDFs. Requires internet. "
        "User must review extracted fields before confirming — AI output is not auto-saved."
        "Upload one receipt at a time — one file per request."
    ),
)
async def scan_receipt_ai(
    file: UploadFile = File(...), current_user: dict = Depends(get_current_user)
):
    """
    Extract transaction fields from a receipt using Gemini vision AI.

    Accepts JPG, PNG, or PDF. Returns structured fields extracted by the model —
    title (business name + key items), amount (from total line), date (from receipt
    or today if not found), suggested_category, and an AI-generated description.

    Args:
        file (UploadFile): The uploaded receipt image (JPG/PNG) or PDF.
        current_user (dict): The current authenticated user.

    Raises:
        HTTPException: 400 for unsupported file types.
        HTTPException: 422 if Gemini returns unparseable output.
        HTTPException: 503 if the Gemini API is unreachable.

    Returns:
        dict: title, amount (float or null), date (ISO string), 
              suggested_category, description.
    """
    filename = file.filename.lower()

    if filename.endswith((".jpg", ".jpeg", ".png")):
        mime_type = "image/jpeg" if not filename.endswith(".png") else "image/png"
    elif filename.endswith(".pdf"):
        mime_type = "application/pdf"
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Use JPG, PNG, or PDF.",
        )

    file_bytes = await file.read()

    prompt = """
You are a receipt data extraction assistant for a personal finance app used in Nepal.

Analyze this receipt and extract the following fields. Respond ONLY with a valid JSON object — no markdown, no explanation, no extra text.

Fields to extract:
- "title": Business name combined with the main item(s) or service(s). Example: "New Namo Buddha Tent & Catering — Stage, Sound, Screen". Keep it under 120 characters.
- "amount": The final total amount as a number (float). Look for labels like "Total", "Grand Total", "जम्मा", "कुल". If you cannot find a clear total, return null.
- "date": The transaction date in YYYY-MM-DD format. If no date is found on the receipt, return null.
- "description": A one or two sentence natural language summary of what this receipt is for, written as if explaining the expense to someone.

Return exactly this JSON shape:
{
  "title": "...",
  "amount": 0.00,
  "date": "YYYY-MM-DD",
  "description": "..."
}
"""

    try:
        model = genai.GenerativeModel("gemini-3.5-flash")
        response = model.generate_content([
            {"mime_type": mime_type, "data": file_bytes},
            prompt,
        ])

        raw = response.text.strip()
        # Strip markdown fences if Gemini wraps output despite instructions.
        if raw.startswith("```"):
            raw = re.sub(r"^```[a-z]*\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)

        extracted = json.loads(raw)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=422,
            detail="Gemini returned an unreadable response. Please try again.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Gemini API error: {str(e)}",
        )

    # Resolve date — use receipt date if found, fall back to today.
    receipt_date = extracted.get("date")
    if receipt_date:
        try:
            datetime.strptime(receipt_date, "%Y-%m-%d")
        except ValueError:
            receipt_date = date.today().isoformat()
    else:
        receipt_date = date.today().isoformat()

    title = extracted.get("title") or "Unlabeled Receipt"
    amount_raw = extracted.get("amount")
    amount = round(float(amount_raw), 2) if amount_raw is not None else None

    return {
        "title": title,
        "amount": amount,
        "date": receipt_date,
        "suggested_category": suggest_category(title),
        "description": extracted.get("description") or "",
    }