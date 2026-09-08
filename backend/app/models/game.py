"""Game session model."""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, ARRAY, String, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class GameSession(Base):
    """Game session model."""
    
    __tablename__ = "game_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    # Plain text: the allowed set is enforced by FlagQuizResult, at the trust
    # boundary. A DB enum only bought migrations every time a mode was added.
    game_mode = Column(String(20), nullable=False, index=True)
    regions = Column(ARRAY(String), nullable=False, default=list)
    entity_types = Column(ARRAY(String), nullable=False, default=list)
    difficulties = Column(ARRAY(String), nullable=False, default=list)

    # Game state
    country_ids = Column(ARRAY(Integer), nullable=False, default=list)  # Sequence of country IDs for questions
    current_question_index = Column(Integer, nullable=False, default=0)
    current_streak = Column(Integer, nullable=False, default=0)
    is_complete = Column(Boolean, nullable=False, default=False)

    # Final results
    score = Column(Integer, nullable=False, default=0)
    questions_count = Column(Integer, nullable=False, default=20)
    correct_count = Column(Integer, nullable=False, default=0)
    avg_response_ms = Column(Integer, nullable=False, default=0)
    max_streak = Column(Integer, nullable=False, default=0)

    # Detailed answer tracking (for statistics/review)
    answers = Column(JSONB, nullable=False, default=list)  # List of {question_idx, country_id, correct, points, response_ms}

    played_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationship
    user = relationship("User", back_populates="game_sessions")
