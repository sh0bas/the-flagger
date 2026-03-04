"""Country service for autocomplete and data retrieval."""

import unicodedata
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.country import Country, RegionEnum, DifficultyEnum, EntityTypeEnum


def normalize_str(s: str) -> str:
    """Strip diacritics and lowercase for comparison."""
    return (
        unicodedata.normalize("NFD", s)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
        .strip()
    )


class CountryService:
    """Service for country-related operations."""

    @staticmethod
    def _prioritize_matches(query: str, items: List[str]) -> List[str]:
        """
        Prioritize autocomplete matches.

        Priority Order:
        1. Exact match (case-insensitive, diacritic-normalized)
        2. Exact prefix match
        3. Word-boundary match
        4. Substring match
        """
        if not query:
            return items

        q = normalize_str(query)

        exact_matches = []
        prefix_matches = []
        word_boundary_matches = []
        substring_matches = []

        for item in items:
            item_norm = normalize_str(item)

            if item_norm == q:
                exact_matches.append(item)
            elif item_norm.startswith(q):
                prefix_matches.append(item)
            elif any(word.startswith(q) for word in item_norm.split()):
                word_boundary_matches.append(item)
            elif q in item_norm:
                substring_matches.append(item)

        return (
            sorted(exact_matches)
            + sorted(prefix_matches)
            + sorted(word_boundary_matches)
            + sorted(substring_matches)
        )

    @staticmethod
    async def get_all_countries(
        db: AsyncSession,
        regions: Optional[List[RegionEnum]] = None,
        only_independent: bool = True,
        difficulties: Optional[List[DifficultyEnum]] = None,
        entity_types: Optional[List[EntityTypeEnum]] = None,
    ) -> List[Country]:
        """Get all countries, optionally filtered."""
        query = select(Country)

        if only_independent and not entity_types:
            query = query.where(Country.is_independent == True)

        if regions:
            query = query.where(Country.region.in_(regions))

        if difficulties:
            query = query.where(Country.difficulty.in_(difficulties))

        if entity_types:
            query = query.where(Country.entity_type.in_(entity_types))

        query = query.order_by(Country.name)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_countries_autocomplete(
        db: AsyncSession,
        search: Optional[str] = None,
        regions: Optional[List[RegionEnum]] = None,
        only_independent: bool = True,
        difficulties: Optional[List[DifficultyEnum]] = None,
        entity_types: Optional[List[EntityTypeEnum]] = None,
        limit: int = 8,
    ) -> List[str]:
        """Get country names for autocomplete with smart prioritization."""
        countries = await CountryService.get_all_countries(
            db,
            regions=regions,
            only_independent=only_independent,
            difficulties=difficulties,
            entity_types=entity_types,
        )

        # Build a flat list of (display_name, match_target) pairs.
        # For each country, include the name itself plus all alt_names so that
        # abbreviation input (e.g. "USA") surfaces the canonical country name.
        candidates: List[str] = []
        seen: set[str] = set()
        for c in countries:
            if c.name not in seen:
                candidates.append(c.name)
                seen.add(c.name)

        if search and len(search) >= 1:
            # Also check alt_names for abbreviation/alias matches
            alias_hits: dict[str, str] = {}  # alias -> canonical name
            for c in countries:
                for alias in (c.alt_names or []):
                    alias_hits[alias] = c.name

            # Prioritize canonical names; if query matches an alias but not a
            # canonical name, bubble the canonical name to the top.
            q_norm = normalize_str(search)
            promoted: List[str] = []
            for alias, canon in alias_hits.items():
                if normalize_str(alias).startswith(q_norm) or normalize_str(alias) == q_norm:
                    if canon not in promoted:
                        promoted.append(canon)

            remaining = [c for c in candidates if c not in promoted]
            prioritized = promoted + CountryService._prioritize_matches(search, remaining)
            return prioritized[:limit]

        return candidates[:limit]

    @staticmethod
    async def get_capitals_autocomplete(
        db: AsyncSession,
        search: Optional[str] = None,
        regions: Optional[List[RegionEnum]] = None,
        only_independent: bool = True,
        limit: int = 8,
    ) -> List[str]:
        """Get capital names for autocomplete with smart prioritization."""
        countries = await CountryService.get_all_countries(
            db, regions=regions, only_independent=only_independent
        )

        capital_names = [c.capital for c in countries if c.capital]

        if search and len(search) >= 2:
            capital_names = CountryService._prioritize_matches(search, capital_names)

        return capital_names[:limit]

    @staticmethod
    async def get_country_by_name(db: AsyncSession, name: str) -> Optional[Country]:
        """Get a country by exact name match (case-insensitive)."""
        query = select(Country).where(Country.name.ilike(name))
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_country_by_capital(db: AsyncSession, capital: str) -> Optional[Country]:
        """Get a country by its capital (case-insensitive)."""
        query = select(Country).where(Country.capital.ilike(capital))
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def validate_answer(
        db: AsyncSession,
        country_id: int,
        user_answer: str,
        answer_type: str,
    ) -> bool:
        """Validate if user's answer is correct."""
        query = select(Country).where(Country.id == country_id)
        result = await db.execute(query)
        country = result.scalar_one_or_none()

        if not country:
            return False

        user_norm = normalize_str(user_answer)

        if answer_type == "country":
            if user_norm == normalize_str(country.name):
                return True
            return any(user_norm == normalize_str(alt) for alt in (country.alt_names or []))

        elif answer_type == "capital":
            if not country.capital:
                return False
            return user_norm == normalize_str(country.capital)

        return False
