"""
Admin router — read-only account oversight. Explicitly does NOT access
other users' financial data (expenses, incomes, goals, etc.) — account
metadata only, to stay consistent with the proposal's individual-use-only model.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
from JWT_Authentication.auth import get_current_admin
from sql_Alchemy_db_model.user_models import Users
from sql_Alchemy_db_model.expense_models import Expenses
from sql_Alchemy_db_model.income_model import Income

router_admin = APIRouter()


@router_admin.get(
    "/users",
    summary="List all registered users (admin only)",
    description="Returns username, email, and registration date for every user. Does not expose passwords or financial data.",
)
def list_users(
    current_user: dict = Depends(get_current_admin), db: Session = Depends(get_db)
):
    """
    List all registered users with basic account metadata.

    Args:
        current_user (dict): The authenticated admin user (enforced by get_current_admin).
        db (Session): The database session.

    Returns:
        list: List of dicts with 'id', 'username', 'email', and 'created_at' for every user.
    """
    users = db.query(Users).order_by(Users.created_at.desc()).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "created_at": u.created_at,
        }
        for u in users
    ]


@router_admin.get(
    "/users/activity-counts",
    summary="Per-user record counts (admin only)",
    description="Returns how many expense and income records each user has, for account-health monitoring. Does not expose amounts, titles, or categories.",
)
def get_user_activity_counts(
    current_user: dict = Depends(get_current_admin), db: Session = Depends(get_db)
):
    """
    Return per-user counts of expense and income records, without exposing the underlying financial details.

    Args:
        current_user (dict): The authenticated admin user (enforced by get_current_admin).
        db (Session): The database session.

    Returns:
        list: List of dicts with 'user_id', 'username', 'expense_count', and 'income_count'.
    """
    expense_counts = dict(
        db.query(Expenses.user_id, func.count(Expenses.id))
        .group_by(Expenses.user_id)
        .all()
    )
    income_counts = dict(
        db.query(Income.user_id, func.count(Income.id)).group_by(Income.user_id).all()
    )

    users = db.query(Users).all()
    return [
        {
            "user_id": u.id,
            "username": u.username,
            "expense_count": expense_counts.get(u.id, 0),
            "income_count": income_counts.get(u.id, 0),
        }
        for u in users
    ]
