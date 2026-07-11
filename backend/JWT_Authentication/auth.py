# auth.py
from datetime import datetime, timedelta
from jose import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from dotenv import load_dotenv
import os

load_dotenv("../.env")

SECRET_KEY = os.getenv("SERECT_KEY")
ALGORITHM = os.getenv("ALGORITHM")

router = APIRouter()

def create_access_token(data: dict) -> str:
    """
    TODO: docstring here
    """
    to_encode = data.copy()
    # TODO: add expiry to to_encode
    # TODO: return encoded JWT

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    TODO: docstring here
    """
    # TODO: hardcoded user check
    # TODO: verify password
    # TODO: return token or raise 401