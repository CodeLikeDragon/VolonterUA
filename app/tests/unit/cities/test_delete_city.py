from uuid import uuid4

import pytest
from sqlalchemy import select

from app.common.errors import NotFoundError
from app.geo.cities.models import City
from app.geo.cities.schemas import CityCreate
from app.geo.countries.schemas import CountryCreate
from app.tests.helper import get_city_service, get_country_service


@pytest.mark.asyncio
async def test_delete_city(session):
    country_service = get_country_service(session)
    city_service = get_city_service(session)

    country = await country_service.create_country(
        CountryCreate(name="Germany", iso_code="DE")
    )

    city = await city_service.create_city(
        CityCreate(
            name="Berlin",
            region="Berlin",
            timezone="Europe/Berlin",
            country_id=country.id
        )
    )

    await city_service.delete_city(city.id)

    stmt = select(City).where(City.id == city.id)
    result = await session.execute(stmt)
    deleted = result.scalar_one_or_none()

    assert deleted is None


@pytest.mark.asyncio
async def test_delete_city_not_found(session):
    city_service = get_city_service(session)

    with pytest.raises(NotFoundError):
        await city_service.delete_city(uuid4())
