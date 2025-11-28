"""Game routes."""
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.schemas.game import GameCreate, GameSessionResponse, Question, GameResult
from app.services.game_service import start_game, generate_questions, submit_score

router = APIRouter()


@router.post("/start", response_model=GameSessionResponse)
async def start_new_game(
    game_in: GameCreate,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Start a new game session."""
    return await start_game(db, current_user.id, game_in)


@router.get("/{game_id}/questions", response_model=List[Question])
async def get_game_questions(
    game_id: UUID,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get questions for a game session."""
    # We need to fetch the game session first to know the settings
    from app.models.game import GameSession
    game = await db.get(GameSession, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    return await generate_questions(db, game)


@router.post("/{game_id}/end", response_model=GameSessionResponse)
async def end_game(
    game_id: UUID,
    result_in: GameResult,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """End game and submit results."""
    # Verify ownership
    from app.models.game import GameSession
    game = await db.get(GameSession, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    return await submit_score(db, game_id, result_in)
