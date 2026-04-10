import pytest

from sqlalchemy import select

from app.core.security import verify_password
from app.common.errors import UnauthorizedError, ConflictError

from app.auth.schemas import RegisterRequest, ChangePasswordRequest
from app.tests.fixtures.fixtures import verify_user_helper

from app.users.users.models import User
from app.users.password_resets.models import PasswordReset
from app.users.refresh_tokens.models import RefreshToken

from app.tests.helper import get_auth_service, get_password_reset_service


@pytest.mark.asyncio
async def test_request_reset(session):
    auth_service = get_auth_service(session)
    password_reset_service = get_password_reset_service(session)

    await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )



    result = await session.execute(select(User))
    user = result.scalars().one()

    await password_reset_service.request_reset(user.email)

    stmt = (select(PasswordReset).where(PasswordReset.user_id == user.id))
    result = await session.execute(stmt)
    password_reset = result.scalars().one()

    assert password_reset.user_id == user.id


@pytest.mark.asyncio
async def test_confirm_reset(session, monkeypatch):
    auth_service = get_auth_service(session)
    password_reset_service = get_password_reset_service(session)

    monkeypatch.setattr(
        "app.users.password_resets.service.generate_otp_code",
        lambda: "123456"
    )

    await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    result = await session.execute(select(User))
    user = result.scalars().one()

    await password_reset_service.request_reset(user.email)

    await password_reset_service.confirm_reset(
        user.email,
        "123456",
        "new_password123"
    )

    assert verify_password("new_password123", user.credentials.password_hash)

    result = await session.execute(select(PasswordReset))
    reset = result.scalars().one()

    assert reset.used_at is not None


@pytest.mark.asyncio
async def test_change_password_success(session, verify_user_helper):
    service = get_auth_service(session)

    # створюємо юзера
    await service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await verify_user_helper(session)

    # створюємо refresh token
    tokens = await service.login(
        email="test@test.com",
        password="123456"
    )

    # дістаємо юзера
    result = await session.execute(select(User))
    user = result.scalars().one()

    # міняємо пароль
    await service.change_password(
        user_id=user.id,
        data=ChangePasswordRequest(
            old_password="123456",
            new_password="new_password123"
        )
    )

    # 1. пароль реально змінився
    assert verify_password(
        "new_password123",
        user.credentials.password_hash
    )

    # 2. старий пароль більше не працює
    with pytest.raises(UnauthorizedError):
        await service.login(
            email="test@test.com",
            password="123456"
        )

    # 3. refresh токени інвалідовані
    result = await session.execute(select(RefreshToken))
    tokens = result.scalars().all()

    assert len(tokens) == 1
    assert tokens[0].revoked is True


@pytest.mark.asyncio
async def test_change_password_wrong_old_password(session):
    service = get_auth_service(session)

    await service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    result = await session.execute(select(User))
    user = result.scalars().one()

    with pytest.raises(UnauthorizedError):
        await service.change_password(
            user_id=user.id,
            data=ChangePasswordRequest(
                old_password="wrong",
                new_password="new_password123"
            )
        )

    # пароль не змінився
    assert verify_password(
        "123456",
        user.credentials.password_hash
    )


@pytest.mark.asyncio
async def test_change_password_same_password(session):
    service = get_auth_service(session)

    await service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    result = await session.execute(select(User))
    user = result.scalars().one()

    with pytest.raises(ConflictError):
        await service.change_password(
            user_id=user.id,
            data=ChangePasswordRequest(
                old_password="123456",
                new_password="123456"
            )
        )
