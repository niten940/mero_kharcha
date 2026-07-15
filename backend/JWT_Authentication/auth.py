from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from JWT_Authentication.hash_test import verify_password, hash_password
from database import get_db
from sqlAlchemy.user_models import Users
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
load_dotenv(r"D:\mero_kharcha\backend\.env")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth_login/login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

router_login = APIRouter()

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

@router_login.post("/register", status_code=201, summary="Register a new user", description="Creates a new user account with a hashed password.")
def register(username: str, email: str, password: str, db: Session = Depends(get_db)):
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
    existing = db.query(Users).filter(
        (Users.username == username) | (Users.email == email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    hashed = hash_password(password).decode("utf-8")
    new_user = Users(username=username, email=email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"User {username} registered successfully"}

@router_login.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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

    token = create_access_token(data={"sub": user.username, "user_id":user.id})
    return {"access_token": token, "token_type": "bearer"}

@router_login.post("/login/google", summary="Login or register via Google", description="Verifies a Google ID token, then finds or creates the matching user and issues a JWT.")
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
        google_payload = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)
        google_email = google_payload.get("email")

        user_check = db.query(Users).filter(Users.email == google_email).first()

        if user_check is None:
            user_check = Users(username=google_email, email=google_email, hashed_password=None)
            db.add(user_check)
            db.commit()
            db.refresh(user_check)

        jwt_token = create_access_token(data={"sub": user_check.username, "user_id": user_check.id})
        return {"access_token": jwt_token, "token_type": "bearer"}

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")