"""Game service with server-side validation and scoring."""
import random
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.game import GameSession, GameModeEnum
from app.models.country import Country, RegionEnum
from app.schemas.game import (
    GameCreate,
    Question,
    Option,
    AnswerSubmission,
    AnswerResult,
    GameSessionResponse
)
from app.services.country_service import CountryService


class GameService:
    """Service for game operations with server-side validation."""

    @staticmethod
    def _calculate_points(
        correct: bool,
        response_time_ms: int,
        streak: int
    ) -> int:
        """
        Calculate points for an answer according to PRD scoring system.

        Scoring Rules:
        - Correct answer: 100 base points
        - Speed bonus (< 5 seconds): +50 points
        - Speed bonus (< 10 seconds): +25 points
        - Streak bonus (3+ correct): +10 points per streak count
        - Incorrect answer: 0 points

        Args:
            correct: Whether answer was correct
            response_time_ms: Response time in milliseconds
            streak: Current streak count

        Returns:
            Points earned for this answer
        """
        if not correct:
            return 0

        points = 100  # Base points

        # Speed bonuses
        if response_time_ms < 5000:
            points += 50
        elif response_time_ms < 10000:
            points += 25

        # Streak bonus (3+ correct in a row)
        if streak >= 3:
            points += 10 * streak

        return points

    @staticmethod
    async def start_game(
        db: AsyncSession,
        user_id: UUID,
        game_in: GameCreate
    ) -> GameSession:
        """
        Start a new game session.

        Creates a game session with a randomized sequence of countries.
        Does not return questions - client must call get_current_question().

        Args:
            db: Database session
            user_id: ID of the user starting the game
            game_in: Game configuration

        Returns:
            Created GameSession

        Raises:
            HTTPException: If not enough countries available
        """
        # Fetch countries based on filters
        query = select(Country).where(Country.is_independent == True)

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
        countries = list(result.scalars().all())

        if len(countries) < game_in.questions_count:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough countries for selected criteria. Found {len(countries)}, need {game_in.questions_count}"
            )

        # Select random countries for the game
        selected_countries = random.sample(countries, game_in.questions_count)
        country_ids = [c.id for c in selected_countries]

        # Create game session
        game_session = GameSession(
            user_id=user_id,
            game_mode=GameModeEnum(game_in.game_mode),
            regions=game_in.regions,
            questions_count=game_in.questions_count,
            country_ids=country_ids,
            current_question_index=0,
            current_streak=0,
            is_complete=False,
            score=0,
            correct_count=0,
            answers=[]
        )

        db.add(game_session)
        await db.commit()
        await db.refresh(game_session)

        return game_session

    @staticmethod
    async def get_current_question(
        db: AsyncSession,
        game_id: UUID,
        user_id: UUID
    ) -> Question:
        """
        Get the current question for a game session.

        Args:
            db: Database session
            game_id: Game session ID
            user_id: User ID (for authorization)

        Returns:
            Question object with 4 multiple-choice options

        Raises:
            HTTPException: If game not found, unauthorized, or already complete
        """
        game = await db.get(GameSession, game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")

        if game.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        if game.is_complete:
            raise HTTPException(status_code=400, detail="Game already complete")

        if game.current_question_index >= len(game.country_ids):
            raise HTTPException(status_code=400, detail="No more questions")

        # Get the target country for this question
        target_country_id = game.country_ids[game.current_question_index]

        # Fetch all countries in the game's regions for generating distractors
        query = select(Country).where(Country.is_independent == True)
        if game.regions:
            region_enums = [RegionEnum(r.lower()) for r in game.regions]
            query = query.where(Country.region.in_(region_enums))

        result = await db.execute(query)
        all_countries = list(result.scalars().all())

        # Find target country
        target = next((c for c in all_countries if c.id == target_country_id), None)
        if not target:
            raise HTTPException(status_code=500, detail="Target country not found")

        # Generate 3 random distractors
        distractors = random.sample(
            [c for c in all_countries if c.id != target.id],
            min(3, len(all_countries) - 1)
        )

        # Create options and shuffle
        options_list = [target] + distractors
        random.shuffle(options_list)

        # Build question based on game mode
        question_text = ""
        image_url = None

        if game.game_mode == GameModeEnum.FLAG_TO_COUNTRY:
            question_text = "Which country does this flag belong to?"
            image_url = target.flag_url
            options = [
                Option(id=c.id, name=c.name, capital=c.capital or "")
                for c in options_list
            ]

        elif game.game_mode == GameModeEnum.COUNTRY_TO_CAPITAL:
            question_text = f"What is the capital of {target.name}?"
            image_url = target.flag_url  # Optional: show flag as hint
            options = [
                Option(id=c.id, name=c.capital or "", capital=c.capital or "")
                for c in options_list
            ]

        elif game.game_mode == GameModeEnum.CAPITAL_TO_COUNTRY:
            question_text = f"Which country has {target.capital} as its capital?"
            options = [
                Option(id=c.id, name=c.name, capital=c.capital or "")
                for c in options_list
            ]

        # Create question (DO NOT include correct answer in response)
        question = Question(
            id=f"{game_id}_{game.current_question_index}",
            text=question_text,
            image_url=image_url,
            options=options,
            correct_country_id=None  # Hidden from client
        )

        return question

    @staticmethod
    async def submit_answer(
        db: AsyncSession,
        game_id: UUID,
        user_id: UUID,
        answer: AnswerSubmission
    ) -> AnswerResult:
        """
        Submit an answer and get immediate feedback with points.

        This method:
        1. Validates the answer server-side
        2. Calculates points based on correctness, speed, and streak
        3. Updates game state (score, streak, question index)
        4. Returns result to client

        Args:
            db: Database session
            game_id: Game session ID
            user_id: User ID (for authorization)
            answer: Answer submission with option ID and response time

        Returns:
            AnswerResult with correctness, points, and streak

        Raises:
            HTTPException: If game not found, unauthorized, or invalid state
        """
        game = await db.get(GameSession, game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")

        if game.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        if game.is_complete:
            raise HTTPException(status_code=400, detail="Game already complete")

        if game.current_question_index >= len(game.country_ids):
            raise HTTPException(status_code=400, detail="No more questions")

        # Get correct country ID for current question
        correct_country_id = game.country_ids[game.current_question_index]

        # Check if answer is correct
        is_correct = answer.selected_option_id == correct_country_id

        # Update streak
        if is_correct:
            game.current_streak += 1
            game.correct_count += 1
        else:
            game.current_streak = 0

        # Update max streak
        if game.current_streak > game.max_streak:
            game.max_streak = game.current_streak

        # Calculate points
        points = GameService._calculate_points(
            correct=is_correct,
            response_time_ms=answer.response_time_ms,
            streak=game.current_streak
        )

        game.score += points

        # Record this answer
        answer_record = {
            "question_index": game.current_question_index,
            "country_id": correct_country_id,
            "selected_option_id": answer.selected_option_id,
            "correct": is_correct,
            "points": points,
            "response_time_ms": answer.response_time_ms,
            "streak": game.current_streak
        }

        # Update answers array
        current_answers = game.answers or []
        current_answers.append(answer_record)
        game.answers = current_answers

        # Move to next question
        game.current_question_index += 1

        # Check if game is complete
        if game.current_question_index >= game.questions_count:
            game.is_complete = True

            # Calculate average response time
            if current_answers:
                total_time = sum(a["response_time_ms"] for a in current_answers)
                game.avg_response_ms = total_time // len(current_answers)

        await db.commit()
        await db.refresh(game)

        # Return result
        return AnswerResult(
            correct=is_correct,
            correct_option_id=correct_country_id,
            points_earned=points,
            streak=game.current_streak
        )

    @staticmethod
    async def get_game_result(
        db: AsyncSession,
        game_id: UUID,
        user_id: UUID
    ) -> GameSessionResponse:
        """
        Get final results for a completed game.

        Args:
            db: Database session
            game_id: Game session ID
            user_id: User ID (for authorization)

        Returns:
            GameSessionResponse with all game statistics

        Raises:
            HTTPException: If game not found or unauthorized
        """
        game = await db.get(GameSession, game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")

        if game.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        return GameSessionResponse(
            id=game.id,
            game_mode=game.game_mode.value,
            regions=game.regions,
            score=game.score,
            questions_count=game.questions_count,
            correct_count=game.correct_count,
            avg_response_ms=game.avg_response_ms,
            max_streak=game.max_streak,
            played_at=game.played_at
        )

    @staticmethod
    async def get_game_history(
        db: AsyncSession,
        user_id: UUID,
        limit: int = 10,
        offset: int = 0
    ) -> List[GameSessionResponse]:
        """
        Get user's game history.

        Args:
            db: Database session
            user_id: User ID
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of completed game sessions, most recent first
        """
        query = (
            select(GameSession)
            .where(GameSession.user_id == user_id)
            .where(GameSession.is_complete == True)
            .order_by(GameSession.played_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await db.execute(query)
        games = result.scalars().all()

        return [
            GameSessionResponse(
                id=game.id,
                game_mode=game.game_mode.value,
                regions=game.regions,
                score=game.score,
                questions_count=game.questions_count,
                correct_count=game.correct_count,
                avg_response_ms=game.avg_response_ms,
                max_streak=game.max_streak,
                played_at=game.played_at
            )
            for game in games
        ]
