import pytest

from app.auth.schemas import RegisterRequest
from app.tests.helper import (
    get_auth_service,
    get_password_reset_service,
)
from app.common.errors import ConflictError


@pytest.mark.asyncio
async def test_request_reset_rate_limit(session, monkeypatch):
    auth_service = get_auth_service(session)
    service = get_password_reset_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    monkeypatch.setattr(
        service.email_service,
        "send_email",
        lambda *args, **kwargs: None
    )

    await service.request_reset(user.email)

    with pytest.raises(ConflictError):
        await service.request_reset(user.email)
