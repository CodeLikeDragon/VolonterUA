import pytest
from uuid import uuid4
from sqlalchemy import select
from datetime import date, timedelta

from app.auth.schemas import RegisterRequest
from app.common.errors import NotFoundError, ConflictError, BadRequestError
from app.users.users.models import User
from app.users.users.schemas import UserCreate, UserUpdate
from app.tests.helper import (
    get_user_service,
    get_auth_service,
    get_city_service,
    get_country_service,
)
from app.geo.cities.schemas import CityCreate
from app.geo.countries.schemas import CountryCreate


@pytest.mark.asyncio
async def test_create_user(session):
    service = get_user_service(session)
    city_service = get_city_service(session)
    country_service = get_country_service(session)

    country = await country_service.create_country(
        CountryCreate(name="Germany", iso_code="DE")
    )

    city = await city_service.create_city(
        CityCreate(
            name="Berlin",
            region="Berlin",
            timezone="Europe/Berlin",
            country_id=country.id,
        )
    )

    user = await service.create_user(
        data=UserCreate(
            email="test@test.com",
            city_id=city.id
        )
    )

    stmt = select(User).where(User.id == user.id)
    result = await session.execute(stmt)

    assert result.scalar_one() is not None


@pytest.mark.asyncio
async def test_create_user_duplicate(session):
    service = get_user_service(session)

    await service.create_user(UserCreate(email="test@test.com"))

    with pytest.raises(ConflictError):
        await service.create_user(UserCreate(email="test@test.com"))


@pytest.mark.asyncio
async def test_create_user_invalid_birth_date(session):
    service = get_user_service(session)

    with pytest.raises(BadRequestError):
        await service.create_user(
            UserCreate(
                email="test@test.com",
                birth_date=date.today() + timedelta(days=1)
            )
        )
