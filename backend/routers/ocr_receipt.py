"""
OCR receipt scanning — extracts title/amount/date from a photographed receipt
image, then feeds the result through the same normalization pattern as imports.py.
Accuracy depends heavily on receipt layout/print quality — demo on clean samples.
"""

import io
import re
from datetime import date, datetime
import pytesseract
from PIL import Image
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from JWT_Authentication.auth import get_current_user
from category_rules import suggest_category

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
    summary="Extract transaction details from a photographed receipt",
    description="Runs OCR on an uploaded receipt image and extracts a best-guess title, amount, date, and suggested category. Accuracy varies by receipt layout — user should review before confirming.",
)
async def scan_receipt(
    file: UploadFile = File(...), current_user: dict = Depends(get_current_user)
):
    """
    Extract transaction fields from a photographed receipt using OCR.

    Args:
        file (UploadFile): The uploaded receipt image (jpg/png).
        current_user (dict): The current authenticated user.

    Raises:
        HTTPException: 400 for unsupported file types, 422 if OCR yields no readable text.

    Returns:
        dict: Best-guess 'title', 'amount', 'date', 'suggested_category', and the raw OCR text for user review.
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
