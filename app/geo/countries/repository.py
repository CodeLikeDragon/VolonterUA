from uuid import UUID

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.geo.cities.models import City
from app.geo.countries.models import Country
from app.geo.countries.schemas import CountryUpdate


class CountryRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_by_id(self, country_id: UUID) -> Country | None:
        result = await self.session.execute(
            select(Country).where(Country.id == country_id)
        )
        return result.scalar_one_or_none()


    async def get_by_name(self, name: str) -> Country | None:
        result = await self.session.execute(
            select(Country).where(Country.name == name)
        )
        return result.scalar_one_or_none()


    async def get_by_iso_code(self, iso_code: str) -> Country | None:
        result = await self.session.execute(
            select(Country).where(Country.iso_code == iso_code)
        )
        return result.scalar_one_or_none()


    async def get_all(self, limit: int, offset: int) -> list[Country]:
        stmt = select(Country).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def get_all_cities(self, country_id: UUID, limit: int, offset: int) -> list[City]:
        result = await self.session.execute(
            select(City)
            .where(City.country_id == country_id)
            .order_by(City.name)
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()


    async def has_cities(self, country_id: UUID) -> bool:
        stmt = select(City.id).where(City.country_id == country_id).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None


    async def create(self, country: Country) -> Country:
        self.session.add(country)
        await self.session.flush()

        return country


    async def is_same_country(self, country_id: UUID, data: CountryUpdate) -> bool:
        conditions = []

        if data.name is not None:
            conditions.append(Country.name == data.name.strip())

        if data.iso_code is not None:
            conditions.append(Country.iso_code == data.iso_code.strip().upper())

        if not conditions:
            return False

        stmt = (
            select(Country)
            .where(
                and_(
                    or_(*conditions),
                    Country.id != country_id,
                )
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None


    async def update(self, country: Country, data: CountryUpdate) -> Country:
        country.name = data.name.strip()
        country.iso_code = data.iso_code.strip().upper()

        return country


    async def update_partial(self, country: Country, data: CountryUpdate) -> Country:
        allowed_fields = {"name", "iso_code"}

        for field, value in data.model_dump(exclude_unset=True).items():
            if field not in allowed_fields:
                continue

            if field == "iso_code":
                value = value.strip().upper()

            if field == "name":
                value = value.strip()

            setattr(country, field, value)

        return country


    async def delete(self, country: Country) -> None:
        await self.session.delete(country)
