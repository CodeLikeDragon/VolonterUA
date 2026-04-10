from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.refresh_tokens.models import RefreshToken


class RefreshTokenRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def revoke_all_for_user(self, user_id: UUID):
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False,
            )
            .values(revoked=True)
        )

        await self.session.execute(stmt)


    async def create(self, token: RefreshToken):
        self.session.add(token)


    async def revoke(self, token: RefreshToken):
        token.revoked = True
