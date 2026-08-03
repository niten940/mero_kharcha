"""
Registration page — /auth/register.
"""
import re
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from better_profanity import profanity
from database import get_db
from rate_limiter import limiter
from sql_Alchemy_db_model.user_models import Users
from JWT_Authentication.hash_test import hash_password

profanity.load_censor_words()

router_register = APIRouter()


class RegisterInput(BaseModel):
    full_name: str = Field(..., min_length=1)
    email: EmailStr
    phone: str = Field(..., pattern=r"^\+?[0-9]{7,15}$")
    currency: str = "NPR"
    nationality: str = Field(..., min_length=1)
    age: int = Field(..., gt=0, lt=120)
    gender: str
    password: str = Field(..., min_length=8)


def _generate_unique_username(full_name: str, email: str, db: Session) -> str:
    """
    Derive a unique username from the email's local part, falling back to a
    numeric suffix if that username is already taken.

    Args:
        full_name (str): The user's full name (used only as a fallback base if email parsing yields nothing usable).
        email (str): The user's email address.
        db (Session): The database session.

    Returns:
        str: A username guaranteed not to collide with an existing row.
    """
    base = email.split("@")[0].lower()
    base = re.sub(r"[^a-z0-9_]", "", base) or re.sub(r"[^a-z0-9_]", "", full_name.lower()) or "user"

    candidate = base
    suffix = 1
    while db.query(Users).filter(Users.username == candidate).first():
        candidate = f"{base}{suffix}"
        suffix += 1

    return candidate


@router_register.post(
    "/register",
    status_code=201,
    summary="Register a new user",
    description="Creates a new user account with a hashed password. Username is auto-derived from the email address since the signup form does not collect one.",
)
@limiter.limit("5/minute")
def register(request: Request, payload: RegisterInput, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Args:
        request (Request): The incoming request, required by the rate limiter.
        payload (RegisterInput): Signup form data — full_name, email, phone, currency, nationality, age, gender, password.
        db (Session): The database session.

    Raises:
        HTTPException: 400 if the email is already registered, or the derived username/full name contains profanity.

    Returns:
        dict: A success message confirming account creation, plus the generated username.
    """
    existing = db.query(Users).filter(Users.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    username = _generate_unique_username(payload.full_name, payload.email, db)

    if profanity.contains_profanity(username) or profanity.contains_profanity(payload.full_name):
        raise HTTPException(
            status_code=400,
            detail="Name contains inappropriate language. Please use a different name.",
        )

    hashed = hash_password(payload.password).decode("utf-8")
    new_user = Users(
        username=username,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        currency=payload.currency,
        nationality=payload.nationality,
        age=payload.age,
        gender=payload.gender,
        hashed_password=hashed,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"User {username} registered successfully", "username": username}