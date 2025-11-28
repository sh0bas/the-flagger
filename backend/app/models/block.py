"""Block model."""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Block(Base):
    """Block model."""
    
    __tablename__ = "blocks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    blocker_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    blocked_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    blocker = relationship("User", foreign_keys=[blocker_id], back_populates="blocked_users")
    blocked = relationship("User", foreign_keys=[blocked_id], back_populates="blocked_by")
    
    # Ensure unique block pairs
    __table_args__ = (
        UniqueConstraint('blocker_id', 'blocked_id', name='unique_block'),
    )
