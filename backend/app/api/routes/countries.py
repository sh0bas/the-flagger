"""Country catalog endpoint."""

from typing import List

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.country import Country
from app.schemas.country import CountryResponse

router = APIRouter(prefix="/countries", tags=["countries"])

# Populated on first request, kept for the life of the process. Countries only
# change when a seed script is re-run (outside this process), so there's no
# invalidation to do - a restart is what picks up a re-seed.
_catalog_cache: List[CountryResponse] | None = None


@router.get("/catalog", response_model=List[CountryResponse])
async def get_catalog(response: Response, db: AsyncSession = Depends(get_db)):
    """Full flag catalog.

    The client builds its own pool, shuffles, and runs every game mode from this
    one payload — including autocomplete, which is why there is no suggestion
    endpoint. ~290 rows that only change when a seed script is re-run, so it
    caches hard, in-process as well as via the Cache-Control header below.
    """
    response.headers["Cache-Control"] = "public, max-age=3600"

    global _catalog_cache
    if _catalog_cache is None:
        rows = await db.execute(select(Country).order_by(Country.name))
        _catalog_cache = [CountryResponse.model_validate(c) for c in rows.scalars().all()]
    return _catalog_cache
