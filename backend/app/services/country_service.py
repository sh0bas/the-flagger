"""Country service for autocomplete and data retrieval."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.country import Country, RegionEnum


class CountryService:
    """Service for country-related operations."""

    @staticmethod
    def _prioritize_matches(query: str, items: List[str]) -> List[str]:
        """
        Prioritize autocomplete matches according to PRD specification.

        Priority Order:
        1. Exact match (case-insensitive)
        2. Exact prefix match
        3. Word-boundary match
        4. Substring match

        Args:
            query: User's input query
            items: List of country/capital names to match against

        Returns:
            Sorted list with highest priority matches first
        """
        if not query:
            return items

        query_lower = query.lower()

        exact_matches = []
        prefix_matches = []
        word_boundary_matches = []
        substring_matches = []

        for item in items:
            item_lower = item.lower()

            # 1. Exact match
            if item_lower == query_lower:
                exact_matches.append(item)
            # 2. Exact prefix match
            elif item_lower.startswith(query_lower):
                prefix_matches.append(item)
            # 3. Word-boundary match (query matches start of any word)
            elif any(word.startswith(query_lower) for word in item_lower.split()):
                word_boundary_matches.append(item)
            # 4. Substring match
            elif query_lower in item_lower:
                substring_matches.append(item)

        # Combine in priority order (each group is alphabetically sorted)
        return (
            sorted(exact_matches) +
            sorted(prefix_matches) +
            sorted(word_boundary_matches) +
            sorted(substring_matches)
        )

    @staticmethod
    async def get_all_countries(
        db: AsyncSession,
        regions: Optional[List[RegionEnum]] = None,
        only_independent: bool = True
    ) -> List[Country]:
        """
        Get all countries, optionally filtered by region.

        Args:
            db: Database session
            regions: List of regions to filter by (None = all regions)
            only_independent: If True, only return independent countries

        Returns:
            List of Country objects
        """
        query = select(Country)

        if only_independent:
            query = query.where(Country.is_independent == True)

        if regions:
            query = query.where(Country.region.in_(regions))

        query = query.order_by(Country.name)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_countries_autocomplete(
        db: AsyncSession,
        search: Optional[str] = None,
        regions: Optional[List[RegionEnum]] = None,
        only_independent: bool = True,
        limit: int = 8
    ) -> List[str]:
        """
        Get country names for autocomplete with smart prioritization.

        Args:
            db: Database session
            search: Search query for filtering
            regions: List of regions to filter by
            only_independent: If True, only return independent countries
            limit: Maximum number of results

        Returns:
            List of country names, prioritized by match quality
        """
        countries = await CountryService.get_all_countries(
            db, regions=regions, only_independent=only_independent
        )

        country_names = [c.name for c in countries]

        if search and len(search) >= 2:
            # Apply prioritization algorithm
            country_names = CountryService._prioritize_matches(search, country_names)

        return country_names[:limit]

    @staticmethod
    async def get_capitals_autocomplete(
        db: AsyncSession,
        search: Optional[str] = None,
        regions: Optional[List[RegionEnum]] = None,
        only_independent: bool = True,
        limit: int = 8
    ) -> List[str]:
        """
        Get capital names for autocomplete with smart prioritization.

        Args:
            db: Database session
            search: Search query for filtering
            regions: List of regions to filter by
            only_independent: If True, only return independent countries
            limit: Maximum number of results

        Returns:
            List of capital names, prioritized by match quality
        """
        countries = await CountryService.get_all_countries(
            db, regions=regions, only_independent=only_independent
        )

        capital_names = [c.capital for c in countries if c.capital]

        if search and len(search) >= 2:
            # Apply prioritization algorithm
            capital_names = CountryService._prioritize_matches(search, capital_names)

        return capital_names[:limit]

    @staticmethod
    async def get_country_by_name(
        db: AsyncSession,
        name: str
    ) -> Optional[Country]:
        """
        Get a country by exact name match (case-insensitive).

        Args:
            db: Database session
            name: Country name

        Returns:
            Country object or None
        """
        query = select(Country).where(Country.name.ilike(name))
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_country_by_capital(
        db: AsyncSession,
        capital: str
    ) -> Optional[Country]:
        """
        Get a country by its capital (case-insensitive).

        Args:
            db: Database session
            capital: Capital city name

        Returns:
            Country object or None
        """
        query = select(Country).where(Country.capital.ilike(capital))
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def validate_answer(
        db: AsyncSession,
        country_id: int,
        user_answer: str,
        answer_type: str  # "country" or "capital"
    ) -> bool:
        """
        Validate if user's answer is correct.

        Args:
            db: Database session
            country_id: ID of the country in question
            user_answer: User's submitted answer
            answer_type: Whether answer should be "country" or "capital"

        Returns:
            True if answer is correct, False otherwise
        """
        query = select(Country).where(Country.id == country_id)
        result = await db.execute(query)
        country = result.scalar_one_or_none()

        if not country:
            return False

        user_answer_lower = user_answer.strip().lower()

        if answer_type == "country":
            correct_answer = country.name.lower()
            # Also check alternative names
            alt_names = [alt.lower() for alt in (country.alt_names or [])]
            return user_answer_lower == correct_answer or user_answer_lower in alt_names

        elif answer_type == "capital":
            if not country.capital:
                return False
            return user_answer_lower == country.capital.lower()

        return False
