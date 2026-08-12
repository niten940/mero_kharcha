"""
Token refresh page — /auth/refresh.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from JWT_Authentication.auth import create_access_token, verify_refresh_token

router_token = APIRouter()


class RefreshTokenInput(BaseModel):
    refresh_token: str


@router_token.post(
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