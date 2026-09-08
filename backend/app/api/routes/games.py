"""Game routes.

Scoring is authoritative here. The client sends what the player typed and how
long they took; every derived number — correctness, score, streak, averages —
is recomputed server-side, so there is nothing for a tampered payload to inflate.
"""
import uuid
from datetime import datetime
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.database import get_db
from app.models.country import Country
from app.models.game import GameSession
from app.models.user import User
from app.schemas.game import FlagQuizResult, GameSessionResponse
from app.services.country_service import normalize_str

router = APIRouter()

# Kept in sync by hand with calcScore() in frontend/src/hooks/useQuizReducer.ts,
# which is display-only. This copy is the one that counts.
FAST_MS = 5_000
MEDIUM_MS = 10_000
STREAK_THRESHOLD = 3


def _points(response_ms: int, streak: int) -> int:
    """Points for one correct answer. Streak is the count *including* this answer."""
    points = 100
    if response_ms < FAST_MS:
        points += 50
    elif response_ms < MEDIUM_MS:
        points += 25
    if streak >= STREAK_THRESHOLD:
        points += 10 * streak
    return points


def grade(answers, names_by_id: dict[int, list[str]]) -> dict:
    """Derive every stat from the raw answers.

    Pure so it can be tested without a database — this is the path that stops a
    tampered payload from claiming an arbitrary score.
    """
    score = streak = max_streak = correct_count = 0
    graded = []

    for a in answers:
        answer_norm = normalize_str(a.user_answer)
        correct = any(
            answer_norm == normalize_str(name)
            for name in names_by_id.get(a.country_id, ())
        )

        if correct:
            streak += 1
            max_streak = max(max_streak, streak)
            correct_count += 1
            score += _points(a.response_ms, streak)
        else:
            streak = 0

        graded.append({
            "country_id": a.country_id,
            "user_answer": a.user_answer,
            "correct": correct,
            "response_ms": a.response_ms,
        })

    return {
        "score": score,
        "correct_count": correct_count,
        "max_streak": max_streak,
        "questions_count": len(answers),
        "avg_response_ms": (
            round(sum(a.response_ms for a in answers) / len(answers)) if answers else 0
        ),
        "answers": graded,
    }


def _to_response(session: GameSession) -> GameSessionResponse:
    return GameSessionResponse(
        id=session.id,
        game_mode=session.game_mode,
        regions=session.regions,
        score=session.score,
        questions_count=session.questions_count,
        correct_count=session.correct_count,
        avg_response_ms=session.avg_response_ms,
        max_streak=session.max_streak,
        played_at=session.played_at,
    )


@router.post("/save-result", response_model=GameSessionResponse)
async def save_flag_quiz_result(
    result: FlagQuizResult,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Save a completed client-side flag quiz, grading it server-side."""
    # One query for every country referenced, not one per answer: a full gauntlet
    # is ~290 answers, and per-answer lookups would be 290 sequential round trips.
    ids = {a.country_id for a in result.answers}
    names_by_id: dict[int, list[str]] = {}
    if ids:
        rows = await db.execute(select(Country).where(Country.id.in_(ids)))
        names_by_id = {
            c.id: [c.name, *(c.alt_names or [])] for c in rows.scalars().all()
        }

    stats = grade(result.answers, names_by_id)

    session = GameSession(
        id=uuid.uuid4(),
        user_id=current_user.id,
        game_mode=result.game_mode,
        regions=result.regions,
        country_ids=[a.country_id for a in result.answers],
        score=stats["score"],
        questions_count=stats["questions_count"],
        correct_count=stats["correct_count"],
        avg_response_ms=stats["avg_response_ms"],
        max_streak=stats["max_streak"],
        is_complete=True,
        answers=stats["answers"],
        played_at=datetime.utcnow(),
    )
    db.add(session)
    await db.commit()

    return _to_response(session)


@router.get("/history", response_model=List[GameSessionResponse])
async def get_game_history(
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(10, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """The user's completed games, most recent first."""
    rows = await db.execute(
        select(GameSession)
        .where(GameSession.user_id == current_user.id)
        .where(GameSession.is_complete.is_(True))
        .order_by(GameSession.played_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return [_to_response(g) for g in rows.scalars().all()]
