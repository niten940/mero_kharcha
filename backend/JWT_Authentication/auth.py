import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from pydantic import BaseModel

# 1. Load environment variables FIRST before reading os.getenv
load_dotenv(r"D:\mero_kharcha\backend\.env")

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from database import get_db
from JWT_Authentication.hash_test import hash_password, verify_password
from sqlAlchemy.user_models import Users

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth_login/login")

router_login = APIRouter()


# Pydantic models for request validation
class RegistrationData(BaseModel):
    username: str
    email: str
    password: str
    fullName: str = None
    phone: str = None
    currency: str = "NPR"
    nationality: str = None
    age: int = None
    gender: str = None
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("user_id")

        if username is None:
            raise HTTPException(
                status_code=401, detail="Invalid or expired token"
            )
        return {"username": username, "user_id": user_id}

    except JWTError:
        raise HTTPException(
            status_code=401, detail="Error occurred: JWTError occurred."
        )



def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    # Use timezone-aware UTC datetime
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router_login.post(
    "/register",
    status_code=201,
    summary="Register a new user",
    description="Creates a new user account with a hashed password and profile information.",
)
def register(
    registration_data: RegistrationData,
    db: Session = Depends(get_db)
):
    """
    Register a new user account with profile information.

    Args:
        registration_data (RegistrationData): User registration data including profile fields.
        db (Session): The database session.

    Returns:
        dict: A success message confirming account creation and user_id.
    """
    try:
        existing = (
            db.query(Users)
            .filter((Users.username == registration_data.username) | (Users.email == registration_data.email))
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400, detail="Username or email already registered"
            )

        hashed = hash_password(registration_data.password)
        new_user = Users(
            username=registration_data.username,
            email=registration_data.email,
            hashed_password=hashed,
            full_name=registration_data.fullName,
            phone=registration_data.phone,
            currency=registration_data.currency,
            nationality=registration_data.nationality,
            age=registration_data.age,
            gender=registration_data.gender
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": f"User {registration_data.username} registered successfully", "user_id": new_user.id}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Registration error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Registration failed: {str(e)}"
        )




@router_login.post("/login")
def login(
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
    user = (
        db.query(Users).filter((Users.username == form_data.username) | (Users.email == form_data.username)).first()
    )
    if not user or not user.hashed_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    try:
       is_valid = verify_password(form_data.password, user.hashed_password)
    except Exception as e:
        print(f"Password verification failed with exception: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )
    return {"access_token": token, "token_type": "bearer"}


@router_login.post(
    "/login/google",
    summary="Login or register via Google",
    description="Verifies a Google ID token, then finds or creates the matching user and issues a JWT.",
)
def login_google(token: str, db: Session = Depends(get_db)):
    try:
        google_payload = id_token.verify_oauth2_token(
            token, google_requests.Request(), GOOGLE_CLIENT_ID
        )
        google_email = google_payload.get("email")

        user_check = (
            db.query(Users).filter(Users.email == google_email).first()
        )

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
        return {"access_token": jwt_token, "token_type": "bearer"}

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")
