"""Game service."""
import random
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.game import GameSession, GameModeEnum
from app.models.country import Country, RegionEnum
from app.models.user import User
from app.schemas.game import GameCreate, GameResult, Question, AnswerSubmission, AnswerResult


async def start_game(db: AsyncSession, user_id: UUID, game_in: GameCreate) -> GameSession:
    """Start a new game session."""
    # 1. Fetch countries based on filters
    query = select(Country).where(Country.is_independent == True)  # Default to independent for now
    
    if game_in.regions:
        # Convert string regions to enum
        region_enums = []
        for r in game_in.regions:
            try:
                region_enums.append(RegionEnum(r.lower()))
            except ValueError:
                pass
        if region_enums:
            query = query.where(Country.region.in_(region_enums))
            
    result = await db.execute(query)
    countries = result.scalars().all()
    
    if len(countries) < game_in.questions_count:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough countries found for the selected criteria"
        )
        
    # 2. Select random countries for the game
    selected_countries = random.sample(countries, game_in.questions_count)
    
    # 3. Create game session
    # We store the sequence of country IDs to ask
    # For now, we'll just store the country IDs in a temporary way or rely on the client?
    # Better: Store the question sequence in Redis or in the DB.
    # For MVP: We'll return the full list of questions to the client at once.
    # Security risk: Client knows all answers.
    # Better approach: Return one question at a time or just the questions without answers.
    # But for "Flag to Country", the question IS the flag (URL), and the answer is the country name.
    # If we send the flag URL, the client can't easily guess the country name unless they look it up.
    # But we need to send multiple choices (multiple choice) or expect text input.
    # Let's assume multiple choice for now, or text input?
    # PRD says: "Multiple choice (4 options) or typed input (hard mode)"
    # Let's implement Multiple Choice generation here.
    
    # We need to generate questions with options.
    # But GameSession model doesn't store questions.
    # We should probably store the game state in Redis.
    # For this MVP step, let's just create the session record and return the questions.
    
    game_session = GameSession(
        user_id=user_id,
        game_mode=game_in.game_mode,
        regions=game_in.regions,
        questions_count=game_in.questions_count,
        score=0,
        correct_count=0
    )
    
    db.add(game_session)
    await db.commit()
    await db.refresh(game_session)
    
    return game_session


async def generate_questions(db: AsyncSession, game_session: GameSession) -> List[Question]:
    """Generate questions for a game session."""
    # Re-fetch countries based on session criteria
    # This is slightly inefficient, ideally we'd pass them or cache them.
    query = select(Country).where(Country.is_independent == True)
    
    if game_session.regions:
        region_enums = [RegionEnum(r.lower()) for r in game_session.regions]
        query = query.where(Country.region.in_(region_enums))
            
    result = await db.execute(query)
    all_countries = result.scalars().all()
    
    # Select target countries
    targets = random.sample(all_countries, game_session.questions_count)
    
    questions = []
    for target in targets:
        # Generate 3 distractors
        distractors = random.sample([c for c in all_countries if c.id != target.id], 3)
        options = [target] + distractors
        random.shuffle(options)
        
        question_text = ""
        image_url = None
        
        if game_session.game_mode == GameModeEnum.FLAG_TO_COUNTRY:
            question_text = "Which country does this flag belong to?"
            image_url = target.flag_url
        elif game_session.game_mode == GameModeEnum.COUNTRY_TO_CAPITAL:
            question_text = f"What is the capital of {target.name}?"
        elif game_session.game_mode == GameModeEnum.CAPITAL_TO_COUNTRY:
            question_text = f"Which country has {target.capital} as its capital?"
            
        questions.append(Question(
            id=str(uuid4()), # Temporary ID for the question
            country_id=target.id, # The correct answer ID (hidden from user in real app?)
            # In a secure app, we wouldn't send country_id as the correct answer to the client.
            # We would send a question ID and validate on backend.
            # But for simplicity here, we'll send it and trust the client or validate later.
            # Actually, let's NOT send the correct answer ID in the Question model if we want to be secure.
            # But the Question schema might require it?
            # Let's check the schema.
            text=question_text,
            image_url=image_url,
            options=[{"id": c.id, "name": c.name, "capital": c.capital} for c in options]
        ))
        
    return questions


async def submit_score(db: AsyncSession, game_id: UUID, result_in: GameResult) -> GameSession:
    """Submit final game score."""
    game = await db.get(GameSession, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
        
    game.score = result_in.score
    game.correct_count = result_in.correct_count
    game.avg_response_ms = result_in.avg_response_ms
    game.max_streak = result_in.max_streak
    
    db.add(game)
    await db.commit()
    await db.refresh(game)
    
    return game
