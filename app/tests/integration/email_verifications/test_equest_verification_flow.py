import pytest
from sqlalchemy import select

from app.auth.schemas import RegisterRequest
from app.users.email_verifications.models import EmailVerification
from app.tests.helper import (
    get_auth_service,
    get_email_verification_service,
)


@pytest.mark.asyncio
async def test_request_verification_flow(session, monkeypatch):
    auth_service = get_auth_service(session)
    service = get_email_verification_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    # mock email
    monkeypatch.setattr(
        service.email_service,
        "send_email",
        lambda *args, **kwargs: None
    )

    await service.request_verification(user.email)

    stmt = select(EmailVerification).where(
        EmailVerification.user_id == user.id
    )
    result = await session.execute(stmt)
    verification = result.scalars().first()

    assert verification is not None
