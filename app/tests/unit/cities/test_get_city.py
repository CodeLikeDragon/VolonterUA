from uuid import uuid4

import pytest

from app.common.errors import NotFoundError
from app.geo.cities.schemas import CityCreate
from app.geo.countries.schemas import CountryCreate
from app.tests.helper import get_country_service, get_city_service


@pytest.mark.asyncio
async def test_get_city(session):
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

    result = await city_service.get_city(city.id)

    assert result.id == city.id
    assert result.name == "Berlin"


@pytest.mark.asyncio
async def test_get_city_not_found(session):
    city_service = get_city_service(session)

    with pytest.raises(NotFoundError):
        await city_service.get_city(uuid4())


@pytest.mark.asyncio
async def test_get_cities(session):
    country_service = get_country_service(session)
    city_service = get_city_service(session)

    country = await country_service.create_country(
        CountryCreate(name="Germany", iso_code="DE")
    )

    await city_service.create_city(
        CityCreate(name="Berlin", region="Berlin", timezone="Europe/Berlin", country_id=country.id)
    )
    await city_service.create_city(
        CityCreate(name="Potsdam", region="Brandenburg", timezone="Europe/Berlin", country_id=country.id)
    )

    cities = await city_service.get_cities(limit=10, offset=0)

    assert len(cities) == 2

    names = {c.name for c in cities}
    assert names == {"Berlin", "Potsdam"}

