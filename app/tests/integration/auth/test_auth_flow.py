import pytest

from app.auth.schemas import RegisterRequest
from app.common.errors import UnauthorizedError

from app.tests.helper import get_auth_service, get_refresh_token_service
from app.tests.fixtures.fixtures import verify_user_helper



@pytest.mark.asyncio
async def test_full_auth_flow(session, verify_user_helper):
    auth = get_auth_service(session)
    refresh_service = get_refresh_token_service(session)

    await auth.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    # verify email
    await verify_user_helper(session)

    tokens = await auth.login(
        email="test@test.com",
        password="123456"
    )

    # refresh
    new_tokens = await refresh_service.refresh(tokens.refresh_token)

    assert new_tokens.access_token != tokens.access_token
    assert new_tokens.refresh_token != tokens.refresh_token

    # logout
    await auth.logout(new_tokens.refresh_token)

    # refresh after logout → має впасти
    with pytest.raises(UnauthorizedError):
        await refresh_service.refresh(new_tokens.refresh_token)
