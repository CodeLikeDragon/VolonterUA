import pytest
import asyncio

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.errors import ConflictError
from app.auth.schemas import RegisterRequest

from app.users.users.models import User
from app.users.credentials.models import Credentials

from app.tests.helper import get_auth_service


@pytest.mark.asyncio
async def test_register_creates_user_and_credentials(session):
    service = get_auth_service(session)

    await service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    result = await session.execute(select(User))
    user = result.scalar_one()

    result = await session.execute(select(Credentials))
    creds = result.scalar_one()

    assert user.email == "test@test.com"
    assert creds.password_hash != "123456"


@pytest.mark.asyncio
async def test_register_duplicate_email(session):
    service = get_auth_service(session)

    await service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    with pytest.raises(ConflictError):
        await service.register(
            RegisterRequest(
                email="test@test.com",
                password="123456"
            )
        )


@pytest.mark.asyncio
async def test_concurrent_register(engine):

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def register():
        async with async_session() as s:
            service = get_auth_service(s)
            return await service.register(
                RegisterRequest(
                    email="test@test.com",
                    password="123456"
                )
            )

    results = await asyncio.gather(
        register(),
        register(),
        return_exceptions=True
    )

    success = [r for r in results if not isinstance(r, Exception)]

    assert len(success) == 1
