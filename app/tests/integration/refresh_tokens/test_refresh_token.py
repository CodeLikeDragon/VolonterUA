import pytest
from datetime import datetime, timedelta, timezone

from app.auth.schemas import RegisterRequest
from app.core.security import hash_token
from app.users.refresh_tokens.models import RefreshToken
from app.tests.helper import get_auth_service, get_refresh_token_service


@pytest.mark.asyncio
async def test_refresh_token_flow(session):
    auth_service = get_auth_service(session)
    service = get_refresh_token_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    raw_refresh = "refresh123"
    token_hash = hash_token(raw_refresh)

    token = RefreshToken(
        user_id=user.id,
        jti="old",
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
    )

    await service.repo.create(token)
    await session.commit()

    result = await service.refresh(raw_refresh)

    assert result.access_token is not None
    assert result.refresh_token is not None
