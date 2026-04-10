import pytest
from sqlalchemy import select
from datetime import datetime, timedelta, timezone

from app.auth.schemas import RegisterRequest
from app.core.security import hash_token
from app.users.refresh_tokens.models import RefreshToken
from app.tests.helper import get_auth_service, get_refresh_token_service



@pytest.mark.asyncio
async def test_refresh_creates_new_token(session):
    auth_service = get_auth_service(session)
    service = get_refresh_token_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
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

    await service.refresh(raw_refresh)

    stmt = select(RefreshToken).where(
        RefreshToken.user_id == user.id
    )
    result = await session.execute(stmt)
    tokens = result.scalars().all()

    assert len(tokens) == 2
