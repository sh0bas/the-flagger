"""User service."""
from typing import Optional, List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, or_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserUpdate


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, user_id: UUID, user_in: UserUpdate) -> User:
    """Update user profile."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
        
    # Update fields
    update_data = user_in.model_dump(exclude_unset=True)
    
    # If updating email, check uniqueness
    if "email" in update_data and update_data["email"] != user.email:
        result = await db.execute(select(User).where(User.email == update_data["email"]))
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
            
    for field, value in update_data.items():
        setattr(user, field, value)
        
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user
