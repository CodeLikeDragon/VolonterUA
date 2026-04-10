import pytest
from sqlalchemy import select

from app.common.errors import UnauthorizedError

from app.auth.schemas import RegisterRequest
from app.tests.fixtures.fixtures import verify_user_helper

from app.users.users.models import User
from app.users.refresh_tokens.models import RefreshToken

from app.tests.helper import get_auth_service


@pytest.mark.asyncio
async def test_login_user_and_create_tokens(session, verify_user_helper):
    service = get_auth_service(session)

    await service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await verify_user_helper(session)

    token = await service.login(
        email="test@test.com",
        password="123456"
    )

    assert token.token_type == "bearer"
    assert token.access_token is not None
    assert token.refresh_token is not None

    result = await session.execute(select(RefreshToken))
    db_tokens = result.scalars().all()

    assert len(db_tokens) == 1
    assert db_tokens[0].revoked is False


@pytest.mark.asyncio
async def test_login_wrong_password(session, verify_user_helper):
    service = get_auth_service(session)

    await service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await verify_user_helper(session)

    with pytest.raises(UnauthorizedError):
        await service.login(
            email="test@test.com",
            password="wrong_password"
        )

    result = await session.execute(select(RefreshToken))
    db_tokens = result.scalars().all()
    assert len(db_tokens) == 0


@pytest.mark.asyncio
async def test_login_user_not_found(session, verify_user_helper):
    service = get_auth_service(session)

    await service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await verify_user_helper(session)

    with pytest.raises(UnauthorizedError):
        await service.login(
            email="wrong_test@test.com",
            password="123456"
        )

    result = await session.execute(select(RefreshToken))
    db_tokens = result.scalars().all()
    assert len(db_tokens) == 0


@pytest.mark.asyncio
async def test_login_inactive_user(session, verify_user_helper):
    service = get_auth_service(session)

    await service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await verify_user_helper(session)

    result = await session.execute(select(User))
    user = result.scalars().one()

    user.is_active = False
    await session.commit()

    with pytest.raises(UnauthorizedError):
        await service.login(
            email="test@test.com",
            password="123456"
        )

    result = await session.execute(select(RefreshToken))
    tokens = result.scalars().all()

    assert len(tokens) == 0
