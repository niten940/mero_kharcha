"""
Forgot/reset password page — /auth/forgot-password and /auth/reset-password.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from database import get_db
from rate_limiter import limiter
from sql_Alchemy_db_model.user_models import Users
from JWT_Authentication.hash_test import hash_password
from JWT_Authentication.auth import create_password_reset_token, verify_password_reset_token

router_password = APIRouter()


class ForgotPasswordInput(BaseModel):
    email: EmailStr


class ResetPasswordInput(BaseModel):
    token: str
    new_password: str


@router_password.post(
    "/forgot-password",
    summary="Request a password reset",
    description="Generates a password reset token for a registered email. Google-only accounts (no password set) are rejected with guidance to use Google Sign-In instead.",
)
@limiter.limit("3/minute")
def forgot_password(request: Request, payload: ForgotPasswordInput, db: Session = Depends(get_db)):
    """
    Request a password reset token for the given email.

    Args:
        request (Request): The incoming request, required by the rate limiter.
        payload (ForgotPasswordInput): The email address to send a reset link to.
        db (Session): The database session.

    Raises:
        HTTPException: 400 if the account is Google-only (no password to reset).

    Returns:
        dict: A generic confirmation message (token is emailed, not returned in the response, for security).
    """
    user = db.query(Users).filter(Users.email == payload.email).first()

    if not user:
        return {"message": "If an account exists with this email, a reset link has been sent."}

    if user.hashed_password is None:
        raise HTTPException(
            status_code=400,
            detail="This account signs in with Google. Please use 'Sign in with Google' instead of resetting a password.",
        )

    reset_token = create_password_reset_token(user.id)

    # TODO: send `reset_token` via email once SMTP credentials are set up in .env.
    # Example: send_reset_email(user.email, reset_token)

    return {"message": "If an account exists with this email, a reset link has been sent."}


@router_password.post(
    "/reset-password",
    summary="Reset password using a valid token",
    description="Validates a password reset token and sets a new password for the account.",
)
def reset_password(payload: ResetPasswordInput, db: Session = Depends(get_db)):
    """
    Reset a user's password using a valid reset token.

    Args:
        payload (ResetPasswordInput): The reset token and new plaintext password.
        db (Session): The database session.

    Raises:
        HTTPException: 400 if the token is invalid/expired. 404 if the associated user no longer exists.

    Returns:
        dict: A success message confirming the password was reset.
    """
    user_id = verify_password_reset_token(payload.token)

    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Account no longer exists.")

    user.hashed_password = hash_password(payload.new_password).decode("utf-8")
    db.commit()

    return {"message": "Password has been reset successfully. You can now log in."}