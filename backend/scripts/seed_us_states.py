"""Seed US state entries into the countries table.

Each state uses iso_code = 'US-XX' (ISO 3166-2), entity_type = 'us_state',
region = 'americas', and a flagcdn.com flag URL.

Idempotent — skips states that already exist by iso_code.
Run inside the Docker container:
    docker-compose exec backend python scripts/seed_us_states.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal
from app.models.country import Country, RegionEnum, DifficultyEnum, EntityTypeEnum

# (name, iso_code, capital, difficulty)
# flag_url is derived as: https://flagcdn.com/w320/{iso_code.lower()}.png
US_STATES: list[tuple[str, str, str, str]] = [
    ("Alabama",        "US-AL", "Montgomery",    "hard"),
    ("Alaska",         "US-AK", "Juneau",        "medium"),
    ("Arizona",        "US-AZ", "Phoenix",       "medium"),
    ("Arkansas",       "US-AR", "Little Rock",   "hard"),
    ("California",     "US-CA", "Sacramento",    "easy"),
    ("Colorado",       "US-CO", "Denver",        "easy"),
    ("Connecticut",    "US-CT", "Hartford",      "hard"),
    ("Delaware",       "US-DE", "Dover",         "hard"),
    ("Florida",        "US-FL", "Tallahassee",   "medium"),
    ("Georgia",        "US-GA", "Atlanta",       "medium"),
    ("Hawaii",         "US-HI", "Honolulu",      "easy"),
    ("Idaho",          "US-ID", "Boise",         "hard"),
    ("Illinois",       "US-IL", "Springfield",   "hard"),
    ("Indiana",        "US-IN", "Indianapolis",  "medium"),
    ("Iowa",           "US-IA", "Des Moines",    "medium"),
    ("Kansas",         "US-KS", "Topeka",        "hard"),
    ("Kentucky",       "US-KY", "Frankfort",     "hard"),
    ("Louisiana",      "US-LA", "Baton Rouge",   "medium"),
    ("Maine",          "US-ME", "Augusta",       "hard"),
    ("Maryland",       "US-MD", "Annapolis",     "easy"),
    ("Massachusetts",  "US-MA", "Boston",        "hard"),
    ("Michigan",       "US-MI", "Lansing",       "hard"),
    ("Minnesota",      "US-MN", "Saint Paul",    "hard"),
    ("Mississippi",    "US-MS", "Jackson",       "medium"),
    ("Missouri",       "US-MO", "Jefferson City","medium"),
    ("Montana",        "US-MT", "Helena",        "hard"),
    ("Nebraska",       "US-NE", "Lincoln",       "hard"),
    ("Nevada",         "US-NV", "Carson City",   "medium"),
    ("New Hampshire",  "US-NH", "Concord",       "hard"),
    ("New Jersey",     "US-NJ", "Trenton",       "hard"),
    ("New Mexico",     "US-NM", "Santa Fe",      "easy"),
    ("New York",       "US-NY", "Albany",        "hard"),
    ("North Carolina", "US-NC", "Raleigh",       "medium"),
    ("North Dakota",   "US-ND", "Bismarck",      "hard"),
    ("Ohio",           "US-OH", "Columbus",      "easy"),
    ("Oklahoma",       "US-OK", "Oklahoma City", "medium"),
    ("Oregon",         "US-OR", "Salem",         "medium"),
    ("Pennsylvania",   "US-PA", "Harrisburg",    "hard"),
    ("Rhode Island",   "US-RI", "Providence",    "hard"),
    ("South Carolina", "US-SC", "Columbia",      "medium"),
    ("South Dakota",   "US-SD", "Pierre",        "hard"),
    ("Tennessee",      "US-TN", "Nashville",     "easy"),
    ("Texas",          "US-TX", "Austin",        "easy"),
    ("Utah",           "US-UT", "Salt Lake City","hard"),
    ("Vermont",        "US-VT", "Montpelier",    "hard"),
    ("Virginia",       "US-VA", "Richmond",      "hard"),
    ("Washington",     "US-WA", "Olympia",       "medium"),
    ("West Virginia",  "US-WV", "Charleston",    "medium"),
    ("Wisconsin",      "US-WI", "Madison",       "hard"),
    ("Wyoming",        "US-WY", "Cheyenne",      "medium"),
]


def flag_url(iso_code: str) -> str:
    return f"https://flagcdn.com/w320/{iso_code.lower()}.png"


async def seed_us_states():
    async with AsyncSessionLocal() as session:
        inserted = 0
        updated = 0
        for name, iso_code, capital, difficulty in US_STATES:
            result = await session.execute(
                select(Country).where(Country.iso_code == iso_code)
            )
            existing = result.scalar_one_or_none()
            if existing is not None:
                # Update flag_url in case it was previously set to Wikimedia
                if not existing.flag_url.startswith("https://flagcdn.com"):
                    existing.flag_url = flag_url(iso_code)
                    updated += 1
                continue

            state = Country(
                name=name,
                iso_code=iso_code,
                capital=capital,
                region=RegionEnum.AMERICAS,
                flag_url=flag_url(iso_code),
                is_independent=False,
                difficulty=DifficultyEnum(difficulty),
                entity_type=EntityTypeEnum.US_STATE,
                alt_names=[],
            )
            session.add(state)
            inserted += 1

        await session.commit()
        print(f"Done. Inserted {inserted} states, updated {updated} flag URLs.")


if __name__ == "__main__":
    asyncio.run(seed_us_states())
