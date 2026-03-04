"""Seed difficulty classifications and abbreviation aliases for countries.

Run this after the 004 migration. Idempotent — safe to run multiple times.
"""
import asyncio
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.models.country import Country, DifficultyEnum


# Well-known, highly distinct flags — easy to recognise
EASY_COUNTRIES = {
    "United States",
    "United Kingdom",
    "France",
    "Germany",
    "Japan",
    "Brazil",
    "Canada",
    "Australia",
    "China",
    "India",
    "Italy",
    "Spain",
    "Mexico",
    "Russia",
    "South Africa",
    "Argentina",
    "Sweden",
    "Norway",
    "Denmark",
    "Switzerland",
    "Portugal",
    "Netherlands",
    "Belgium",
    "Greece",
    "Turkey",
    "Saudi Arabia",
    "Israel",
    "South Korea",
    "Indonesia",
    "Pakistan",
    "Nigeria",
    "Egypt",
    "Kenya",
    "Ghana",
    "Jamaica",
    "Cuba",
    "New Zealand",
    "Ireland",
    "Poland",
    "Ukraine",
    "Finland",
    "Austria",
    "Czech Republic",
    "Hungary",
    "Romania",
    "Colombia",
    "Chile",
    "Peru",
    "Venezuela",
    "Thailand",
    "Vietnam",
    "Philippines",
    "Malaysia",
    "Singapore",
    "Bangladesh",
    "Nepal",
    "Sri Lanka",
    "Morocco",
    "Algeria",
    "Ethiopia",
    "Tanzania",
    "Zimbabwe",
    "Cameroon",
}

# Obscure territories, visually similar, or very small nations — hard
HARD_COUNTRIES = {
    "Tuvalu",
    "Nauru",
    "Kiribati",
    "Palau",
    "Marshall Islands",
    "Micronesia",
    "Tonga",
    "Samoa",
    "Vanuatu",
    "Solomon Islands",
    "Comoros",
    "São Tomé and Príncipe",
    "Cabo Verde",
    "Equatorial Guinea",
    "Gabon",
    "Republic of the Congo",
    "Democratic Republic of the Congo",
    "Central African Republic",
    "Chad",
    "Eritrea",
    "Djibouti",
    "Burundi",
    "Rwanda",
    "Malawi",
    "Zambia",
    "Mozambique",
    "Lesotho",
    "Eswatini",
    "Mauritania",
    "Guinea-Bissau",
    "Sierra Leone",
    "Liberia",
    "Togo",
    "Benin",
    "Burkina Faso",
    "Niger",
    "Mali",
    "Gambia",
    "Guinea",
    "Tajikistan",
    "Turkmenistan",
    "Kyrgyzstan",
    "Uzbekistan",
    "Kazakhstan",
    "Azerbaijan",
    "Armenia",
    "Georgia",
    "Moldova",
    "Belarus",
    "Montenegro",
    "North Macedonia",
    "Kosovo",
    "San Marino",
    "Liechtenstein",
    "Andorra",
    "Monaco",
    "Maldives",
    "Bhutan",
    "Timor-Leste",
    "Papua New Guinea",
    "Guyana",
    "Suriname",
    "Belize",
    "Haiti",
    "Trinidad and Tobago",
}

# Abbreviation aliases to add to alt_names
ABBREVIATION_ALIASES: dict[str, list[str]] = {
    "United States": ["USA", "US", "United States of America"],
    "United Kingdom": ["UK", "Great Britain", "Britain"],
    "United Arab Emirates": ["UAE"],
    "Democratic Republic of the Congo": ["DRC", "DR Congo", "Congo-Kinshasa"],
    "Central African Republic": ["CAR"],
    "Papua New Guinea": ["PNG"],
    "Republic of the Congo": ["Congo-Brazzaville"],
    "Bosnia and Herzegovina": ["Bosnia", "BiH"],
    "Trinidad and Tobago": ["T&T"],
    "Saint Kitts and Nevis": ["St Kitts"],
    "Saint Vincent and the Grenadines": ["St Vincent"],
    "Saint Lucia": ["St Lucia"],
    "Antigua and Barbuda": ["Antigua"],
    "São Tomé and Príncipe": ["Sao Tome", "Sao Tome and Principe"],
    "Côte d'Ivoire": ["Ivory Coast", "Cote d'Ivoire", "Cote dIvoire"],
    "North Macedonia": ["Macedonia"],
    "Czech Republic": ["Czechia"],
    "South Korea": ["Korea", "Republic of Korea"],
    "North Korea": ["DPRK"],
    "Russia": ["Russian Federation"],
    "Iran": ["Islamic Republic of Iran"],
    "Syria": ["Syrian Arab Republic"],
    "Tanzania": ["United Republic of Tanzania"],
    "Bolivia": ["Plurinational State of Bolivia"],
    "Venezuela": ["Bolivarian Republic of Venezuela"],
    "Vietnam": ["Viet Nam"],
    "Laos": ["Lao PDR", "Lao People's Democratic Republic"],
    "Brunei": ["Brunei Darussalam"],
    "Myanmar": ["Burma"],
    "Palestine": ["Palestinian Territory", "State of Palestine"],
    "Timor-Leste": ["East Timor"],
    "Eswatini": ["Swaziland"],
    "Cabo Verde": ["Cape Verde"],
}


async def seed_difficulty_and_aliases() -> None:
    """Update countries with difficulty classifications and abbreviation aliases."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Country))
        countries = result.scalars().all()

        if not countries:
            print("No countries found. Run seed_countries.py first.")
            return

        updated = 0
        for country in countries:
            changed = False

            # Set difficulty
            if country.name in EASY_COUNTRIES:
                new_difficulty = DifficultyEnum.EASY
            elif country.name in HARD_COUNTRIES:
                new_difficulty = DifficultyEnum.HARD
            else:
                new_difficulty = DifficultyEnum.MEDIUM

            if country.difficulty != new_difficulty:
                country.difficulty = new_difficulty
                changed = True

            # Add abbreviation aliases
            extra_aliases = ABBREVIATION_ALIASES.get(country.name, [])
            if extra_aliases:
                existing = set(country.alt_names or [])
                new_aliases = [a for a in extra_aliases if a not in existing]
                if new_aliases:
                    country.alt_names = list(existing) + new_aliases
                    changed = True

            if changed:
                updated += 1

        await session.commit()
        print(f"Updated {updated} / {len(countries)} countries with difficulty & aliases.")


if __name__ == "__main__":
    asyncio.run(seed_difficulty_and_aliases())
