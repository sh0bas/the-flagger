"""User schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""
    username: str
    email: EmailStr
    display_name: str | None = None


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8)


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


class UserPublic(BaseModel):
    """Public user profile schema."""
    id: UUID
    username: str
    display_name: str | None
    avatar_url: str | None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserSearch(BaseModel):
    """User search result schema."""
    id: UUID
    username: str
    display_name: str | None
    avatar_url: str | None
    
    class Config:
        from_attributes = True
