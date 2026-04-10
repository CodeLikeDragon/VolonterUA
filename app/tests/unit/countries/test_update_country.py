from uuid import uuid4

import pytest
from sqlalchemy import select

from app.common.errors import NotFoundError, ConflictError
from app.geo.countries.models import Country
from app.geo.countries.schemas import CountryCreate, CountryUpdate, CountryUpdatePartial
from app.tests.helper import get_country_service


@pytest.mark.asyncio
async def test_update_country_full(session):
    service = get_country_service(session)

    country = await service.create_country(
        CountryCreate(
            name="Germany",
            iso_code="UA"
        )
    )

    await service.update_country_full(
        data=CountryUpdate(
            name="  Deutschland  ",
            iso_code=" de "
        ),
        country_id=country.id
    )

    stmt = select(Country).where(Country.id == country.id)
    result = await session.execute(stmt)
    updated_country = result.scalar_one_or_none()

    assert updated_country is not None
    assert updated_country.name == "Deutschland"
    assert updated_country.iso_code == "DE"


@pytest.mark.asyncio
async def test_update_country_full_not_found_error(session):
    service = get_country_service(session)

    await service.create_country(
        CountryCreate(
            name="Germany",
            iso_code="UA"
        )
    )

    with pytest.raises(NotFoundError):
        await service.update_country_full(
            data=CountryUpdate(
                name="Deutschland",
                iso_code="DE"
            ),
            country_id=uuid4()
        )


@pytest.mark.asyncio
async def test_update_country_full_conflict_error(session):
    service = get_country_service(session)

    await service.create_country(
        CountryCreate(
            name="Germany",
            iso_code="DE"
        )
    )

    country_ua = await service.create_country(
        CountryCreate(
            name="Ukraine",
            iso_code="UA"
        )
    )

    with pytest.raises(ConflictError):
        await service.update_country_full(
            data=CountryUpdate(
                name="Germany",
                iso_code="DE"
            ),
            country_id=country_ua.id
        )


# =========================
# PARTIAL UPDATE
# =========================

@pytest.mark.asyncio
async def test_update_country_partial_only_name(session):
    service = get_country_service(session)

    country = await service.create_country(
        CountryCreate(
            name="Germany",
            iso_code="UA"
        )
    )

    await service.update_country_partial(
        data=CountryUpdatePartial(
            name="New Germany"
        ),
        country_id=country.id
    )

    stmt = select(Country).where(Country.id == country.id)
    result = await session.execute(stmt)
    updated_country = result.scalar_one_or_none()

    assert updated_country.name == "New Germany"
    assert updated_country.iso_code == "UA"  # не змінено


@pytest.mark.asyncio
async def test_update_country_partial_only_iso_code(session):
    service = get_country_service(session)

    country = await service.create_country(
        CountryCreate(
            name="Germany",
            iso_code="UA"
        )
    )

    await service.update_country_partial(
        data=CountryUpdatePartial(
            iso_code="de"
        ),
        country_id=country.id
    )

    stmt = select(Country).where(Country.id == country.id)
    result = await session.execute(stmt)
    updated_country = result.scalar_one_or_none()

    assert updated_country.name == "Germany"
    assert updated_country.iso_code == "DE"


@pytest.mark.asyncio
async def test_update_country_partial_both_fields(session):
    service = get_country_service(session)

    country = await service.create_country(
        CountryCreate(
            name="Germany",
            iso_code="UA"
        )
    )

    await service.update_country_partial(
        data=CountryUpdatePartial(
            name=" Deutschland ",
            iso_code=" de "
        ),
        country_id=country.id
    )

    stmt = select(Country).where(Country.id == country.id)
    result = await session.execute(stmt)
    updated_country = result.scalar_one_or_none()

    assert updated_country.name == "Deutschland"
    assert updated_country.iso_code == "DE"


@pytest.mark.asyncio
async def test_update_country_partial_not_found_error(session):
    service = get_country_service(session)

    await service.create_country(
        CountryCreate(
            name="Germany",
            iso_code="UA"
        )
    )

    with pytest.raises(NotFoundError):
        await service.update_country_partial(
            data=CountryUpdatePartial(
                name="Germany"
            ),
            country_id=uuid4()
        )


@pytest.mark.asyncio
async def test_update_country_partial_conflict_error(session):
    service = get_country_service(session)

    await service.create_country(
        CountryCreate(
            name="Germany",
            iso_code="DE"
        )
    )

    country_ua = await service.create_country(
        CountryCreate(
            name="Ukraine",
            iso_code="UA"
        )
    )

    with pytest.raises(ConflictError):
        await service.update_country_partial(
            data=CountryUpdatePartial(
                iso_code="DE"
            ),
            country_id=country_ua.id
        )
