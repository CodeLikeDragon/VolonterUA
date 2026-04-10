from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.email_verifications.models import EmailVerification


class EmailVerificationRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, verification: EmailVerification):
        self.session.add(verification)


    async def get_valid_code(
        self,
        user_id: str,
        code_hash: str
    ) -> EmailVerification | None:
        stmt = select(EmailVerification).where(
            EmailVerification.user_id == user_id,
            EmailVerification.code_hash == code_hash,
            EmailVerification.used_at.is_(None),
            EmailVerification.expires_at > datetime.now(timezone.utc)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def invalidate_all(self, user_id: str):
        stmt = (
            update(EmailVerification)
            .where(
                EmailVerification.user_id == user_id,
                EmailVerification.used_at.is_(None)
            )
            .values(used_at=datetime.now(timezone.utc))
        )

        await self.session.execute(stmt)


    async def get_last_active(self, user_id: str) -> EmailVerification | None:
        stmt = (
            select(EmailVerification)
            .where(
                EmailVerification.user_id == user_id,
                EmailVerification.used_at.is_(None),
                EmailVerification.expires_at > datetime.now(timezone.utc)
            )
            .order_by(EmailVerification.expires_at.desc())
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
