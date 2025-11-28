"""User model."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """User account model."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(50), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    email_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    game_sessions = relationship("GameSession", back_populates="user", cascade="all, delete-orphan")
    sent_friend_requests = relationship(
        "Friendship",
        foreign_keys="Friendship.requester_id",
        back_populates="requester",
        cascade="all, delete-orphan"
    )
    received_friend_requests = relationship(
        "Friendship",
        foreign_keys="Friendship.addressee_id",
        back_populates="addressee",
        cascade="all, delete-orphan"
    )
    blocked_users = relationship(
        "Block",
        foreign_keys="Block.blocker_id",
        back_populates="blocker",
        cascade="all, delete-orphan"
    )
    blocked_by = relationship(
        "Block",
        foreign_keys="Block.blocked_id",
        back_populates="blocked",
        cascade="all, delete-orphan"
    )
