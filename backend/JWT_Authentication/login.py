"""
Login page — /auth/login (username+password) and /auth/login/google.
"""
import os
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from database import get_db
from rate_limiter import limiter
from sql_Alchemy_db_model.user_models import Users
from JWT_Authentication.hash_test import verify_password
from JWT_Authentication.auth import create_access_token, create_refresh_token

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

router_auth_login = APIRouter()


@router_auth_login.post("/login")
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Logs in a user and issues both a JWT access token and a refresh token.

    Args:
        request (Request): The incoming request, required by the rate limiter.
        form_data (OAuth2PasswordRequestForm): Collects username and password as form data.
        db (Session): The database session.

    Returns:
        dict: Contains 'access_token', 'refresh_token', and 'token_type' (str).
    """
    user = db.query(Users).filter(Users.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(form_data.password, user.hashed_password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": user.username, "user_id": user.id})
    refresh_token = create_refresh_token(data={"sub": user.username, "user_id": user.id})
    return {"access_token": token, "refresh_token": refresh_token, "token_type": "bearer"}


@router_auth_login.post(
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
        dict: Access token metadata.

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
                username=google_email,
                full_name=google_payload.get("name", google_email),
                email=google_email,
                phone="",
                currency="NPR",
                nationality="",
                age=18,
                gender="",
                hashed_password=None,
            )
            db.add(user_check)
            db.commit()
            db.refresh(user_check)

        jwt_token = create_access_token(data={"sub": user_check.username, "user_id": user_check.id})
        refresh_token = create_refresh_token(data={"sub": user_check.username, "user_id": user_check.id})
        return {"access_token": jwt_token, "refresh_token": refresh_token, "token_type": "bearer"}

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")