"""Friend and friendship schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FriendRequest(BaseModel):
    """Friend request schema."""
    addressee_id: UUID


class FriendshipResponse(BaseModel):
    """Friendship response schema."""
    id: UUID
    requester_id: UUID
    addressee_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FriendProfile(BaseModel):
    """Friend profile schema."""
    id: UUID
    username: str
    display_name: str | None
    avatar_url: str | None
    friendship_since: datetime
    
    class Config:
        from_attributes = True
