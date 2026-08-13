"""
Financial Health Score — combines five weighted components into a single
0-100 score. Weights follow the design confirmed for the capstone defense:

    Savings Rate         25%
    Budget Adherence     20%
    Goal Progress        20%
    Expense Consistency  20%
    Income Stability     15%

Each component returns None (and is excluded, with the remaining weights
renormalized to 100%) when there isn't enough data yet to calculate it —
e.g. a brand-new account with no budget set, no goals, or fewer than two
months of expense/income history.
"""

import statistics
from datetime import date
from dateutil.relativedelta import relativedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from JWT_Authentication.auth import get_current_user
from sql_Alchemy_db_model.expense_models import Expenses
from sql_Alchemy_db_model.income_model import Income
from sql_Alchemy_db_model.budget_model import Budget
from sql_Alchemy_db_model.goals_model import Goals

router_financial_health = APIRouter()

WEIGHTS = {
    "savings_rate": 0.25,
    "budget_adherence": 0.20,
    "goal_progress": 0.20,
    "expense_consistency": 0.20,
    "income_stability": 0.15,
}

SAVINGS_LOOKBACK_MONTHS = 3
CONSISTENCY_MONTHS = 6


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    """
    Restrict a float value to the range [low, high].

    Args:
        value (float): The value to clamp.
        low (float): Lower bound, default 0.0.
        high (float): Upper bound, default 100.0.

    Returns:
        float: Clamped value.
    """
    return max(low, min(high, value))


def _monthly_totals(
    db: Session, user_id: int, model, months: int
) -> list[float]:
    """
    Sum of model.amount grouped by calendar month for the last N months,
    ordered oldest to newest. Uses exact month boundaries via relativedelta.

    Args:
        db (Session): The database session.
        user_id (int): The authenticated user's ID.
        model: SQLAlchemy model — Expenses or Income.
        months (int): How many months back to include.

    Returns:
        list[float]: One total per month that has at least one row.
            Months with no activity are omitted, not zero-filled.
    """
    cutoff = date.today().replace(day=1) - relativedelta(months=months)
    month_col = func.date_trunc("month", model.date).label("month")
    total_col = func.sum(model.amount).label("total")

    rows = (
        db.query(month_col, total_col)
        .filter(model.user_id == user_id, model.date >= cutoff)
        .group_by(month_col)
        .order_by(month_col)
        .all()
    )
    return [float(row.total) for row in rows]


def _score_savings_rate(db: Session, user_id: int) -> dict:
    """
    Score based on savings rate over the trailing 3 months.
    Saving 20%+ of income scores 100. Zero or negative savings scores 0.
    Scales linearly between 0 and 20%.

    Args:
        db (Session): The database session.
        user_id (int): The authenticated user's ID.

    Returns:
        dict: 'score' (float or None) and supporting breakdown figures.
    """
    since = date.today().replace(day=1) - relativedelta(months=SAVINGS_LOOKBACK_MONTHS)

    total_income = float(
        db.query(func.sum(Income.amount))
        .filter(Income.user_id == user_id, Income.date >= since)
        .scalar()
        or 0
    )
    total_expenses = float(
        db.query(func.sum(Expenses.amount))
        .filter(Expenses.user_id == user_id, Expenses.date >= since)
        .scalar()
        or 0
    )

    if total_income <= 0:
        return {
            "score": None,
            "reason": "No income recorded in the last 3 months.",
        }

    savings_rate = (total_income - total_expenses) / total_income
    score = _clamp((savings_rate / 0.20) * 100)
    return {
        "score": round(score, 2),
        "savings_rate_percent": round(savings_rate * 100, 2),
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
    }


def _score_budget_adherence(db: Session, user_id: int) -> dict:
    """
    Score based on current month's spending vs the monthly budget limit.
    Within budget = 100. Loses 2 points per 1% over the limit.
    50% over budget = 0.

    Args:
        db (Session): The database session.
        user_id (int): The authenticated user's ID.

    Returns:
        dict: 'score' (float or None) and supporting breakdown figures.
    """
    budget = db.query(Budget).filter(Budget.user_id == user_id).first()
    if not budget:
        return {"score": None, "reason": "No monthly budget set yet."}

    monthly_limit = float(budget.monthly_limit)
    if monthly_limit <= 0:
        return {"score": None, "reason": "Monthly budget limit is zero."}

    month_start = date.today().replace(day=1)
    total_spent = float(
        db.query(func.sum(Expenses.amount))
        .filter(Expenses.user_id == user_id, Expenses.date >= month_start)
        .scalar()
        or 0
    )

    spending_percent = (total_spent / monthly_limit) * 100
    overage = max(0.0, spending_percent - 100)
    score = _clamp(100 - overage * 2)
    return {
        "score": round(score, 2),
        "spending_percent": round(spending_percent, 2),
        "total_spent": round(total_spent, 2),
        "monthly_limit": monthly_limit,
    }


def _score_goal_progress(db: Session, user_id: int) -> dict:
    """
    Average progress across all goals, each capped at 100%.

    Args:
        db (Session): The database session.
        user_id (int): The authenticated user's ID.

    Returns:
        dict: 'score' (float or None) and supporting breakdown figures.
    """
    goals = db.query(Goals).filter(Goals.user_id == user_id).all()
    if not goals:
        return {"score": None, "reason": "No goals set yet."}

    progresses = [
        min(100.0, (float(g.current_amount) / float(g.goal_amount)) * 100)
        for g in goals
        if float(g.goal_amount) > 0
    ]
    if not progresses:
        return {"score": None, "reason": "No goals with a valid target amount."}

    score = _clamp(statistics.mean(progresses))
    return {
        "score": round(score, 2),
        "goal_count": len(goals),
        "average_progress_percent": round(score, 2),
    }


def _score_consistency(monthly_totals: list[float], label: str) -> dict:
    """
    Score month-to-month consistency using coefficient of variation (CV).
    CV of 0 (identical every month) = 100. CV >= 1.0 = 0.

    Args:
        monthly_totals (list[float]): Monthly totals from _monthly_totals().
        label (str): Human-readable label for the reason message
            (e.g. 'expense' or 'income').

    Returns:
        dict: 'score' (float or None) and supporting breakdown figures.
    """
    if len(monthly_totals) < 2:
        return {
            "score": None,
            "reason": f"Need at least 2 months of {label} history.",
        }

    mean = statistics.mean(monthly_totals)
    if mean == 0:
        return {"score": None, "reason": f"All {label} totals are zero."}

    stdev = statistics.stdev(monthly_totals)
    cv = stdev / mean
    score = _clamp(100 - cv * 100)
    return {
        "score": round(score, 2),
        "months_used": len(monthly_totals),
        "coefficient_of_variation": round(cv, 3),
    }


@router_financial_health.get(
    "/score",
    summary="Financial Health Score",
    description=(
        "Combines Savings Rate (25%), Budget Adherence (20%), Goal Progress (20%), "
        "Expense Consistency (20%), and Income Stability (15%) into a single 0–100 score. "
        "Components with insufficient data are excluded and remaining weights are "
        "renormalized to sum to 100%."
    ),
)
def get_financial_health_score(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Calculate the authenticated user's overall financial health score.

    Args:
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Returns:
        dict: 'total_score' (float or None), 'components' (per-component
            breakdown with score and supporting figures), and 'weights_applied'
            (renormalized weights actually used, keyed by component name).
    """
    user_id = current_user["user_id"]

    expense_totals = _monthly_totals(db, user_id, Expenses, CONSISTENCY_MONTHS)
    income_totals = _monthly_totals(db, user_id, Income, CONSISTENCY_MONTHS)

    components = {
        "savings_rate": _score_savings_rate(db, user_id),
        "budget_adherence": _score_budget_adherence(db, user_id),
        "goal_progress": _score_goal_progress(db, user_id),
        "expense_consistency": _score_consistency(expense_totals, "expense"),
        "income_stability": _score_consistency(income_totals, "income"),
    }

    available = {k: v for k, v in components.items() if v["score"] is not None}
    if not available:
        return {
            "total_score": None,
            "message": "Not enough data yet to calculate a financial health score.",
            "components": components,
            "weights_applied": {},
        }

    weight_sum = sum(WEIGHTS[k] for k in available)
    total_score = sum(WEIGHTS[k] * available[k]["score"] for k in available) / weight_sum
    weights_applied = {k: round(WEIGHTS[k] / weight_sum, 4) for k in available}

    return {
        "total_score": round(total_score, 2),
        "components": components,
        "weights_applied": weights_applied,
    }