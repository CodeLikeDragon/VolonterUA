import pytest

from app.common.errors import UnauthorizedError
from app.auth.schemas import RegisterRequest

from app.tests.helper import get_auth_service, get_refresh_token_service
from app.tests.fixtures.fixtures import verify_user_helper


@pytest.mark.asyncio
async def test_refresh(session, verify_user_helper):
    auth_service = get_auth_service(session)
    refresh_service = get_refresh_token_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await verify_user_helper(session)

    tokens = await auth_service.login(
        email="test@test.com",
        password="123456"
    )

    ref_token = tokens.refresh_token
    access_token = tokens.access_token

    new_tokens = await refresh_service.refresh(ref_token)

    assert ref_token != new_tokens.refresh_token
    assert access_token != new_tokens.access_token


@pytest.mark.asyncio
async def test_refresh_reuse_token(session, verify_user_helper):
    auth_service = get_auth_service(session)
    refresh_service = get_refresh_token_service(session)

    await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )

    await verify_user_helper(session)

    tokens = await auth_service.login(
        email="test@test.com",
        password="123456"
    )

    # перший раз ок
    await refresh_service.refresh(tokens.refresh_token)

    # другий раз — має впасти
    with pytest.raises(UnauthorizedError):
        await refresh_service.refresh(tokens.refresh_token)
