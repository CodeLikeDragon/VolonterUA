from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.geo.cities.models import City


class CityRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_by_id(self, city_id: UUID) -> City | None:
        result = await self.session.execute(
            select(City).where(City.id == city_id)
        )
        return result.scalar_one_or_none()


    async def get_all(self, limit: int, offset: int) -> list[City]:
        result = await self.session.execute(
            select(City)
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()


    async def create(self, city: City) -> City:
        self.session.add(city)
        return city


    async def delete(self, city: City) -> None:
        await self.session.delete(city)
