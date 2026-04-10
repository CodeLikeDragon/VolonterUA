import pytest
from sqlalchemy import select

from app.common.errors import ConflictError
from app.geo.countries.models import Country
from app.geo.countries.schemas import CountryCreate
from app.tests.helper import get_country_service


@pytest.mark.asyncio
async def test_create_country(session):
    service = get_country_service(session)

    country = await service.create_country(
        CountryCreate(
            name="Germany",
            iso_code="DE"
        )
    )

    stmt = select(Country).where(Country.id == country.id)
    result = await session.execute(stmt)
    country = result.scalar_one_or_none()

    assert country is not None
    assert country.name == "Germany"
    assert country.iso_code == "DE"



@pytest.mark.asyncio
async def test_create_country_double(session):
    service = get_country_service(session)

    country = await service.create_country(
        CountryCreate(
            name="Germany",
            iso_code="DE"
        )
    )

    with pytest.raises(ConflictError):
        await service.create_country(
            CountryCreate(
                name="Germany",
                iso_code="DE"
            )
        )

    with pytest.raises(ConflictError):
        await service.create_country(
            CountryCreate(
                name="germany",
                iso_code="de"
            )
        )

    stmt = select(Country).where(Country.name=="Germany")
    result = await session.execute(stmt)
    countries = result.scalars().all()

    assert len(countries) == 1
    assert country.name == "Germany"
    assert country.iso_code == "DE"
