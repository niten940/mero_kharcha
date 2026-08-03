"""
Bikram Sambat calendar support — AD (Gregorian) to BS conversion and vice versa.
"""

from datetime import date
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
import nepali_datetime
from JWT_Authentication.auth import get_current_user

router_calendar_bs = APIRouter()


class ADToBSInput(BaseModel):
    ad_date: date


class BSToADInput(BaseModel):
    bs_year: int
    bs_month: int
    bs_day: int


@router_calendar_bs.post(
    "/ad-to-bs",
    summary="Convert an AD (Gregorian) date to Bikram Sambat",
    description="Converts a standard Gregorian calendar date into the corresponding Bikram Sambat date.",
)
def convert_ad_to_bs(
    payload: ADToBSInput, current_user: dict = Depends(get_current_user)
):
    """
    Convert an AD date to its Bikram Sambat equivalent.

    Args:
        payload (ADToBSInput): The Gregorian date to convert.
        current_user (dict): The current authenticated user.

    Raises:
        HTTPException: 400 if the date falls outside the supported BS conversion range.

    Returns:
        dict: 'bs_year', 'bs_month', 'bs_day', and 'bs_label' (formatted string).
    """
    try:
        bs_date = nepali_datetime.date.from_datetime_date(payload.ad_date)
    except (ValueError, OverflowError):
        raise HTTPException(
            status_code=400, detail="Date is outside the supported BS conversion range."
        )

    return {
        "bs_year": bs_date.year,
        "bs_month": bs_date.month,
        "bs_day": bs_date.day,
        "bs_label": bs_date.strftime("%Y-%m-%d"),
    }


@router_calendar_bs.post(
    "/bs-to-ad",
    summary="Convert a Bikram Sambat date to AD (Gregorian)",
    description="Converts a Bikram Sambat date into the corresponding standard Gregorian calendar date.",
)
def convert_bs_to_ad(
    payload: BSToADInput, current_user: dict = Depends(get_current_user)
):
    """
    Convert a Bikram Sambat date to its AD equivalent.

    Args:
        payload (BSToADInput): The BS year, month, and day to convert.
        current_user (dict): The current authenticated user.

    Raises:
        HTTPException: 400 if the given BS date is invalid or out of supported range.

    Returns:
        dict: 'ad_date' as an ISO-formatted date string.
    """
    try:
        bs_date = nepali_datetime.date(
            payload.bs_year, payload.bs_month, payload.bs_day
        )
        ad_date = bs_date.to_datetime_date()
    except (ValueError, OverflowError):
        raise HTTPException(
            status_code=400, detail="Invalid or unsupported Bikram Sambat date."
        )

    return {"ad_date": ad_date.isoformat()}


@router_calendar_bs.get(
    "/today",
    summary="Get today's date in both AD and BS",
    description="Returns the current date in both Gregorian and Bikram Sambat formats.",
)
def get_today_dual_calendar(current_user: dict = Depends(get_current_user)):
    """
    Return today's date in both AD and BS formats.

    Args:
        current_user (dict): The current authenticated user.

    Returns:
        dict: 'ad_date' (ISO string) and 'bs_date' (dict with year/month/day/label).
    """
    today_ad = date.today()
    today_bs = nepali_datetime.date.from_datetime_date(today_ad)

    return {
        "ad_date": today_ad.isoformat(),
        "bs_date": {
            "year": today_bs.year,
            "month": today_bs.month,
            "day": today_bs.day,
            "label": today_bs.strftime("%Y-%m-%d"),
        },
    }
