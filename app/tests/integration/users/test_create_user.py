from datetime import date, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.common.errors import ConflictError, NotFoundError, BadRequestError
from app.users.users.schemas import UserCreate
from app.users.users.models import User

from app.tests.helper import get_user_service


@pytest.mark.asyncio
async def test_create_user(session):
    service = get_user_service(session)

    user = await service.create_user(
        UserCreate(
            email="test@test.com",
            first_name="John",
            last_name="Doe"
        )
    )

    stmt = select(User).where(User.id == user.id)
    result = await session.execute(stmt)
    db_user = result.scalar_one()

    assert db_user.email == "test@test.com"


@pytest.mark.asyncio
async def test_create_user_duplicate_email(session):
    service = get_user_service(session)

    await service.create_user(
        UserCreate(email="test@test.com")
    )

    with pytest.raises(ConflictError):
        await service.create_user(
            UserCreate(email="test@test.com")
        )


@pytest.mark.asyncio
async def test_create_user_invalid_city(session):
    service = get_user_service(session)

    with pytest.raises(NotFoundError):
        await service.create_user(
            UserCreate(
                email="test@test.com",
                city_id=uuid4()
            )
        )


@pytest.mark.asyncio
async def test_create_user_future_birth_date(session):
    service = get_user_service(session)

    future_date = date.today() + timedelta(days=1)

    with pytest.raises(BadRequestError):
        await service.create_user(
            UserCreate(
                email="test@test.com",
                birth_date=future_date
            )
        )