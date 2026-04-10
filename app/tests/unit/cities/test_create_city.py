import pytest
from sqlalchemy import select

from app.common.errors import ConflictError
from app.geo.cities.models import City
from app.geo.cities.schemas import CityCreate
from app.geo.countries.schemas import CountryCreate
from app.tests.helper import get_city_service, get_country_service


@pytest.mark.asyncio
async def test_create_city(session):
    country_service = get_country_service(session)
    city_service = get_city_service(session)

    country = await country_service.create_country(
        CountryCreate(name="Germany", iso_code="DE")
    )

    city = await city_service.create_city(
        CityCreate(
            name=" Berlin ",
            region=" Berlin ",
            timezone=" Europe/Berlin ",
            country_id=country.id
        )
    )

    stmt = select(City).where(City.id == city.id)
    result = await session.execute(stmt)
    db_city = result.scalar_one_or_none()

    assert db_city is not None
    assert db_city.name == "Berlin"
    assert db_city.region == "Berlin"
    assert db_city.timezone == "Europe/Berlin"
    assert db_city.country_id == country.id


@pytest.mark.asyncio
async def test_create_city_conflict(session):
    country_service = get_country_service(session)
    city_service = get_city_service(session)

    country = await country_service.create_country(
        CountryCreate(name="Germany", iso_code="DE")
    )

    await city_service.create_city(
        CityCreate(
            name="Berlin",
            region="Berlin",
            timezone="Europe/Berlin",
            country_id=country.id
        )
    )

    with pytest.raises(ConflictError):
        await city_service.create_city(
            CityCreate(
                name="Berlin",
                region="Berlin",
                timezone="Europe/Berlin",
                country_id=country.id
            )
        )
