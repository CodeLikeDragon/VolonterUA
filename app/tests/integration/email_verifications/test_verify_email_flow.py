import pytest

from app.auth.schemas import RegisterRequest
from app.tests.helper import (
    get_auth_service,
    get_email_verification_service,
)


@pytest.mark.asyncio
async def test_verify_email_flow(session, monkeypatch):
    auth_service = get_auth_service(session)
    service = get_email_verification_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    # стабільний код
    monkeypatch.setattr(
        "app.users.email_verifications.service.generate_otp_code",
        lambda: "123456"
    )

    monkeypatch.setattr(
        service.email_service,
        "send_email",
        lambda *args, **kwargs: None
    )

    await service.request_verification(user.email)

    await service.verify_email(user.email, "123456")

    assert user.email_verified_at is not None
