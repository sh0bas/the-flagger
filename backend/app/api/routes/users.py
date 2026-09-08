"""User routes."""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import update_user

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
