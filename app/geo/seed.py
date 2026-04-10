from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.geo.countries.models import Country, City


COUNTRIES = [
    {"iso_code": "UA", "name": "Ukraine"},
    {"iso_code": "DE", "name": "Germany"},
]

CITIES = {
    "UA": [
        {"name": "Kyiv", "region": "Kyiv", "timezone": "Europe/Kyiv"},
        {"name": "Lviv", "region": "Lviv", "timezone": "Europe/Kyiv"},
    ],
    "DE": [
        {"name": "Berlin", "region": "Berlin", "timezone": "Europe/Berlin"},
        {"name": "Hamburg", "region": "Hamburg", "timezone": "Europe/Berlin"},
    ],
}


async def seed_countries_and_cities(session: AsyncSession) -> None:
    # --- countries ---
    existing = {
        c.iso_code: c
        for c in (await session.execute(select(Country))).scalars().all()
    }

    for data in COUNTRIES:
        if data["iso_code"] not in existing:
            session.add(Country(**data))

    await session.flush()

    countries = {
        c.iso_code: c
        for c in (await session.execute(select(Country))).scalars().all()
    }

    # --- cities ---
    for iso_code, cities in CITIES.items():
        country = countries[iso_code]

        existing_cities = {
            c.name
            for c in (
                await session.execute(
                    select(City).where(City.country_id == country.id)
                )
            ).scalars().all()
        }

        for city in cities:
            if city["name"] not in existing_cities:
                session.add(
                    City(
                        country_id=country.id,
                        **city,
                    )
                )

    await session.commit()
