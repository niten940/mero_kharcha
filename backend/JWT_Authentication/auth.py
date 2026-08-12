"""
Shared JWT core — token creation/validation and auth dependencies.
Route handlers (register, login, forgot-password, refresh) live in their
own modules and import from here, so other routers across the project
(expenses.py, goals.py, admin.py, etc.) keep working unchanged via
`from JWT_Authentication.auth import get_current_user`.
"""
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from database import get_db
from sql_Alchemy_db_model.user_models import Users

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(data: dict) -> str:
    """
    Creates access token for user to login to the system.

    Args:
        data (dict): Payload to encode, typically contains 'sub' (username).

    Returns:
        str: Signed JWT token string.
    """
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=30)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """
    Creates a long-lived refresh token for a user.

    Args:
        data (dict): Payload to encode, typically contains 'sub' (username) and 'user_id'.

    Returns:
        str: Signed JWT valid for REFRESH_TOKEN_EXPIRE_DAYS, with a 'purpose' claim marking it as refresh-only.
    """
    to_encode = data.copy()
    to_encode["purpose"] = "refresh"
    to_encode["exp"] = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_refresh_token(token: str) -> dict:
    """
    Validate a refresh token and extract its payload.

    Args:
        token (str): The refresh token to validate.

    Raises:
        HTTPException: 401 if the token is invalid, expired, or not a refresh-purpose token.

    Returns:
        dict: Contains 'username' and 'user_id' from the token payload.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

    if payload.get("purpose") != "refresh":
        raise HTTPException(status_code=401, detail="Token is not a valid refresh token.")

    username = payload.get("sub")
    user_id = payload.get("user_id")
    if username is None or user_id is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token.")

    return {"username": username, "user_id": user_id}


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get current user token for protecting the APIs.

    Args:
        token (str): Takes token from oauth2_scheme.

    Returns:
        dict: username and role of the logged in user.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("user_id")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return {"username": username, "user_id": user_id}

    except JWTError:
        raise HTTPException(status_code=401, detail="Error occured: JWTError occured.")


def get_current_admin(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict:
    """
    Verify the current authenticated user has admin privileges.

    Args:
        current_user (dict): The current authenticated user payload from get_current_user.
        db (Session): The database session.

    Raises:
        HTTPException: 403 if the user is not an admin.

    Returns:
        dict: The same current_user payload, confirmed as admin.
    """
    user = db.query(Users).filter(Users.id == current_user["user_id"]).first()
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required.")
    return current_user


def create_password_reset_token(user_id: int) -> str:
    """
    Create a short-lived JWT scoped only for password reset (not a login token).

    Args:
        user_id (int): The ID of the user requesting a reset.

    Returns:
        str: Signed JWT valid for 15 minutes, with a 'purpose' claim to prevent misuse as a login token.
    """
    to_encode = {
        "user_id": user_id,
        "purpose": "password_reset",
        "exp": datetime.utcnow() + timedelta(minutes=15),
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_password_reset_token(token: str) -> int:
    """
    Validate a password reset token and extract the user_id.

    Args:
        token (str): The reset token from the confirm-reset request.

    Raises:
        HTTPException: 400 if the token is invalid, expired, or not a reset-purpose token.

    Returns:
        int: The user_id the token was issued for.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")

    if payload.get("purpose") != "password_reset":
        raise HTTPException(status_code=400, detail="Invalid reset token.")

    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=400, detail="Invalid reset token.")

    return user_id