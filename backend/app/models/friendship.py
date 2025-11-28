"""Friendship model."""
import uuid
from datetime import datetime
import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class FriendshipStatus(str, enum.Enum):
    """Friendship status enumeration."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class Friendship(Base):
    """Friendship model."""
    
    __tablename__ = "friendships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requester_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    addressee_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(FriendshipStatus, values_callable=lambda obj: [e.value for e in obj]), default=FriendshipStatus.PENDING, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    requester = relationship("User", foreign_keys=[requester_id], back_populates="sent_friend_requests")
    addressee = relationship("User", foreign_keys=[addressee_id], back_populates="received_friend_requests")
    
    # Ensure unique friendship pairs
    __table_args__ = (
        UniqueConstraint('requester_id', 'addressee_id', name='unique_friendship'),
    )
