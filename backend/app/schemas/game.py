"""Game-related schemas."""
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class GameSessionResponse(BaseModel):
    """Game session response schema."""
    id: UUID
    game_mode: str
    regions: list[str]
    score: int
    questions_count: int
    correct_count: int
    avg_response_ms: int
    max_streak: int
    played_at: datetime

    class Config:
        from_attributes = True


class FlagQuizAnswer(BaseModel):
    """One answer as the player gave it. Correctness is decided server-side."""
    country_id: int
    user_answer: str = Field(..., max_length=100)
    response_ms: int = Field(..., ge=0, le=600_000)


class FlagQuizResult(BaseModel):
    """A completed client-side flag quiz.

    Deliberately carries no score, correct_count, questions_count, max_streak or
    avg_response_ms: the server derives all of them from `answers`. There is no
    client-supplied number here to validate, so there is no way to inflate one.
    """
    game_mode: Literal['practice', 'endless', 'gauntlet']
    regions: list[str] = Field(default_factory=list)
    entity_types: list[str] = Field(default_factory=list)
    difficulties: list[str] = Field(default_factory=list)
    answers: list[FlagQuizAnswer] = Field(default_factory=list, max_length=1000)
