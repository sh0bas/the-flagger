"""Game routes with server-side validation."""
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.schemas.game import (
    GameCreate,
    GameSessionResponse,
    Question,
    AnswerSubmission,
    AnswerResult
)
from app.services.game_service import GameService

router = APIRouter()


@router.post("/start", response_model=GameSessionResponse)
async def start_new_game(
    game_in: GameCreate,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Start a new game session.

    Creates a game with randomized questions based on selected mode and regions.
    After starting, use GET /{game_id}/question to fetch questions one at a time.
    """
    session = await GameService.start_game(db, current_user.id, game_in)
    return GameSessionResponse(
        id=session.id,
        game_mode=session.game_mode.value,
        regions=session.regions,
        score=session.score,
        questions_count=session.questions_count,
        correct_count=session.correct_count,
        avg_response_ms=session.avg_response_ms,
        max_streak=session.max_streak,
        played_at=session.played_at
    )


@router.get("/{game_id}/question", response_model=Question)
async def get_current_question(
    game_id: UUID,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get the current question for a game session.

    Returns one question at a time with 4 multiple-choice options.
    The correct answer is NOT included in the response (validated server-side).
    """
    return await GameService.get_current_question(db, game_id, current_user.id)


@router.post("/{game_id}/answer", response_model=AnswerResult)
async def submit_answer(
    game_id: UUID,
    answer: AnswerSubmission,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Submit an answer for the current question.

    Server validates the answer, calculates points based on:
    - Correctness (100 base points)
    - Speed (< 5s: +50, < 10s: +25)
    - Streak (3+ correct: +10 per streak)

    Returns immediate feedback with correctness, points, and streak.
    Game automatically advances to next question.
    """
    return await GameService.submit_answer(db, game_id, current_user.id, answer)


@router.get("/{game_id}/result", response_model=GameSessionResponse)
async def get_game_result(
    game_id: UUID,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get final results for a completed game.

    Returns all game statistics including:
    - Total score
    - Correct answer count
    - Average response time
    - Maximum streak achieved
    """
    return await GameService.get_game_result(db, game_id, current_user.id)


@router.get("/history", response_model=List[GameSessionResponse])
async def get_game_history(
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(10, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Get user's game history.

    Returns list of completed games, most recent first.
    Supports pagination via limit and offset parameters.
    """
    return await GameService.get_game_history(
        db, current_user.id, limit=limit, offset=offset
    )
