"""
Incomes router — handles all income-related routes for Mero Kharcha.
"""

from fastapi import HTTPException
from datetime import date
from pydantic import BaseModel, Field
from database import get_db
from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends
from JWT_Authentication.auth import get_current_user
from sql_Alchemy_db_model.income_model import Income

router_income = APIRouter()


class IncomeInput(BaseModel):
    title: str
    amount: float = Field(..., gt=0, description="Amount must be greater than zero.")
    description: str
    received_from: str
    date: date


@router_income.post(
    "/",
    status_code=201,
    summary="Creates new income entry",
    description="Creates new income entry and return dictionary and status code: 201",
)
def create_income(
    income: IncomeInput,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new income entry for the system. Take data as: title: str, amount: float, description: str, received_from: str, date: date

    Args:
        income(IncomeInput): body where data is sent
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Return:
        Incomes: the newly created income record.
    """
    user_id = current_user["user_id"]
    add_income = Income(
        user_id=user_id,
        title=income.title,
        amount=income.amount,
        description=income.description,
        received_from=income.received_from,
        date=income.date,
    )
    db.add(add_income)
    db.commit()
    db.refresh(add_income)
    return add_income


@router_income.get("/{income_id}")
def get_income_id(
    income_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get income details based on income id.
    Args:
        income_id (int): income id of the existing income.
        current_user (dict): The current authenticated user.
        db (Session): The database session.
    Returns:
         Incomes: the existing income record.
    """
    income_data = (
        db.query(Income)
        .filter(Income.id == income_id, Income.user_id == current_user["user_id"])
        .first()
    )

    if income_data is None:
        raise HTTPException(status_code=404, detail=f"{income_id} not found")
    return income_data


@router_income.get(
    "/",
    summary="Return list of incomes rows matching the given filters",
    description="Returns all incomes, optionally filtered by income id and/or received_from",
)
def get_income_Query(
    received_from: str | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Returns all incomes, optionally filtered by income_id and/or received_from (case-insensitive).

    Args:
        received_from (str | None): received_from name to filter by, if provided.
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Returns:
        list: List of incomes rows matching the given filters.
    """
    income_query = (
        db.query(Income)
        .filter(Income.user_id == current_user["user_id"])
        .order_by(Income.date.desc())
    )
    if received_from:
        income_query = income_query.filter(Income.received_from.ilike(received_from))
    return income_query.all()


@router_income.put(
    "/put/{income_id}",
    summary="Update an existing income",
    description="Updates all fields of an income by ID. Returns 404 if the ID doesn't exist.",
)
def update_income(
    income: IncomeInput,
    income_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update income row in the database.

    Args:
        income (IncomeInput): The income data payload.
        income_id (int) : id of incomes.
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Raises:
        404 : Income id not found

    Returns:
        Updated data of the income
    """

    income_data = (
        db.query(Income)
        .filter(Income.id == income_id, Income.user_id == current_user["user_id"])
        .first()
    )
    if not income_data:
        raise HTTPException(status_code=404, detail=f"Income id {income_id} not found.")

    updating_data = income.model_dump()

    for key, value in updating_data.items():
        setattr(income_data, key, value)

    db.commit()
    db.refresh(income_data)
    return income_data


@router_income.delete(
    "/dlt/{income_id}",
    summary="Delete an income",
    description="Deletes an income by ID. Returns 404 if the ID doesn't exist.",
)
def delete_income(
    income_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete income entry in the database.

    Args:
        income_id (int) : id of income.
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Raises:
        404 : income id not found

    Returns:
        message: income id is deleted successfully.
    """
    income_value = (
        db.query(Income)
        .filter(Income.id == income_id, Income.user_id == current_user["user_id"])
        .first()
    )
    if not income_value:
        raise HTTPException(status_code=404, detail=f"Income id {income_id} not found.")
    db.delete(income_value)
    db.commit()
    return {"message": f"Income id {income_id} is deleted successfully."}
