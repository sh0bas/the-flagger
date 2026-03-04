"""Country endpoints for autocomplete and catalog."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.country import RegionEnum, DifficultyEnum, EntityTypeEnum
from app.schemas.country import CountryResponse
from app.services.country_service import CountryService

router = APIRouter(prefix="/countries", tags=["countries"])


@router.get("/catalog", response_model=List[CountryResponse])
async def get_catalog(
    regions: Optional[List[RegionEnum]] = Query(None, description="Filter by regions"),
    difficulties: Optional[List[DifficultyEnum]] = Query(None, description="Filter by difficulty"),
    entity_types: Optional[List[EntityTypeEnum]] = Query(None, description="Filter by entity type"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get full flag catalog for client-side game logic.

    Returns complete country objects so the frontend can build its own
    game pool, shuffle, and run game modes without round-tripping for each question.
    """
    countries = await CountryService.get_all_countries(
        db=db,
        regions=regions,
        only_independent=False,
        difficulties=difficulties,
        entity_types=entity_types,
    )
    return countries


@router.get("", response_model=List[str])
async def get_countries(
    search: Optional[str] = Query(None, min_length=1, description="Search query"),
    regions: Optional[List[RegionEnum]] = Query(None, description="Filter by regions"),
    only_independent: bool = Query(True, description="Only independent countries"),
    difficulties: Optional[List[DifficultyEnum]] = Query(None, description="Filter by difficulty"),
    entity_types: Optional[List[EntityTypeEnum]] = Query(None, description="Filter by entity type"),
    limit: int = Query(8, ge=1, le=50, description="Maximum results"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get country names for autocomplete.

    Supports abbreviation matching (e.g. "USA" → "United States") and
    diacritic-insensitive matching (e.g. "Cote" → "Côte d'Ivoire").
    """
    return await CountryService.get_countries_autocomplete(
        db=db,
        search=search,
        regions=regions,
        only_independent=only_independent,
        difficulties=difficulties,
        entity_types=entity_types,
        limit=limit,
    )


@router.get("/capitals", response_model=List[str])
async def get_capitals(
    search: Optional[str] = Query(None, min_length=2, description="Search query"),
    regions: Optional[List[RegionEnum]] = Query(None, description="Filter by regions"),
    only_independent: bool = Query(True, description="Only independent countries"),
    limit: int = Query(8, ge=1, le=50, description="Maximum results"),
    db: AsyncSession = Depends(get_db),
):
    """Get capital city names for autocomplete."""
    return await CountryService.get_capitals_autocomplete(
        db=db,
        search=search,
        regions=regions,
        only_independent=only_independent,
        limit=limit,
    )
