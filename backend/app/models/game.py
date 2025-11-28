"""Game session model."""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, ARRAY, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class GameModeEnum(str, enum.Enum):
    """Game mode enumeration."""
    FLAG_TO_COUNTRY = "flag_to_country"
    COUNTRY_TO_CAPITAL = "country_to_capital"
    CAPITAL_TO_COUNTRY = "capital_to_country"


class GameSession(Base):
    """Game session model."""
    
    __tablename__ = "game_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    game_mode = Column(Enum(GameModeEnum, values_callable=lambda obj: [e.value for e in obj]), nullable=False, index=True)
    regions = Column(ARRAY(String), nullable=False, default=list)
    score = Column(Integer, nullable=False, default=0)
    questions_count = Column(Integer, nullable=False, default=20)
    correct_count = Column(Integer, nullable=False, default=0)
    avg_response_ms = Column(Integer, nullable=False, default=0)
    max_streak = Column(Integer, nullable=False, default=0)
    played_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationship
    user = relationship("User", back_populates="game_sessions")
