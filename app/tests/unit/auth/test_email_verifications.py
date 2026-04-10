import pytest
from sqlalchemy import select
from datetime import datetime, timezone, timedelta

from app.common.errors import BadRequestError
from app.auth.schemas import RegisterRequest

from app.users.users.models import User
from app.users.email_verifications.models import EmailVerification

from app.tests.helper import get_auth_service, get_email_verification_service


@pytest.mark.asyncio
async def test_request_verification(session):
    auth_service = get_auth_service(session)
    email_verification_service = get_email_verification_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await email_verification_service.request_verification(email="test@test.com")

    stmt = select(EmailVerification).where(EmailVerification.user_id == user.id)
    result = await session.execute(stmt)
    email_verification = result.scalars().one()

    assert email_verification.user_id == user.id
    assert email_verification.code_hash != None
    assert email_verification.expires_at != None


@pytest.mark.asyncio
async def test_verify_email(session, monkeypatch):
    auth_service = get_auth_service(session)
    email_verification_service = get_email_verification_service(session)

    monkeypatch.setattr(
        "app.users.email_verifications.service.generate_otp_code",
        lambda: "123456"
    )

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await email_verification_service.request_verification("test@test.com")

    await email_verification_service.verify_email(
        email="test@test.com",
        code="123456"
    )

    # перевірка user
    result = await session.execute(select(User))
    user = result.scalars().one()

    assert user.email_verified_at is not None

    # перевірка verification
    result = await session.execute(select(EmailVerification))
    verification = result.scalars().one()

    assert verification.used_at is not None


@pytest.mark.asyncio
async def test_verify_email_invalid_code(session, monkeypatch):

    auth_service = get_auth_service(session)
    email_verification_service = get_email_verification_service(session)

    monkeypatch.setattr(
        "app.users.email_verifications.service.generate_otp_code",
        lambda: "123456"
    )

    await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await email_verification_service.request_verification("test@test.com")

    with pytest.raises(BadRequestError):
        await email_verification_service.verify_email(
            email="test@test.com",
            code="wrong_code"
        )

    # перевірка — нічого не змінилось
    result = await session.execute(select(User))
    user = result.scalars().one()
    assert user.email_verified_at is None

    result = await session.execute(select(EmailVerification))
    verification = result.scalars().one()
    assert verification.used_at is None


@pytest.mark.asyncio
async def test_verify_email_expired_code(session, monkeypatch):

    auth_service = get_auth_service(session)
    email_verification_service = get_email_verification_service(session)

    monkeypatch.setattr(
        "app.users.email_verifications.service.generate_otp_code",
        lambda: "123456"
    )

    await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await email_verification_service.request_verification("test@test.com")

    # вручну робимо код expired
    result = await session.execute(select(EmailVerification))
    verification = result.scalars().one()

    verification.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    await session.commit()

    with pytest.raises(BadRequestError):
        await email_verification_service.verify_email(
            email="test@test.com",
            code="123456"
        )

    # перевірка
    result = await session.execute(select(User))
    user = result.scalars().one()
    assert user.email_verified_at is None


@pytest.mark.asyncio
async def test_verify_email_reuse_code(session, monkeypatch):

    auth_service = get_auth_service(session)
    email_verification_service = get_email_verification_service(session)

    monkeypatch.setattr(
        "app.users.email_verifications.service.generate_otp_code",
        lambda: "123456"
    )

    await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await email_verification_service.request_verification("test@test.com")

    # перший раз — ок
    await email_verification_service.verify_email(
        email="test@test.com",
        code="123456"
    )

    # другий раз — має впасти
    with pytest.raises(BadRequestError):
        await email_verification_service.verify_email(
            email="test@test.com",
            code="123456"
        )
