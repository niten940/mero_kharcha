"""
Profile update — PUT /auth/profile.
Handles partial updates to user profile fields.
Sensitive field changes (email, password) require current password verification
and trigger a notification email.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from JWT_Authentication.auth import get_current_user
from JWT_Authentication.hash_test import hash_password, verify_password
from sql_Alchemy_db_model.user_models import Users
from routers.email_notifications import send_profile_update_email

router_profile = APIRouter()


class ProfileUpdateInput(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1)
    phone: Optional[str] = Field(None, pattern=r"^\+?[0-9]{7,15}$")
    nationality: Optional[str] = Field(None, min_length=1)
    age: Optional[int] = Field(None, gt=0, lt=120)
    gender: Optional[str] = None
    currency: Optional[str] = None
    email: Optional[EmailStr] = None
    new_password: Optional[str] = Field(None, min_length=8)
    current_password: Optional[str] = None


@router_profile.put(
    "/profile",
    summary="Update user profile",
    description=(
        "Partially updates the authenticated user's profile. "
        "Sensitive changes (email, password) require current_password to be provided. "
        "A notification email is sent for each sensitive field changed."
    ),
)
def update_profile(
    payload: ProfileUpdateInput,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Partially update the authenticated user's profile fields.

    Non-sensitive fields (full_name, phone, nationality, age, gender, currency)
    are updated directly. Sensitive fields (email, new_password) require
    current_password verification before applying the change.

    Args:
        payload (ProfileUpdateInput): Fields to update. All fields are optional.
            current_password is required if email or new_password is provided.
        background_tasks (BackgroundTasks): FastAPI background task runner for
            sending notification emails without blocking the response.
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Raises:
        HTTPException: 400 if sensitive fields are provided without current_password.
        HTTPException: 400 if current_password is incorrect.
        HTTPException: 400 if the new email is already registered to another account.
        HTTPException: 404 if the user record cannot be found.

    Returns:
        dict: Confirmation message and updated non-sensitive profile fields.
    """
    user = db.query(Users).filter(Users.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    sensitive_change_requested = payload.email is not None or payload.new_password is not None

    # Require current password for any sensitive change.
    if sensitive_change_requested:
        if not payload.current_password:
            raise HTTPException(
                status_code=400,
                detail="current_password is required to change email or password.",
            )
        if not user.hashed_password:
            raise HTTPException(
                status_code=400,
                detail="This account uses Google Sign-In and has no password to verify.",
            )
        if not verify_password(payload.current_password, user.hashed_password):
            raise HTTPException(
                status_code=400,
                detail="Current password is incorrect.",
            )

    # Apply non-sensitive fields.
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.phone is not None:
        user.phone = payload.phone
    if payload.nationality is not None:
        user.nationality = payload.nationality
    if payload.age is not None:
        user.age = payload.age
    if payload.gender is not None:
        user.gender = payload.gender
    if payload.currency is not None:
        user.currency = payload.currency

    # Apply sensitive fields — password verified above.
    if payload.email is not None:
        duplicate = (
            db.query(Users)
            .filter(Users.email == payload.email, Users.id != user.id)
            .first()
        )
        if duplicate:
            raise HTTPException(
                status_code=400,
                detail="This email address is already registered to another account.",
            )
        user.email = payload.email
        background_tasks.add_task(
            send_profile_update_email,
            to_email=user.email,
            full_name=user.full_name,
            changed_field="email address",
        )

    if payload.new_password is not None:
        user.hashed_password = hash_password(payload.new_password)
        background_tasks.add_task(
            send_profile_update_email,
            to_email=user.email,
            full_name=user.full_name,
            changed_field="password",
        )

    db.commit()
    db.refresh(user)

    return {
        "message": "Profile updated successfully.",
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "nationality": user.nationality,
        "age": user.age,
        "gender": user.gender,
        "currency": user.currency,
    }