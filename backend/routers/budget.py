from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
from JWT_Authentication.auth import get_current_user
from sqlAlchemy.budget_model import Budget
from sqlAlchemy.expense_models import Expenses

router_budget = APIRouter()

class BudgetInput(BaseModel):
    monthly_limit: float

@router_budget.post("/", status_code=201, summary="Set monthly budget limit", description="Creates the user's monthly budget limit. Fails if one already exists — use PUT to update.")
def create_budget(budget: BudgetInput, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Create the authenticated user's monthly budget limit.

    Args:
        budget (BudgetInput): The monthly limit payload.
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Raises:
        HTTPException: 400 if a budget already exists for this user.

    Returns:
        Budget: The newly created budget record.
    """
    existing = db.query(Budget).filter(Budget.user_id == current_user["user_id"]).first()
    if existing:
        raise HTTPException(status_code=400, detail="Budget already exists. Use PUT to update it.")

    new_budget = Budget(user_id=current_user["user_id"], monthly_limit=budget.monthly_limit)
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    return new_budget

@router_budget.get("/", summary="Get the current monthly budget limit", description="Returns the authenticated user's monthly budget limit.")
def get_budget(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Fetch the authenticated user's monthly budget limit.

    Args:
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Raises:
        HTTPException: 404 if no budget has been set yet.

    Returns:
        Budget: The user's budget record.
    """
    budget = db.query(Budget).filter(Budget.user_id == current_user["user_id"]).first()
    if not budget:
        raise HTTPException(status_code=404, detail="No budget set yet.")
    return budget

@router_budget.put("/", summary="Update the monthly budget limit", description="Updates the authenticated user's monthly budget limit. Returns 404 if none exists yet.")
def update_budget(budget: BudgetInput, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Update the authenticated user's monthly budget limit.

    Args:
        budget (BudgetInput): The new monthly limit payload.
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Raises:
        HTTPException: 404 if no budget exists yet for this user.

    Returns:
        Budget: The updated budget record.
    """
    existing = db.query(Budget).filter(Budget.user_id == current_user["user_id"]).first()
    if not existing:
        raise HTTPException(status_code=404, detail="No budget set yet. Use POST to create one.")

    existing.monthly_limit = budget.monthly_limit
    db.commit()
    db.refresh(existing)
    return existing

@router_budget.get("/watchdog", summary="Budget watchdog status", description="Returns current-month total spending against the monthly limit, for the dashboard's Spending Velocity card.")
def get_budget_watchdog(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Calculate current-month spending against the user's monthly budget limit.

    Args:
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Raises:
        HTTPException: 404 if no budget has been set yet.

    Returns:
        dict: monthly_limit, total_spent, spending_percent, remaining, over_budget.
    """
    budget = db.query(Budget).filter(Budget.user_id == current_user["user_id"]).first()
    if not budget:
        raise HTTPException(status_code=404, detail="No budget set yet.")

    month_start = date.today().replace(day=1)

    total_spent = round(float(
        db.query(func.sum(Expenses.amount))
        .filter(Expenses.user_id == current_user["user_id"], Expenses.date >= month_start)
        .scalar() or 0
    ), 2)

    monthly_limit = float(budget.monthly_limit)
    spending_percent = round((total_spent / monthly_limit) * 100, 2) if monthly_limit > 0 else 0
    remaining = round(monthly_limit - total_spent, 2)
    over_budget = total_spent > monthly_limit

    return {
        "monthly_limit": monthly_limit,
        "total_spent": total_spent,
        "spending_percent": spending_percent,
        "remaining": remaining,
        "over_budget": over_budget,
    }