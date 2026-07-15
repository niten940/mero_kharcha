from sys import exec_prefix
from datetime import datetime, timedelta
from jose import jwt,JWTError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from dotenv import load_dotenv
import os
from JWT_Authentication.hash_test import verify_password

load_dotenv(r"D:\mero_kharcha\backend\.env")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth_login/login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

router_login = APIRouter()

def get_current_user(token:str = Depends(oauth2_scheme)):
    """
    Get current user token for protecting the APIs.

    Args:
        token(str): takes token from oauth2_scheme

    Returns:
        username: username and role: role of the logged in user.

    """
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")

        if username is None:
            raise HTTPException(status_code=401, detail= "Invalid or expired token")
        if role is None:
            raise HTTPException(status_code=401, detail= "Invalid or expired token")
        return {"username": username, "role": role}
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Error occured: JWTError occured.")
        
def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Checks if user is admin or not for role based access.

    Args:
        current_user(dict): get the username and role from get_current_user as dictionary

    Returns:
        role: role of the logged in user.

    """
    try:
        if current_user["role"] != "Admin":
            raise HTTPException(status_code=403, detail="Admin only")
        return current_user
    except JWTError:
        raise HTTPException(status_code=401, detail="Error occured: JWTError occured.")

def create_access_token(data: dict) -> str:
    """
    Creates access token for user to login to the system

    Args:
        data (dict): Payload to encode, typically contains 'sub' (username).

    Returns:
        str: Signed JWT token string.

    """
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=30)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router_login.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), role: str = "admin"):
    """
    Logs in user to the system.

    Args:
        form_data (OAuth2PasswordRequestForm): collect username and password as form data for the OAuth2 password flow

    Returns:
        dict: Contains 'access_token' (str) and 'token_type' (str).
    """
    if form_data.username != "zekka":
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(form_data.password, b"$2b$12$JqyrHn4YA88u.XUsKPujq.8mNuixyrQmZ2GRZSJHlvvNhzl8jfMdK"):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": form_data.username, "role": "admin"})
    return {"access_token": token, "token_type": "bearer", "role": role}

