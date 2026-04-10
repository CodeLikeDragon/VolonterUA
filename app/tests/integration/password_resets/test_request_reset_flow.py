import pytest
from sqlalchemy import select

from app.auth.schemas import RegisterRequest
from app.users.password_resets.models import PasswordReset
from app.tests.helper import (
    get_auth_service,
    get_password_reset_service,
)


@pytest.mark.asyncio
async def test_request_reset_flow(session, monkeypatch):
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

    stmt = select(PasswordReset).where(
        PasswordReset.user_id == user.id
    )
    result = await session.execute(stmt)
    reset = result.scalars().first()

    assert reset is not None
