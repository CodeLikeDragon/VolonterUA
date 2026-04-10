import asyncio

from app.core.db import async_session_factory
from app.geo.seed import seed_countries_and_cities


async def main():
    async with async_session_factory() as session:
        await seed_countries_and_cities(session)


if __name__ == "__main__":
    asyncio.run(main())
