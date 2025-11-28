"""Authentication service."""
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse


async def register_user(db: AsyncSession, user_in: RegisterRequest) -> User:
    """Register a new user."""
    # Check if username or email already exists
    result = await db.execute(
        select(User).where(
            or_(User.username == user_in.username, User.email == user_in.email)
        )
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        if existing_user.username == user_in.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    # Create new user
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        display_name=user_in.display_name or user_in.username,
        # For MVP, we'll auto-verify email or handle it loosely. 
        # In a real app, we'd send an email here.
        email_verified=False 
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user


async def authenticate_user(db: AsyncSession, login_in: LoginRequest) -> TokenResponse:
    """Authenticate a user and return tokens."""
    # Find user by username
    result = await db.execute(select(User).where(User.username == login_in.username))
    user = result.scalar_one_or_none()
    
    if not user:
        # Try email if username not found
        result = await db.execute(select(User).where(User.email == login_in.username))
        user = result.scalar_one_or_none()
        
    if not user or not verify_password(login_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )
