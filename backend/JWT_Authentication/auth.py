from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from JWT_Authentication.hash_test import verify_password, hash_password
from database import get_db
from sql_Alchemy_db_model.user_models import Users
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from fastapi import BackgroundTasks
from pydantic import BaseModel, EmailStr
from fastapi import Request
from rate_limiter import limiter
from better_profanity import profanity

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth_login/login")
profanity.load_censor_words()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

router_login = APIRouter()


class ForgotPasswordInput(BaseModel):
    email: EmailStr


class ResetPasswordInput(BaseModel):
    token: str
    new_password: str


REFRESH_TOKEN_EXPIRE_DAYS = 7


class RefreshTokenInput(BaseModel):
    refresh_token: str


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
        raise HTTPException(
            status_code=401, detail="Token is not a valid refresh token."
        )

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


@router_login.post(
    "/register",
    status_code=201,
    summary="Register a new user",
    description="Creates a new user account with a hashed password.",
)
@limiter.limit("5/minute")
def register(
    request: Request,
    username: str,
    email: str,
    password: str,
    db: Session = Depends(get_db),
):
    """
    Register a new user account.

    Args:
        username (str): Desired username, must be unique.
        email (str): User's email, must be unique.
        password (str): Plaintext password to be hashed and stored.
        db (Session): The database session.

    Returns:
        dict: A success message confirming account creation.
    """
    existing = (
        db.query(Users)
        .filter((Users.username == username) | (Users.email == email))
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Username or email already registered"
        )

    if profanity.contains_profanity(username):
        raise HTTPException(
            status_code=400,
            detail="Username contains inappropriate language. Please choose another.",
        )

    hashed = hash_password(password).decode("utf-8")
    new_user = Users(username=username, email=email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"User {username} registered successfully"}


@router_login.post("/login")
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Logs in a user and issues a JWT access token.

    Args:
        form_data (OAuth2PasswordRequestForm): Collects username and password as form data.
        db (Session): The database session.

    Returns:
        dict: Contains 'access_token' (str) and 'token_type' (str).
    """
    user = db.query(Users).filter(Users.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(form_data.password, user.hashed_password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": user.username, "user_id": user.id})
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id}
    )
    return {
        "access_token": token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router_login.post(
    "/login/google",
    summary="Login or register via Google",
    description="Verifies a Google ID token, then finds or creates the matching user and issues a JWT.",
)
def login_google(token: str, db: Session = Depends(get_db)):
    """
    Verify a Google ID token, log in or register the user, and issue a JWT.

    Args:
        token (str): The Google ID token from the client.
        db (Session): Database session.

    Returns:
        dict: Access token metadata or a registration success message.

    Raises:
        HTTPException: 401 if token verification fails.
    """
    try:
        google_payload = id_token.verify_oauth2_token(
            token, google_requests.Request(), GOOGLE_CLIENT_ID
        )
        google_email = google_payload.get("email")

        user_check = db.query(Users).filter(Users.email == google_email).first()

        if user_check is None:
            user_check = Users(
                username=google_email, email=google_email, hashed_password=None
            )
            db.add(user_check)
            db.commit()
            db.refresh(user_check)

        jwt_token = create_access_token(
            data={"sub": user_check.username, "user_id": user_check.id}
        )
        refresh_token = create_refresh_token(
            data={"sub": user_check.username, "user_id": user_check.id}
        )
        return {
            "access_token": jwt_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")


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


@router_login.post(
    "/forgot-password",
    summary="Request a password reset",
    description="Generates a password reset token for a registered email. Google-only accounts (no password set) are rejected with guidance to use Google Sign-In instead.",
)
@limiter.limit("3/minute")
def forgot_password(
    request: Request, payload: ForgotPasswordInput, db: Session = Depends(get_db)
):
    """
    Request a password reset token for the given email.

    Args:
        payload (ForgotPasswordInput): The email address to send a reset link to.
        db (Session): The database session.

    Raises:
        HTTPException: 404 if no account exists with this email. 400 if the account is Google-only (no password to reset).

    Returns:
        dict: A generic confirmation message (token is emailed, not returned in the response, for security).
    """
    user = db.query(Users).filter(Users.email == payload.email).first()

    if not user:
        # Return the same generic message as success to avoid leaking which emails are registered.
        return {
            "message": "If an account exists with this email, a reset link has been sent."
        }

    if user.hashed_password is None:
        raise HTTPException(
            status_code=400,
            detail="This account signs in with Google. Please use 'Sign in with Google' instead of resetting a password.",
        )

    reset_token = create_password_reset_token(user.id)

    # TODO: send `reset_token` via email once SMTP credentials are set up in .env.
    # Example: send_reset_email(user.email, reset_token)
    # For now, the token is not returned in the API response for security —
    # during local testing only, you can temporarily log it server-side to test the flow.

    return {
        "message": "If an account exists with this email, a reset link has been sent."
    }


@router_login.post(
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


@router_login.post(
    "/refresh",
    summary="Exchange a refresh token for a new access token",
    description="Validates a refresh token and issues a new short-lived access token, without requiring the user to log in again.",
)
def refresh_access_token(payload: RefreshTokenInput):
    """
    Issue a new access token from a valid refresh token.

    Args:
        payload (RefreshTokenInput): Contains the refresh_token to validate.

    Raises:
        HTTPException: 401 if the refresh token is invalid or expired.

    Returns:
        dict: A new 'access_token' and 'token_type'.
    """
    token_data = verify_refresh_token(payload.refresh_token)
    new_access_token = create_access_token(
        data={"sub": token_data["username"], "user_id": token_data["user_id"]}
    )
    return {"access_token": new_access_token, "token_type": "bearer"}
