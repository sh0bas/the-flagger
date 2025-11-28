"""Leaderboard schemas."""
from uuid import UUID

from pydantic import BaseModel


class LeaderboardEntry(BaseModel):
    """Leaderboard entry schema."""
    rank: int
    user_id: UUID
    username: str
    display_name: str | None
    avatar_url: str | None
    score: int
    games_played: int


class LeaderboardResponse(BaseModel):
    """Leaderboard response schema."""
    entries: list[LeaderboardEntry]
    total_count: int
    current_user_rank: int | None = None


class LeaderboardFilters(BaseModel):
    """Leaderboard filter schema."""
    mode: str
    period: str  # daily, weekly, monthly, all_time
    region: str | None = None
    friends_only: bool = False
