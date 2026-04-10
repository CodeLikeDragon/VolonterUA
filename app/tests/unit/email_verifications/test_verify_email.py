import pytest
from sqlalchemy import select
from datetime import datetime, timedelta, timezone

from app.auth.schemas import RegisterRequest
from app.core.security import generate_otp_code, hash_code
from app.users.email_verifications.models import EmailVerification
from app.tests.helper import get_email_verification_service, get_auth_service


@pytest.mark.asyncio
async def test_verify_email(session):
    service = get_email_verification_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    code = generate_otp_code()
    code_hash = hash_code(code)

    verification = EmailVerification(
        user_id=user.id,
        code_hash=code_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
    )

    await service.repo.create(verification)
    await session.commit()

    await service.verify_email(user.email, code)

    stmt = select(EmailVerification).where(
        EmailVerification.user_id == user.id
    )
    result = await session.execute(stmt)
    verification = result.scalars().first()

    assert verification.used_at is not None
    assert user.email_verified_at is not None


@pytest.mark.asyncio
async def test_verify_email_invalid_code(session):
    service = get_email_verification_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    with pytest.raises(Exception):
        await service.verify_email(user.email, "wrongcode")


@pytest.mark.asyncio
async def test_verify_email_expired_code(session):
    service = get_email_verification_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    code = generate_otp_code()
    code_hash = hash_code(code)

    verification = EmailVerification(
        user_id=user.id,
        code_hash=code_hash,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )

    await service.repo.create(verification)
    await session.commit()

    with pytest.raises(Exception):
        await service.verify_email(user.email, code)
