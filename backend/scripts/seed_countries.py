"""Country data seeding script.

Fetches country data from REST Countries API and populates the database.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.country import Country, RegionEnum, EntityTypeEnum


# Map REST Countries regions/subregions to our simplified regions
REGION_MAPPING = {
    "Americas": RegionEnum.AMERICAS,
    "Antarctic": RegionEnum.OCEANIA,  # Group with Oceania
    "Africa": RegionEnum.AFRICA,
    "Asia": RegionEnum.ASIA,
    "Europe": RegionEnum.EUROPE,
    "Oceania": RegionEnum.OCEANIA,
}


async def fetch_countries():
    """Fetch country data.

    restcountries.com v3.1 was sunset and v5 now requires a paid API key, so
    this pulls the same shape (name/capital/region/cca2/altSpellings/
    independent/status) from mledoze/countries, a static MIT-licensed mirror.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://raw.githubusercontent.com/mledoze/countries/master/countries.json"
        )
        response.raise_for_status()
        return response.json()



async def seed_countries():
    """Seed the countries table with data."""
    print("Fetching country data from REST Countries API...")
    countries_data = await fetch_countries()
    
    async with AsyncSessionLocal() as session:
        # Check if countries already exist (US states may already be seeded separately)
        result = await session.execute(
            select(Country).where(Country.entity_type == EntityTypeEnum.SOVEREIGN_STATE)
        )
        existing = result.scalars().first()
        
        if existing:
            print("Countries already seeded. Skipping...")
            return
        
        print(f"Seeding {len(countries_data)} countries...")
        
        created_count = 0
        for country_data in countries_data:
            # Skip countries without capitals or invalid regions
            if not country_data.get("capital") or not country_data.get("region"):
                continue
            
            region_name = country_data["region"]
            if region_name not in REGION_MAPPING:
                continue
            
            # Track whether this is an independent/sovereign state
            is_independent = country_data.get("independent", False)
            
            # Get common name
            name = country_data["name"]["common"]
            capital = country_data["capital"][0]  # Take first capital
            iso_code = country_data["cca2"]
            
            # Get alternative names
            alt_names = country_data.get("altSpellings", [])
            # Add official name if different from common
            official = country_data["name"].get("official")
            if official and official != name:
                alt_names.append(official)
            
            # Create flag URL
            flag_url = f"https://flagcdn.com/w320/{iso_code.lower()}.png"
            
            # Create country record
            country = Country(
                name=name,
                capital=capital,
                region=REGION_MAPPING[region_name],
                flag_url=flag_url,
                iso_code=iso_code,
                alt_names=alt_names[:5],  # Limit to 5 alternative names
                is_independent=is_independent,
                entity_type=EntityTypeEnum.SOVEREIGN_STATE if is_independent else EntityTypeEnum.TERRITORY,
            )
            
            session.add(country)
            created_count += 1
        
        await session.commit()
        print(f"Successfully seeded {created_count} countries!")


if __name__ == "__main__":
    asyncio.run(seed_countries())
