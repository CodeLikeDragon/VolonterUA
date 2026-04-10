from uuid import uuid4

import pytest

from sqlalchemy import select

from app.common.errors import NotFoundError
from app.geo.cities.schemas import CityCreate
from app.geo.countries.models import Country
from app.geo.countries.schemas import CountryCreate
from app.tests.helper import get_country_service, get_city_service


@pytest.mark.asyncio
async def test_get_country(session):
    service = get_country_service(session)

    await service.create_country(
        CountryCreate(
            name="Germany",
            iso_code="DE"
        )
    )

    result = await session.execute(select(Country))
    country = result.scalars().first()

    country = await service.get_country(country.id)

    assert country is not None
    assert country.name == "Germany"
    assert country.iso_code == "DE"


@pytest.mark.asyncio
async def test_get_country_error(session):
    service = get_country_service(session)

    await service.create_country(
        CountryCreate(
            name="Germany",
            iso_code="DE"
        )
    )

    with pytest.raises(NotFoundError):
        await service.get_country(uuid4())


@pytest.mark.asyncio
async def test_get_country_cities(session):
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
            timezone="Europe/Berlin",
            country_id=country.id
        )
    )

    await city_service.create_city(
        CityCreate(
            name="Potsdam",
            region="Brandenburg",
            timezone="Europe/Berlin",
            country_id=country.id
        )
    )

    cities = await service.get_country_cities(
        country_id=country.id,
        limit=5,
        offset=0
    )

    assert len(cities) == 2

    assert cities[0].name == "Berlin"
    assert cities[0].region == "Berlin"
    assert cities[0].timezone == "Europe/Berlin"
    assert cities[0].country_id == country.id

    assert cities[1].name == "Potsdam"
    assert cities[1].region == "Brandenburg"
    assert cities[1].timezone == "Europe/Berlin"
    assert cities[1].country_id == country.id


@pytest.mark.asyncio
async def test_get_countries(session):
    service = get_country_service(session)

    await service.create_country(
        CountryCreate(
            name="Germany",
            iso_code="DE"
        )
    )

    await service.create_country(
        CountryCreate(
            name="Ukraine",
            iso_code="UA"
        )
    )

    countries = await service.get_countries(
        limit=5,
        offset=0
    )

    assert len(countries) == 2

    assert countries[0].name == "Germany"
    assert countries[0].iso_code == "DE"

    assert countries[1].name == "Ukraine"
    assert countries[1].iso_code == "UA"


@pytest.mark.asyncio
async def test_get_countries_empty_list(session):
    service = get_country_service(session)

    countries = await service.get_countries(
        limit=5,
        offset=0
    )

    assert len(countries) == 0

