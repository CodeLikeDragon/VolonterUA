import pytest
from datetime import datetime, timedelta, timezone

from app.auth.schemas import RegisterRequest
from app.core.security import create_refresh_token, hash_token
from app.users.refresh_tokens.models import RefreshToken
from app.tests.helper import get_refresh_token_service, get_auth_service


@pytest.mark.asyncio
async def test_refresh_success(session):
    service = get_refresh_token_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )

    refresh = create_refresh_token()
    token_hash = hash_token(refresh)

    token = RefreshToken(
        user_id=user.id,
        jti="test",
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
    )

    await service.repo.create(token)
    await session.commit()

    result = await service.refresh(refresh)

    assert result.access_token is not None
    assert result.refresh_token is not None


@pytest.mark.asyncio
async def test_refresh_invalid_token(session):
    service = get_refresh_token_service(session)

    with pytest.raises(Exception):
        await service.refresh("invalid")


@pytest.mark.asyncio
async def test_refresh_revoked(session):
    service = get_refresh_token_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )

    refresh = create_refresh_token()
    token_hash = hash_token(refresh)

    token = RefreshToken(
        user_id=user.id,
        jti="test",
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        revoked=True,
    )

    await service.repo.create(token)
    await session.commit()

    with pytest.raises(Exception):
        await service.refresh(refresh)


@pytest.mark.asyncio
async def test_refresh_expired(session):
    service = get_refresh_token_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )

    refresh = create_refresh_token()
    token_hash = hash_token(refresh)

    token = RefreshToken(
        user_id=user.id,
        jti="test",
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    )

    await service.repo.create(token)
    await session.commit()

    with pytest.raises(Exception):
        await service.refresh(refresh)
