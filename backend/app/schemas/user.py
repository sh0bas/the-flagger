"""User schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""
    username: str
    email: EmailStr
    display_name: str | None = None


class UserUpdate(BaseModel):
    """User update schema."""
    display_name: str | None = Field(None, max_length=50)
    avatar_url: str | None = Field(None, max_length=500)


class UserResponse(UserBase):
    """User response schema."""
    id: UUID
    avatar_url: str | None
    email_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
