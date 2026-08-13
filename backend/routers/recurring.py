from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from pydantic import BaseModel, Field
from database import get_db
from sqlalchemy.orm.session import Session
from JWT_Authentication.auth import get_current_user
from sql_Alchemy_db_model.recurring_model import (
    RecurringTransaction,
    TransactionType,
    Frequency,
)
from dateutil.relativedelta import relativedelta
from sql_Alchemy_db_model.expense_models import Expenses
from sql_Alchemy_db_model.income_model import Income

router_recurring = APIRouter()


class RecurringInput(BaseModel):
    type: TransactionType
    title: str
    amount: float = Field(..., gt=0, description="Amount must be greater than zero.")
    category: str | None = None
    description: str
    frequency: Frequency
    next_due_date: date
    is_active: bool = True

def _advance_due_date(current_due: date, frequency: Frequency) -> date:
    """
    Calculate the next due date after firing, based on the recurrence frequency.

    Args:
        current_due (date): The due date that was just fired.
        frequency (Frequency): The recurrence frequency enum value.

    Returns:
        date: The next due date.
    """
    if frequency == Frequency.daily:
        return current_due + relativedelta(days=1)
    elif frequency == Frequency.weekly:
        return current_due + relativedelta(weeks=1)
    elif frequency == Frequency.monthly:
        return current_due + relativedelta(months=1)
    elif frequency == Frequency.yearly:
        return current_due + relativedelta(years=1)
    return current_due


@router_recurring.post(
    "/fire-due",
    summary="Fire all due recurring transactions",
    description="Finds active recurring transactions with next_due_date <= today for the authenticated user, creates the corresponding Expense/Income row for each, and advances next_due_date by the template's frequency.",
)
def fire_due_recurring_transactions(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Fire all due recurring transaction templates for the authenticated user.

    Args:
        current_user (dict): The current authenticated user payload containing the user_id.
        db (Session): The active SQLAlchemy database session dependency.

    Returns:
        dict: Counts of expenses and income rows created, plus the list of fired template IDs.
    """
    user_id = current_user["user_id"]
    today = date.today()

    due_templates = (
        db.query(RecurringTransaction)
        .filter(
            RecurringTransaction.user_id == user_id,
            RecurringTransaction.is_active == True,
            RecurringTransaction.next_due_date <= today,
        )
        .all()
    )

    expense_count = income_count = 0
    fired_ids = []

    for template in due_templates:
        # A template may be overdue by more than one cycle (e.g. app unused for 2 months),
        # so fire it repeatedly until next_due_date is in the future.
        while template.next_due_date <= today:
            if template.type == TransactionType.expense:
                db.add(
                    Expenses(
                        user_id=user_id,
                        title=template.title,
                        amount=template.amount,
                        category=template.category,
                        description=template.description,
                        date=template.next_due_date,
                    )
                )
                expense_count += 1
            else:
                db.add(
                    Income(
                        user_id=user_id,
                        title=template.title,
                        amount=template.amount,
                        received_from=template.category,
                        description=template.description,
                        date=template.next_due_date,
                    )
                )
                income_count += 1

            template.next_due_date = _advance_due_date(
                template.next_due_date, template.frequency
            )

        fired_ids.append(template.id)

    db.commit()
    return {
        "message": "Recurring transactions processed",
        "expenses_created": expense_count,
        "income_created": income_count,
        "templates_fired": fired_ids,
    }


@router_recurring.get(
    "/{recurring_id}",
    summary="Get a recurring transaction by ID",
    description="Fetches a specific recurring transaction entry belonging to the authenticated user.",
)
def get_recurring_transaction(
    recurring_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Fetch a single recurring transaction from the database by its unique identifier.

    Args:
        recurring_id (int): The unique ID of the recurring transaction record.
        current_user (dict): The current authenticated user payload containing the user_id.
        db (Session): The active SQLAlchemy database session dependency.

    Raises:
        HTTPException: 404 error if the recurring transaction record does not exist or does not belong to the user.

    Returns:
        RecurringTransaction: The matching database record containing the recurring transaction info.
    """
    recurring_details = (
        db.query(RecurringTransaction)
        .filter(
            RecurringTransaction.user_id == current_user["user_id"],
            RecurringTransaction.id == recurring_id,
        )
        .first()
    )

    if recurring_details is None:
        raise HTTPException(status_code=404, detail="Recurring transaction not found")

    return recurring_details


@router_recurring.get(
    "/",
    summary="Return list of Recurring Transactions of current user",
    description="Returns all recurring transactions matching the authenticated user session.",
)
def get_recurring_transactions_Query(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """
    Returns all recurring transactions for the current user.

    Args:
        current_user (dict): The current authenticated user payload containing the user_id.
        db (Session): The active SQLAlchemy database session dependency.

    Returns:
        list[RecurringTransaction]: List of recurring transactions belonging to the current user.
    """
    query = (
        db.query(RecurringTransaction)
        .filter(RecurringTransaction.user_id == current_user["user_id"])
        .order_by(RecurringTransaction.id.desc())
    )

    return query.all()


@router_recurring.post(
    "/post/",
    status_code=201,
    summary="Create a new recurring transaction",
    description="Creates a new recurring transaction entry associated with the logged-in user.",
)
def create_recurring_transaction(
    recurring: RecurringInput,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new recurring transaction entry in the database.

    Args:
        recurring (RecurringInput): The validated input data payload containing title, amount, type, and frequency.
        current_user (dict): The current authenticated user payload containing the user_id.
        db (Session): The active SQLAlchemy database session dependency.

    Returns:
        RecurringTransaction: The newly created RecurringTransaction record.
    """
    user_id = current_user["user_id"]

    add_recurring = RecurringTransaction(
        user_id=user_id,
        type=recurring.type,
        title=recurring.title,
        amount=recurring.amount,
        category=recurring.category,
        description=recurring.description,
        frequency=recurring.frequency,
        next_due_date=recurring.next_due_date,
    )
    db.add(add_recurring)
    db.commit()
    db.refresh(add_recurring)
    return add_recurring


@router_recurring.put(
    "/put/{recurring_id}",
    summary="Update an existing recurring transaction",
    description="Updates all fields of a specific recurring transaction by ID. Returns 404 if it doesn't exist.",
)
def update_recurring_transaction(
    recurring: RecurringInput,
    recurring_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an existing recurring transaction entry in the database with fresh data.

    Args:
        recurring (RecurringInput): The updated data payload to apply.
        recurring_id (int): The unique ID of the target recurring transaction record.
        current_user (dict): The current authenticated user payload containing the user_id.
        db (Session): The active SQLAlchemy database session dependency.

    Raises:
        HTTPException: 404 error if the recurring transaction ID cannot be found for the authenticated user.

    Returns:
        RecurringTransaction: The updated database model entry containing the persisted changes.
    """
    recurring_record = (
        db.query(RecurringTransaction)
        .filter(
            RecurringTransaction.id == recurring_id,
            RecurringTransaction.user_id == current_user["user_id"],
        )
        .first()
    )

    if not recurring_record:
        raise HTTPException(
            status_code=404,
            detail=f"Recurring transaction id {recurring_id} not found.",
        )

    updating_data = recurring.model_dump()
    for key, value in updating_data.items():
        setattr(recurring_record, key, value)

    db.commit()
    db.refresh(recurring_record)
    return recurring_record


@router_recurring.delete(
    "/dlt/{recurring_id}",
    summary="Delete a recurring transaction",
    description="Permanently deletes a recurring transaction record by its ID. Returns 404 if the target ID doesn't exist.",
)
def delete_recurring_transaction(
    recurring_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a specific recurring transaction record from the database.

    Args:
        recurring_id (int): The unique ID of the recurring transaction record to be removed.
        current_user (dict): The current authenticated user payload containing the user_id.
        db (Session): The active SQLAlchemy database session dependency.

    Raises:
        HTTPException: 404 error if the recurring transaction record is missing or not authorized for removal.

    Returns:
        dict: A success status dictionary indicating completion.
    """
    recurring_record = (
        db.query(RecurringTransaction)
        .filter(
            RecurringTransaction.id == recurring_id,
            RecurringTransaction.user_id == current_user["user_id"],
        )
        .first()
    )

    if not recurring_record:
        raise HTTPException(
            status_code=404,
            detail=f"Recurring transaction id {recurring_id} not found.",
        )

    db.delete(recurring_record)
    db.commit()
    return {"message": f"Recurring transaction id {recurring_id} deleted successfully."}
