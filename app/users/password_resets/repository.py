from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.password_resets.models import PasswordReset


class PasswordResetRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, reset: PasswordReset):
        self.session.add(reset)


    async def get_valid_reset(
        self,
        user_id: str,
        code_hash: str
    ) -> PasswordReset | None:

        stmt = select(PasswordReset).where(
            PasswordReset.user_id == user_id,
            PasswordReset.code_hash == code_hash,
            PasswordReset.used_at.is_(None),
            PasswordReset.expires_at > datetime.now(timezone.utc),
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def get_last_active(self, user_id: str) -> PasswordReset | None:
        stmt = (
            select(PasswordReset)
            .where(
                PasswordReset.user_id == user_id,
                PasswordReset.used_at.is_(None),
                PasswordReset.expires_at > datetime.now(timezone.utc),
            )
            .order_by(PasswordReset.expires_at.desc())
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def invalidate_all(self, user_id: str):
        stmt = (
            update(PasswordReset)
            .where(
                PasswordReset.user_id == user_id,
                PasswordReset.used_at.is_(None),
            )
            .values(used_at=datetime.now(timezone.utc))
        )

        await self.session.execute(stmt)
