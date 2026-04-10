from uuid import uuid4
from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import AuditEventService
from app.common.errors import UnauthorizedError
from app.core.security import (
    hash_token,
    create_refresh_token,
    create_access_token
)
from app.users.refresh_tokens.models import RefreshToken
from app.users.refresh_tokens.repository import RefreshTokenRepository
from app.users.refresh_tokens.schemas import TokenResponse


class RefreshTokenService:

    def __init__(
        self,
        session: AsyncSession,
        repo: RefreshTokenRepository,
        audit_service: AuditEventService,
    ):
        self.session = session
        self.repo = repo
        self.audit_service = audit_service


    async def refresh(self, refresh_token: str) -> TokenResponse:

        token_hash = hash_token(refresh_token)

        token = await self.repo.get_by_hash(token_hash)

        if (
            not token
            or token.revoked
            or token.expires_at < datetime.now(timezone.utc)
        ):
            raise UnauthorizedError("Invalid refresh token")

        user_id = token.user_id

        new_refresh = create_refresh_token()
        new_hash = hash_token(new_refresh)

        try:
            await self.repo.revoke(token)

            new_token = RefreshToken(
                user_id=user_id,
                jti=str(uuid4()),
                token_hash=new_hash,
                expires_at=datetime.now(timezone.utc) + timedelta(days=30),
                replaced_by=None,
            )

            token.replaced_by = new_token.jti

            access = create_access_token(subject=str(user_id))

            await self.repo.create(new_token)

            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise UnauthorizedError("Invalid refresh token")

        try:
            await self.audit_service.log_event(
                event="refresh_token_rotated",
                user_id=user_id,
                data={"user_id": str(user_id)},
            )
        except Exception:
            pass

        return TokenResponse(
            access_token=access,
            refresh_token=new_refresh
        )
