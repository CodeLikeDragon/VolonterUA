import pytest
from sqlalchemy import select
from uuid import uuid4

from app.common.errors import ConflictError, NotFoundError
from app.geo.cities.models import City
from app.geo.cities.schemas import CityCreate, UpdateCity
from app.geo.countries.schemas import CountryCreate

from app.tests.helper import get_city_service, get_country_service


@pytest.mark.asyncio
async def test_city_full_flow(session):
    country_service = get_country_service(session)
    city_service = get_city_service(session)

    # CREATE COUNTRY
    country = await country_service.create_country(
        CountryCreate(name="Germany", iso_code="DE")
    )

    # CREATE CITY
    city = await city_service.create_city(
        CityCreate(
            name="Berlin",
            region="Berlin",
            timezone="Europe/Berlin",
            country_id=country.id
        )
    )

    # GET
    fetched = await city_service.get_city(city.id)
    assert fetched.name == "Berlin"

    # UPDATE
    await city_service.update_city(
        city_id=city.id,
        data=UpdateCity(name="Berlin City")
    )

    updated = await city_service.get_city(city.id)
    assert updated.name == "Berlin City"

    # DELETE
    await city_service.delete_city(city.id)

    stmt = select(City).where(City.id == city.id)
    result = await session.execute(stmt)

    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_city_conflict_same_country(session):
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


@pytest.mark.asyncio
async def test_city_same_name_different_countries(session):
    country_service = get_country_service(session)
    city_service = get_city_service(session)

    de = await country_service.create_country(
        CountryCreate(name="Germany", iso_code="DE")
    )

    us = await country_service.create_country(
        CountryCreate(name="USA", iso_code="US")
    )

    await city_service.create_city(
        CityCreate(
            name="Berlin",
            region="Berlin",
            timezone="Europe/Berlin",
            country_id=de.id
        )
    )

    city_us = await city_service.create_city(
        CityCreate(
            name="Berlin",
            region="Somewhere",
            timezone="America/New_York",
            country_id=us.id
        )
    )

    assert city_us is not None


@pytest.mark.asyncio
async def test_city_not_found(session):
    city_service = get_city_service(session)

    with pytest.raises(NotFoundError):
        await city_service.get_city(uuid4())


@pytest.mark.asyncio
async def test_city_invalid_country(session):
    city_service = get_city_service(session)

    with pytest.raises(ConflictError):
        await city_service.create_city(
            CityCreate(
                name="Ghost",
                region="Nowhere",
                timezone="UTC",
                country_id=uuid4()
            )
        )
