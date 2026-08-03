"""
Behavior router — month-over-month comparisons, spending distribution,
highest-spending category, and multi-period trend analysis.
"""

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
from JWT_Authentication.auth import get_current_user
from sql_Alchemy_db_model.expense_models import Expenses

router_behavior = APIRouter()


def _month_bounds(target: date) -> tuple[date, date]:
    """
    Return the first day of target's month and the first day of the following month.

    Args:
        target (date): Any date within the month of interest.

    Returns:
        tuple[date, date]: (month_start, next_month_start).
    """
    month_start = target.replace(day=1)
    next_month_start = month_start + relativedelta(months=1)
    return month_start, next_month_start


@router_behavior.get(
    "/month-over-month",
    summary="Compare current month vs previous month by category",
    description="Returns per-category totals for the current and previous month, with percent change, for the authenticated user.",
)
def get_month_over_month(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Compare current-month and previous-month spending, grouped by category.

    Args:
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Returns:
        list: List of dicts with 'category', 'current_month_total', 'previous_month_total', and 'percent_change'.
    """
    user_id = current_user["user_id"]
    today = date.today()
    curr_start, curr_end = _month_bounds(today)
    prev_start, prev_end = _month_bounds(curr_start - timedelta(days=1))

    def _category_totals(start: date, end: date) -> dict:
        rows = (
            db.query(Expenses.category, func.sum(Expenses.amount))
            .filter(
                Expenses.user_id == user_id,
                Expenses.date >= start,
                Expenses.date < end,
            )
            .group_by(Expenses.category)
            .all()
        )
        return {row[0]: round(float(row[1]), 2) for row in rows}

    current_totals = _category_totals(curr_start, curr_end)
    previous_totals = _category_totals(prev_start, prev_end)

    all_categories = set(current_totals) | set(previous_totals)
    result = []
    for category in all_categories:
        curr = current_totals.get(category, 0)
        prev = previous_totals.get(category, 0)
        if prev > 0:
            percent_change = round(((curr - prev) / prev) * 100, 2)
        elif curr > 0:
            percent_change = 100.0  # new category this month, no prior baseline
        else:
            percent_change = 0.0

        result.append(
            {
                "category": category,
                "current_month_total": curr,
                "previous_month_total": prev,
                "percent_change": percent_change,
            }
        )

    return sorted(result, key=lambda r: r["current_month_total"], reverse=True)


@router_behavior.get(
    "/distribution",
    summary="Spending distribution by category for the current month",
    description="Returns each category's share of total spending as a percentage, for the current month.",
)
def get_spending_distribution(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Calculate what percentage of current-month spending each category represents.

    Args:
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Returns:
        list: List of dicts with 'category', 'total', and 'percent_of_total', ordered by total descending.
    """
    user_id = current_user["user_id"]
    month_start, month_end = _month_bounds(date.today())

    rows = (
        db.query(Expenses.category, func.sum(Expenses.amount))
        .filter(
            Expenses.user_id == user_id,
            Expenses.date >= month_start,
            Expenses.date < month_end,
        )
        .group_by(Expenses.category)
        .order_by(func.sum(Expenses.amount).desc())
        .all()
    )

    grand_total = sum(float(row[1]) for row in rows)

    return [
        {
            "category": row[0],
            "total": round(float(row[1]), 2),
            "percent_of_total": (
                round((float(row[1]) / grand_total) * 100, 2) if grand_total > 0 else 0
            ),
        }
        for row in rows
    ]


@router_behavior.get(
    "/highest-category",
    summary="Highest-spending category for the current month",
    description="Returns the single category with the highest total spending for the current month.",
)
def get_highest_spending_category(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Find the category with the highest total spending in the current month.

    Args:
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Returns:
        dict: 'category' and 'total', or a message if no expenses exist this month.
    """
    user_id = current_user["user_id"]
    month_start, month_end = _month_bounds(date.today())

    top = (
        db.query(Expenses.category, func.sum(Expenses.amount).label("total"))
        .filter(
            Expenses.user_id == user_id,
            Expenses.date >= month_start,
            Expenses.date < month_end,
        )
        .group_by(Expenses.category)
        .order_by(func.sum(Expenses.amount).desc())
        .first()
    )

    if not top:
        return {"message": "No expenses recorded this month."}

    return {"category": top[0], "total": round(float(top[1]), 2)}


@router_behavior.get(
    "/trend",
    summary="Spending trend over time",
    description="Returns total spending grouped by week, month, or year, for the authenticated user. Use the 'period' query parameter: weekly, monthly, or yearly.",
)
def get_spending_trend(
    period: str = Query("monthly", pattern="^(weekly|monthly|yearly)$"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return total spending grouped by the requested time period.

    Args:
        period (str): One of 'weekly', 'monthly', or 'yearly'. Defaults to 'monthly'.
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Returns:
        list: List of dicts with 'period' (label) and 'total', ordered oldest to newest.
    """
    user_id = current_user["user_id"]

    trunc_unit = {"weekly": "week", "monthly": "month", "yearly": "year"}[period]

    period_col = func.date_trunc(trunc_unit, Expenses.date).label("period")
    total_col = func.sum(Expenses.amount).label("total")

    results = (
        db.query(period_col, total_col)
        .filter(Expenses.user_id == user_id)
        .group_by(period_col)
        .order_by(period_col)
        .all()
    )

    return [
        {"period": row.period.date().isoformat(), "total": round(float(row.total), 2)}
        for row in results
    ]
