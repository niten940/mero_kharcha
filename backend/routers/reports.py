from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
from JWT_Authentication.auth import get_current_user
from sqlAlchemy.expense_models import Expenses

router_reports = APIRouter()


@router_reports.get(
    "/monthly",
    summary="Monthly expense summary",
    description="Returns total expense per month for the authenticated user.",
)
def get_monthly_report(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Return total expenses grouped by month for the authenticated user.

    Args:
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Returns:
        list: List of dicts, each with 'month' (date) and 'total' (float), ordered oldest to newest.
    """
    month_col = func.to_char(
        func.date_trunc("month", Expenses.date), "YYYY-MM-DD"
    ).label("month")
    total_col = func.sum(Expenses.amount).label("total")

    results = (
        db.query(month_col, total_col)
        .filter(Expenses.user_id == current_user["user_id"])
        .group_by(month_col)
        .order_by(month_col)
        .all()
    )

    return [
        {"month": row.month, "total": round(float(row.total), 2)} for row in results
    ]


@router_reports.get(
    "/category",
    summary="Category wise expense summary",
    description="Returns total expense per category for the authenticated user.",
)
def get_category_wise_report(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Return total expenses grouped by category for the authenticated user.

    Args:
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Returns:
        list: List of dicts, each with 'category' (str) and 'total' (float), ordered by total amount in descending order.
    """
    category_col = Expenses.category.label("category")
    total_col = func.sum(Expenses.amount).label("total")

    results = (
        db.query(category_col, total_col)
        .filter(Expenses.user_id == current_user["user_id"])
        .group_by(category_col)
        .order_by(total_col.desc())
        .all()
    )

    return [
        {"category": row.category, "total": round(float(row.total), 2)}
        for row in results
    ]
