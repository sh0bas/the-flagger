"""Update existing countries with correct is_independent values.

Fetches fresh data from REST Countries API and updates is_independent field.
"""
import asyncio
import httpx
from sqlalchemy import select, update

from app.core.database import AsyncSessionLocal
from app.models.country import Country


async def update_independence_status():
    """Update is_independent field for existing countries."""
    print("Fetching country data from REST Countries API...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://restcountries.com/v3.1/all",
            params={"fields": "cca2,independent"}
        )
        response.raise_for_status()
        countries_data = response.json()
    
    # Create a mapping of ISO code -> independence status
    independence_map = {}
    for country_data in countries_data:
        iso_code = country_data.get("cca2")
        is_independent = country_data.get("independent", False)
        if iso_code:
            independence_map[iso_code] = is_independent
    
    print(f"Fetched {len(independence_map)} countries from API")
    
    async with AsyncSessionLocal() as session:
        # Get all countries
        result = await session.execute(select(Country))
        countries = result.scalars().all()
        
        updated_count = 0
        sovereign_count = 0
        territory_count = 0
        
        for country in countries:
            if country.iso_code in independence_map:
                new_status = independence_map[country.iso_code]
                if country.is_independent != new_status:
                    country.is_independent = new_status
                    updated_count += 1
                
                if new_status:
                    sovereign_count += 1
                else:
                    territory_count += 1
        
        await session.commit()
        
        print(f"Updated {updated_count} countries")
        print(f"Total: {len(countries)} countries")
        print(f"  - Sovereign states: {sovereign_count}")
        print(f"  - Territories/Dependencies: {territory_count}")


if __name__ == "__main__":
    asyncio.run(update_independence_status())
