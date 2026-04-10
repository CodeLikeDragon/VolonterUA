from uuid import uuid4

import pytest

from sqlalchemy import select

from app.common.errors import NotFoundError, ConflictError
from app.geo.cities.models import City
from app.geo.cities.schemas import CityCreate
from app.geo.countries.models import Country
from app.geo.countries.schemas import CountryCreate, CountryUpdate, CountryUpdatePartial
from app.tests.helper import get_country_service, get_city_service


@pytest.mark.asyncio
async def test_delete_country(session):
    service = get_country_service(session)

    country = await service.create_country(
        CountryCreate(
            name="Ukraine",
            iso_code="UA"
        )
    )

    await service.delete_country(country.id)

    stmt = select(Country).where(Country.id == country.id)
    result = await session.execute(stmt)
    deleted_country = result.scalar_one_or_none()

    assert deleted_country is None


@pytest.mark.asyncio
async def test_delete_country_not_found_error(session):
    service = get_country_service(session)
    city_service = get_city_service(session)

    country = await service.create_country(
        CountryCreate(
            name="Germany",
            iso_code="DE"
        )
    )

    await city_service.create_city(
        CityCreate(
            name="Berlin",
            region="Berlin",
            country_id=country.id
        )
    )

    with pytest.raises(NotFoundError):
        await service.delete_country(uuid4())


@pytest.mark.asyncio
async def test_delete_country_with_cities(session):
    service = get_country_service(session)
    city_service = get_city_service(session)

    country = await service.create_country(
        CountryCreate(
            name="Germany",
            iso_code="DE"
        )
    )

    city = await city_service.create_city(
        CityCreate(
            name="Berlin",
            region="Berlin",
            country_id=country.id
        )
    )

    with pytest.raises(ConflictError):
        await service.delete_country(country.id)


    stmt = select(City).where(City.country_id == country.id)
    result = await session.execute(stmt)
    cities = result.scalars().all()

    stmt = select(Country).where(Country.id == country.id)
    result = await session.execute(stmt)
    existing_country = result.scalar_one_or_none()

    assert existing_country is not None
    assert len(cities) == 1
