"""Country endpoints for autocomplete."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.country import RegionEnum
from app.services.country_service import CountryService

router = APIRouter(prefix="/countries", tags=["countries"])


@router.get("", response_model=List[str])
async def get_countries(
    search: Optional[str] = Query(None, min_length=2, description="Search query"),
    regions: Optional[List[RegionEnum]] = Query(None, description="Filter by regions"),
    only_independent: bool = Query(True, description="Only independent countries"),
    limit: int = Query(8, ge=1, le=50, description="Maximum results"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get country names for autocomplete.

    Implements smart prioritization:
    1. Exact match
    2. Exact prefix match
    3. Word-boundary match
    4. Substring match
    """
    return await CountryService.get_countries_autocomplete(
        db=db,
        search=search,
        regions=regions,
        only_independent=only_independent,
        limit=limit
    )


@router.get("/capitals", response_model=List[str])
async def get_capitals(
    search: Optional[str] = Query(None, min_length=2, description="Search query"),
    regions: Optional[List[RegionEnum]] = Query(None, description="Filter by regions"),
    only_independent: bool = Query(True, description="Only independent countries"),
    limit: int = Query(8, ge=1, le=50, description="Maximum results"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get capital city names for autocomplete.

    Implements smart prioritization:
    1. Exact match
    2. Exact prefix match
    3. Word-boundary match
    4. Substring match
    """
    return await CountryService.get_capitals_autocomplete(
        db=db,
        search=search,
        regions=regions,
        only_independent=only_independent,
        limit=limit
    )
