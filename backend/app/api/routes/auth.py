"""Authentication routes."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token, create_access_token
from app.schemas.auth import RegisterRequest, TokenResponse, LoginRequest, RefreshRequest
from app.schemas.user import UserResponse
from app.services.auth_service import register_user, authenticate_user
from app.models.user import User
from sqlalchemy import select

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Register a new user."""
    return await register_user(db, user_in)


@router.post("/login", response_model=TokenResponse)
async def login(
    login_in: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Login with username and password."""
    return await authenticate_user(db, login_in)


@router.post("/token", response_model=TokenResponse)
async def login_oauth2(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """OAuth2 compatible token login, used for Swagger UI."""
    return await authenticate_user(db, LoginRequest(username=form_data.username, password=form_data.password))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_in: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Refresh access token."""
    payload = decode_token(refresh_in.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
        
    # Verify user still exists
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
        
    # Create new access token (keep same refresh token for now, or rotate it)
    access_token = create_access_token(subject=user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_in.refresh_token,
        token_type="bearer"
    )
