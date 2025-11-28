"""User routes."""
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, UserPublic
from app.services.user_service import get_user_by_id, get_user_by_username, update_user, search_users

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(deps.get_current_user)]
):
    """Get current user profile."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_user_me(
    user_in: UserUpdate,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Update current user profile."""
    return await update_user(db, current_user.id, user_in)


@router.get("/search", response_model=List[UserPublic])
async def search_users_route(
    q: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
    limit: int = 10
):
    """Search users by username or display name."""
    if len(q) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 3 characters",
        )
    return await search_users(db, q, limit)


@router.get("/{username}", response_model=UserPublic)
async def read_user_by_username(
    username: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)]
):
    """Get public user profile by username."""
    user = await get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
