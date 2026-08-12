"""
Forgot/reset password — /auth/forgot-password, /auth/reset-password.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from database import get_db
from sql_Alchemy_db_model.user_models import Users
from JWT_Authentication.auth import (
    create_password_reset_token,
    verify_password_reset_token,
)
from JWT_Authentication.hash_test import hash_password
from routers.email_notifications import send_password_reset_email

router_forgot_password = APIRouter()


class ForgotPasswordInput(BaseModel):
    email: EmailStr


class ResetPasswordInput(BaseModel):
    token: str
    new_password: str


@router_forgot_password.post(
    "/forgot-password",
    summary="Request a password reset link",
    description=(
        "Sends a password reset email if the account exists and is not a "
        "Google-only account. Always returns the same generic message to avoid "
        "leaking which emails are registered."
    ),
)
def forgot_password(
    payload: ForgotPasswordInput, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """
    Send a password reset email for a registered, non-Google account.

    Args:
        payload (ForgotPasswordInput): The email address to send the reset link to.
        db (Session): The database session.

    Returns:
        dict: Generic confirmation message regardless of whether the email exists.
    """
    user = db.query(Users).filter(Users.email == payload.email).first()
    
    if user and user.hashed_password is not None:
        token = create_password_reset_token(user.username, user.id)
        background_tasks.add_task(
            send_password_reset_email,
            to_email=user.email,
            full_name=user.full_name,
            reset_token=token,
        )
    return {
        "message": "If an account exists with this email, a reset link has been sent."
    }


@router_forgot_password.post(
    "/reset-password",
    summary="Reset password using a valid reset token",
    description="Validates the purpose-scoped reset token and updates the password.",
)
def reset_password(
    payload: ResetPasswordInput, db: Session = Depends(get_db)
):
    """
    Reset a user's password using a valid purpose-scoped JWT.

    Args:
        payload (ResetPasswordInput): The reset token and new plaintext password.
        db (Session): The database session.

    Raises:
        HTTPException: 400 if the token is invalid, expired, or not a reset token.
        HTTPException: 404 if the user no longer exists.

    Returns:
        dict: Confirmation that the password has been reset.
    """
    token_data = verify_password_reset_token(payload.token)
    if not token_data:
        raise HTTPException(
            status_code=400, detail="Invalid reset token."
        )

    user = db.query(Users).filter(Users.id == token_data["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.hashed_password = hash_password(payload.new_password)
    db.commit()

    return {"message": "Password has been reset."}