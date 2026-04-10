from sqlalchemy import select, func, UUID
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.users.models import User


class UserRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def count(self, is_active: bool | None) -> int:

        stmt = select(func.count(User.id))

        if is_active is not None:
            stmt = stmt.where(User.is_active.is_(is_active))
        result = await self.session.execute(stmt)

        return result.scalar_one()


    async def get_by_id(self, user_id: UUID) -> User | None:

        stmt = (
            select(User)
            .options(selectinload(User.credentials))
            .where(User.id == user_id)
        )
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()


    async def get_by_ids(self, user_ids: list[UUID]) -> list[User]:
        query = select(User).where(User.id.in_(user_ids))
        result = await self.session.execute(query)
        return result.scalars().all()


    async def get_by_id_with_credentials(self, user_id: UUID):
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.credentials))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def get_by_email(self, email: str) -> User | None:

        stmt = (
            select(User)
            .options(selectinload(User.credentials))
            .where(User.email == email)
        )
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()


    async def list_filtered(
        self,
        is_active: bool | None,
        limit: int,
        offset: int,
    ) -> list[User]:

        query = select(User).order_by(User.created_at.desc())

        if is_active is not None:
            query = query.where(User.is_active.is_(is_active))

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)

        return result.scalars().all()


    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()

        return user


    async def update(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()

        return user
