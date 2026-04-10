import pytest

from app.tests.helper import get_password_reset_service


@pytest.mark.asyncio
async def test_request_reset_user_not_found(session):
    service = get_password_reset_service(session)

    # не повинно падати
    await service.request_reset("notfound@test.com")
