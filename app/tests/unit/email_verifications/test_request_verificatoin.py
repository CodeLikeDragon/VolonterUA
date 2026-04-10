import pytest
from sqlalchemy import select

from app.auth.schemas import RegisterRequest
from app.users.email_verifications.models import EmailVerification
from app.tests.helper import get_email_verification_service, get_auth_service
from app.tests.fixtures.fixtures import verify_user_helper


@pytest.mark.asyncio
async def test_request_verification(session):
    service = get_email_verification_service(session)
    auth_service = get_auth_service(session)

    # реєстрація користувача
    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await service.request_verification(user.email)

    # перевірка БД
    stmt = select(EmailVerification).where(
        EmailVerification.user_id == user.id
    )
    result = await session.execute(stmt)
    verification = result.scalars().first()

    assert verification is not None
    assert verification.used_at is None


@pytest.mark.asyncio
async def test_request_verification_user_not_found(session):
    service = get_email_verification_service(session)

    await service.request_verification("notfound@test.com")


@pytest.mark.asyncio
async def test_request_verification_already_verified(session, verify_user_helper):
    service = get_email_verification_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    # підтверджуємо email
    await verify_user_helper(session)

    with pytest.raises(Exception):  # або BadRequestError якщо імпортуєш
        await service.request_verification(user.email)


@pytest.mark.asyncio
async def test_request_verification_rate_limit(session):
    service = get_email_verification_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await service.request_verification(user.email)

    with pytest.raises(Exception):
        await service.request_verification(user.email)
