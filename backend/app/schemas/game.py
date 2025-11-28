"""Game-related schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class GameCreate(BaseModel):
    """Game creation schema."""
    game_mode: str = Field(..., pattern=r'^(flag_to_country|country_to_capital|capital_to_country)$')
    regions: list[str] = Field(default_factory=list)
    questions_count: int = Field(default=20, ge=5, le=50)


class Option(BaseModel):
    """Answer option schema."""
    id: int
    name: str
    capital: str


class Question(BaseModel):
    """Question schema."""
    id: str
    text: str
    image_url: str | None = None
    options: list[Option]
    correct_country_id: int | None = None  # Optional, for debugging or if client validates


class AnswerSubmission(BaseModel):
    """Answer submission schema."""
    question_id: str
    selected_option_id: int
    response_time_ms: int = Field(..., ge=0)


class AnswerResult(BaseModel):
    """Answer result schema."""
    correct: bool
    correct_option_id: int
    points_earned: int
    streak: int


class GameResult(BaseModel):
    """Game result submission schema."""
    score: int
    correct_count: int
    avg_response_ms: int
    max_streak: int


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
