import pytest
from datetime import datetime, timedelta, timezone

from app.auth.schemas import RegisterRequest
from app.core.security import generate_otp_code, hash_code
from app.users.password_resets.models import PasswordReset
from app.tests.helper import get_password_reset_service, get_auth_service


@pytest.mark.asyncio
async def test_confirm_reset(session):
    service = get_password_reset_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )

    code = generate_otp_code()
    code_hash = hash_code(code)

    reset = PasswordReset(
        user_id=user.id,
        code_hash=code_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
    )

    await service.repo.create(reset)
    await session.commit()

    await service.confirm_reset(user.email, code, "newpassword")

    assert reset.used_at is not None


@pytest.mark.asyncio
async def test_confirm_reset_invalid_code(session):
    service = get_password_reset_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )

    with pytest.raises(Exception):
        await service.confirm_reset(user.email, "wrong", "newpass")


@pytest.mark.asyncio
async def test_confirm_reset_expired(session):
    service = get_password_reset_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )

    code = generate_otp_code()
    code_hash = hash_code(code)

    reset = PasswordReset(
        user_id=user.id,
        code_hash=code_hash,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )

    await service.repo.create(reset)
    await session.commit()

    with pytest.raises(Exception):
        await service.confirm_reset(user.email, code, "newpass")
