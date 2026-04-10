import pytest
from sqlalchemy import select

from app.common.errors import ConflictError
from app.geo.countries.models import Country
from app.geo.countries.schemas import CountryCreate, CountryUpdatePartial
from app.geo.cities.schemas import CityCreate

from app.tests.helper import get_country_service, get_city_service


@pytest.mark.asyncio
async def test_country_full_flow(session):
    country_service = get_country_service(session)
    city_service = get_city_service(session)

    # CREATE
    country = await country_service.create_country(
        CountryCreate(name="Germany", iso_code="DE")
    )

    assert country.id is not None

    # UPDATE
    await country_service.update_country_partial(
        country_id=country.id,
        data=CountryUpdatePartial(name="Deutschland")
    )

    updated = await country_service.get_country(country.id)
    assert updated.name == "Deutschland"

    # ADD CITY → перевірка залежності
    city = await city_service.create_city(
        CityCreate(
            name="Berlin",
            region="Berlin",
            timezone="Europe/Berlin",
            country_id=country.id
        )
    )

    # DELETE FAIL (є city)
    with pytest.raises(ConflictError):
        await country_service.delete_country(country.id)

    # DELETE city
    await city_service.delete_city(city.id)

    # DELETE SUCCESS
    await country_service.delete_country(country.id)

    stmt = select(Country).where(Country.id == country.id)
    result = await session.execute(stmt)

    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_country_conflict(session):
    service = get_country_service(session)

    await service.create_country(
        CountryCreate(name="Germany", iso_code="DE")
    )

    with pytest.raises(ConflictError):
        await service.create_country(
            CountryCreate(name="Germany", iso_code="DE")
        )
