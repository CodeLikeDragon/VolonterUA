from uuid import uuid4

import pytest
from sqlalchemy import select

from app.common.errors import ConflictError, NotFoundError
from app.geo.cities.models import City
from app.geo.cities.schemas import UpdateCity, CityCreate
from app.geo.countries.schemas import CountryCreate
from app.tests.helper import get_city_service, get_country_service


@pytest.mark.asyncio
async def test_update_city(session):
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

    await city_service.update_city(
        city_id=city.id,
        data=UpdateCity(
            name=" Berlin City ",
            region=" Berlin Region ",
            timezone=" Europe/Berlin "
        )
    )

    stmt = select(City).where(City.id == city.id)
    result = await session.execute(stmt)
    updated = result.scalar_one()

    assert updated.name == "Berlin City"
    assert updated.region == "Berlin Region"
    assert updated.timezone == "Europe/Berlin"


@pytest.mark.asyncio
async def test_update_city_partial(session):
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

    await city_service.update_city(
        city_id=city.id,
        data=UpdateCity(name="New Berlin")
    )

    stmt = select(City).where(City.id == city.id)
    result = await session.execute(stmt)
    updated = result.scalar_one()

    assert updated.name == "New Berlin"
    assert updated.region == "Berlin"  # не змінено


@pytest.mark.asyncio
async def test_update_city_not_found(session):
    city_service = get_city_service(session)

    with pytest.raises(NotFoundError):
        await city_service.update_city(
            city_id=uuid4(),
            data=UpdateCity(name="Test")
        )


@pytest.mark.asyncio
async def test_update_city_conflict(session):
    country_service = get_country_service(session)
    city_service = get_city_service(session)

    country = await country_service.create_country(
        CountryCreate(name="Germany", iso_code="DE")
    )

    await city_service.create_city(
        CityCreate(name="Berlin", region="Berlin", timezone="Europe/Berlin", country_id=country.id)
    )

    city2 = await city_service.create_city(
        CityCreate(name="Potsdam", region="Brandenburg", timezone="Europe/Berlin", country_id=country.id)
    )

    with pytest.raises(ConflictError):
        await city_service.update_city(
            city_id=city2.id,
            data=UpdateCity(name="Berlin")  # duplicate
        )
