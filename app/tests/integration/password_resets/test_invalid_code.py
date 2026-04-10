import pytest

from app.auth.schemas import RegisterRequest
from app.tests.helper import (
    get_auth_service,
    get_password_reset_service,
)
from app.common.errors import BadRequestError


@pytest.mark.asyncio
async def test_confirm_reset_invalid_code(session, monkeypatch):
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

    with pytest.raises(BadRequestError):
        await service.confirm_reset(
            email=user.email,
            code="wrong",
            new_password="123"
        )
