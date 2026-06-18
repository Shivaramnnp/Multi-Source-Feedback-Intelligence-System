"""
Authentication API routes.

Provides login endpoint and current-user dependency.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from app.auth.jwt import create_access_token, verify_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

# Demo credentials
DEMO_USERNAME = "admin"
DEMO_PASSWORD = "admin123"


class LoginRequest(BaseModel):
    """Login request schema."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and get JWT token",
)
async def login(request: LoginRequest):
    """Authenticate with demo credentials and receive a JWT token."""
    if request.username != DEMO_USERNAME or request.password != DEMO_PASSWORD:
        logger.warning("Failed login attempt for user: %s", request.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": request.username})
    logger.info("User '%s' logged in successfully.", request.username)
    return TokenResponse(access_token=token)


async def get_current_user(token: str | None = Depends(oauth2_scheme)) -> dict | None:
    """Dependency to get the current authenticated user.

    Returns None if no token is provided (allowing unauthenticated access).
    Raises HTTPException if token is invalid.
    """
    if token is None:
        return None
    return verify_token(token)
