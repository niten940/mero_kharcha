from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm.session import Session
from database import get_db
from JWT_Authentication.auth import get_current_user
from sql_Alchemy_db_model.goal_deposit_model import Goal_Deposit
from sql_Alchemy_db_model.goals_model import Goals
from pydantic import BaseModel
from datetime import date

router_goal_deposit = APIRouter()


class GoalDepositInput(BaseModel):
    goal_id: int
    amount: float
    date: date


class GoalDepositUpdateInput(BaseModel):
    amount: float
    date: date


@router_goal_deposit.get(
    "/{goal_deposit_id}",
    summary="Get a goal_deposit by ID",
    description="Fetches a specific financial goal_deposit entry belonging to the authenticated user.",
)
def get_goal_deposit(
    goal_deposit_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Fetch a single goal_deposit from the database by its unique identifier.

    Args:
        goal_deposit_id (int): The unique ID of the goal_deposit record.
        current_user (dict): The current authenticated user payload containing the user_id.
        db (Session): The active SQLAlchemy database session dependency.

    Raises:
        HTTPException: 404 error if the goal_deposit record does not exist or does not belong to the user.

    Returns:
        Goal_Deposit: The matching database record containing the goal_deposit information.
    """
    goal_deposit_details = (
        db.query(Goal_Deposit)
        .filter(
            Goal_Deposit.user_id == current_user["user_id"],
            Goal_Deposit.id == goal_deposit_id,
        )
        .first()
    )

    if goal_deposit_details is None:
        raise HTTPException(status_code=404, detail="Goal deposit not found")

    return goal_deposit_details


@router_goal_deposit.get(
    "/",
    summary="Return list of goal_deposit rows of current users",
    description="Returns all goal_deposit, optionally filtered by user id",
)
def get_goal_deposit_Query(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """
    Returns all goal_deposit rows belonging to the current user.

    Args:
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Returns:
        list: List of goal_deposits of current users.
    """
    query = (
        db.query(Goal_Deposit)
        .filter(Goal_Deposit.user_id == current_user["user_id"])
        .order_by(Goal_Deposit.id.desc())
    )
    return query.all()


@router_goal_deposit.post(
    "/post/",
    status_code=201,
    summary="Create a new goal_deposit",
    description="Creates a new financial goal deposit entry associated with the logged-in user.",
)
def create_goal_deposit(
    goalDeposit: GoalDepositInput,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new goal_deposit entry in the database.

    Args:
        goalDeposit (GoalDepositInput): The validated input data payload containing goal_id, amount, and date.
        current_user (dict): The current authenticated user payload containing the user_id.
        db (Session): The active SQLAlchemy database session dependency.

    Raises:
        HTTPException: 404 error if the associated goal does not exist or does not belong to the user.

    Returns:
        Goal_Deposit: The newly created goal deposit record.
    """
    user_id = current_user["user_id"]

    goal_record = (
        db.query(Goals)
        .filter(Goals.id == goalDeposit.goal_id, Goals.user_id == user_id)
        .first()
    )
    if not goal_record:
        raise HTTPException(
            status_code=404,
            detail=f"Goal id {goalDeposit.goal_id} not found for this user.",
        )

    add_goal_deposit = Goal_Deposit(
        user_id=user_id,
        goal_id=goalDeposit.goal_id,
        amount=goalDeposit.amount,
        date=goalDeposit.date,
    )
    db.add(add_goal_deposit)

    goal_record.current_amount += goalDeposit.amount

    db.commit()
    db.refresh(add_goal_deposit)
    return add_goal_deposit


@router_goal_deposit.put(
    "/put/{goal_deposit_id}",
    summary="Update an existing goal_deposit",
    description="Updates amount and date fields of a specific goal_deposit by ID, balancing the running total.",
)
def update_goal_deposit(
    goal_deposit: GoalDepositUpdateInput,
    goal_deposit_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an existing goal_deposit entry in the database with fresh data.

    Args:
        goal_deposit (GoalDepositUpdateInput): The updated data payload to apply (amount and date only).
        goal_deposit_id (int): The unique ID of the target goal_deposit record.
        current_user (dict): The current authenticated user payload containing the user_id.
        db (Session): The active SQLAlchemy database session dependency.

    Raises:
        HTTPException: 404 error if the goal deposit or its associated goal cannot be found.

    Returns:
        Goal_Deposit: The updated goal_deposit record.
    """
    user_id = current_user["user_id"]

    goal_deposit_record = (
        db.query(Goal_Deposit)
        .filter(
            Goal_Deposit.id == goal_deposit_id,
            Goal_Deposit.user_id == user_id,
        )
        .first()
    )
    if not goal_deposit_record:
        raise HTTPException(
            status_code=404, detail=f"Goal_Deposit id {goal_deposit_id} not found."
        )

    goal_record = (
        db.query(Goals)
        .filter(Goals.id == goal_deposit_record.goal_id, Goals.user_id == user_id)
        .first()
    )
    if not goal_record:
        raise HTTPException(status_code=404, detail="Associated Goal not found.")

    old_amount = float(goal_deposit_record.amount)
    new_amount = goal_deposit.amount
    goal_record.current_amount = (
        float(goal_record.current_amount) - old_amount + new_amount
    )

    updating_data = goal_deposit.model_dump()
    for key, value in updating_data.items():
        setattr(goal_deposit_record, key, value)

    db.commit()
    db.refresh(goal_deposit_record)
    return goal_deposit_record


@router_goal_deposit.delete(
    "/dlt/{goal_deposit_id}",
    summary="Delete a goal_deposit",
    description="Permanently deletes a goal_deposit record by its ID and updates the running goal total.",
)
def delete_goal_deposit(
    goal_deposit_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a specific goal_deposit record from the database.

    Args:
        goal_deposit_id (int): The unique ID of the goal_deposit record to be removed.
        current_user (dict): The current authenticated user payload containing the user_id.
        db (Session): The active SQLAlchemy database session dependency.

    Raises:
        HTTPException: 404 error if the goal_deposit record is missing or unauthorized.

    Returns:
        dict: A success status dictionary indicating completion.
    """
    user_id = current_user["user_id"]

    goal_deposit_record = (
        db.query(Goal_Deposit)
        .filter(
            Goal_Deposit.id == goal_deposit_id,
            Goal_Deposit.user_id == user_id,
        )
        .first()
    )
    if not goal_deposit_record:
        raise HTTPException(
            status_code=404, detail=f"Goal_Deposit id {goal_deposit_id} not found."
        )

    goal_record = (
        db.query(Goals)
        .filter(Goals.id == goal_deposit_record.goal_id, Goals.user_id == user_id)
        .first()
    )

    if goal_record:
        goal_record.current_amount -= goal_deposit_record.amount

    db.delete(goal_deposit_record)
    db.commit()
    return {"message": f"Goal deposit id {goal_deposit_id} deleted successfully."}
