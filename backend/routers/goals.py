from fastapi import HTTPException
from datetime import date
from pydantic import BaseModel
from database import get_db
from sqlalchemy.orm.session import Session
from sqlalchemy import func
from fastapi import APIRouter, Depends
from JWT_Authentication.auth import get_current_user
from sql_Alchemy_db_model.goals_model import Goals
from sql_Alchemy_db_model.goal_deposit_model import Goal_Deposit
from datetime import date, timedelta

router_goals = APIRouter()


class GoalsInput(BaseModel):
    title: str
    current_amount: float
    goal_amount: float
    target_date: date
    description: str


def calculate_goal_progress(goal: Goals, db: Session) -> dict:
    """
    Calculate progress percentage, remaining amount, and required monthly payment for a goal,
    using a rolling 3-month deposit average (velocity engine) for projected completion date.

    Args:
        goal (Goals): The goal database record.
        db (Session): The active SQLAlchemy database session dependency.

    Returns:
        dict: The goal's fields plus 'progress_percent', 'remaining_amount', 'projected_completion_date', and 'required_monthly_payment'.
    """
    current = float(goal.current_amount)
    target = float(goal.goal_amount)

    progress_percent = round((current / target) * 100, 2) if target > 0 else 0
    remaining_amount = round(target - current, 2)

    # Rolling 3-month deposit velocity: sum deposits from the last 3 calendar months,
    # divide by 3 regardless of how many of those months actually had deposits.
    three_months_ago = date.today() - timedelta(days=90)

    recent_deposits_total = float(
        db.query(func.sum(Goal_Deposit.amount))
        .filter(
            Goal_Deposit.goal_id == goal.id,
            Goal_Deposit.date >= three_months_ago,
        )
        .scalar()
        or 0
    )
    avg_monthly_saving = recent_deposits_total / 3

    if avg_monthly_saving > 0 and remaining_amount > 0:
        months_left = remaining_amount / avg_monthly_saving
        projected_completion_date = date.today() + timedelta(
            days=round(months_left * 30)
        )
    elif remaining_amount <= 0:
        projected_completion_date = date.today()
    else:
        projected_completion_date = None

    months_to_deadline = (goal.target_date.year - date.today().year) * 12 + (
        goal.target_date.month - date.today().month
    )

    if remaining_amount <= 0:
        required_monthly_payment = 0
    elif months_to_deadline <= 0:
        required_monthly_payment = (
            remaining_amount  # deadline is this month or has passed — pay it all now
        )
    else:
        required_monthly_payment = round(remaining_amount / months_to_deadline, 2)

    return {
        "id": goal.id,
        "title": goal.title,
        "current_amount": current,
        "goal_amount": target,
        "target_date": goal.target_date,
        "description": goal.description,
        "progress_percent": progress_percent,
        "remaining_amount": remaining_amount,
        "projected_completion_date": projected_completion_date,
        "required_monthly_payment": required_monthly_payment,
    }


@router_goals.get(
    "/{goal_id}",
    summary="Get a goal by ID",
    description="Fetches a specific financial goal entry belonging to the authenticated user.",
)
def get_goals(
    goal_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Fetch a single goal from the database by its unique identifier.

    Args:
        goal_id (int): The unique ID of the goal record.
        current_user (dict): The current authenticated user payload containing the user_id.
        db (Session): The active SQLAlchemy database session dependency.

    Raises:
        HTTPException: 404 error if the goal record does not exist or does not belong to the user.

    Returns:
        Goals: The matching database record containing the goal information.
    """
    goal_details = (
        db.query(Goals)
        .filter(Goals.user_id == current_user["user_id"], Goals.id == goal_id)
        .first()
    )

    if goal_details is None:
        raise HTTPException(status_code=404, detail="Goal not found")

    return calculate_goal_progress(goal_details, db)


@router_goals.get(
    "/",
    summary="Return list of Goals rows of current users",
    description="Returns all goals, optionally filtered by user id",
)
def get_goals_Query(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """
    Returns all goals, optionally filtered by user_id/current user expenses.

    Args:
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Returns:
        list: List of Goals of current users.
    """
    query = (
        db.query(Goals)
        .filter(Goals.user_id == current_user["user_id"])
        .order_by(Goals.id.desc())
    )
    return [calculate_goal_progress(g, db) for g in query.all()]


@router_goals.post(
    "/post/",
    status_code=201,
    summary="Create a new goal",
    description="Creates a new financial goal entry associated with the logged-in user.",
)
def create_goal(
    goal: GoalsInput,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new goal entry in the database.

    Args:
        goal (GoalsInput): The validated input data payload containing title, amounts, and target date.
        current_user (dict): The current authenticated user payload containing the user_id.
        db (Session): The active SQLAlchemy database session dependency.

    Returns:
        dict: The newly created goal's fields plus progress_percent, remaining_amount, projected_completion_date, and required_monthly_payment.
    """
    user_id = current_user["user_id"]

    add_goals = Goals(
        user_id=user_id,
        title=goal.title,
        current_amount=goal.current_amount,
        goal_amount=goal.goal_amount,
        description=goal.description,
        target_date=goal.target_date,
    )
    db.add(add_goals)
    db.commit()
    db.refresh(add_goals)
    return calculate_goal_progress(add_goals, db)


@router_goals.put(
    "/put/{goal_id}",
    summary="Update an existing goal",
    description="Updates all fields of a specific goal by ID. Returns 404 if the goal doesn't exist.",
)
def update_goal(
    goal: GoalsInput,
    goal_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an existing goal entry in the database with fresh data.

    Args:
        goal (GoalsInput): The updated data payload to apply.
        goal_id (int): The unique ID of the target goal record.
        current_user (dict): The current authenticated user payload containing the user_id.
        db (Session): The active SQLAlchemy database session dependency.

    Raises:
        HTTPException: 404 error if the goal ID cannot be found for the authenticated user.

    Returns:
        dict: The updated goal's fields plus progress_percent, remaining_amount, projected_completion_date, and required_monthly_payment.
    """
    goal_record = (
        db.query(Goals)
        .filter(Goals.id == goal_id, Goals.user_id == current_user["user_id"])
        .first()
    )
    if not goal_record:
        raise HTTPException(status_code=404, detail=f"Goals id {goal_id} not found.")

    updating_data = goal.model_dump()
    for key, value in updating_data.items():
        setattr(goal_record, key, value)

    db.commit()
    db.refresh(goal_record)
    return calculate_goal_progress(goal_record, db)


@router_goals.delete(
    "/dlt/{goal_id}",
    summary="Delete a goal",
    description="Permanently deletes a goal record by its ID. Returns 404 if the target ID doesn't exist.",
)
def delete_goal(
    goal_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a specific goal record from the database.

    Args:
        goal_id (int): The unique ID of the goal record to be removed.
        current_user (dict): The current authenticated user payload containing the user_id.
        db (Session): The active SQLAlchemy database session dependency.

    Raises:
        HTTPException: 404 error if the goal record is missing or not authorized for removal.

    Returns:
        dict: A success status dictionary indicating completion.
    """
    goal_record = (
        db.query(Goals)
        .filter(Goals.id == goal_id, Goals.user_id == current_user["user_id"])
        .first()
    )
    if not goal_record:
        raise HTTPException(status_code=404, detail=f"Goals id {goal_id} not found.")

    db.delete(goal_record)
    db.commit()
    return {"message": f"Goal id {goal_id} deleted successfully."}
