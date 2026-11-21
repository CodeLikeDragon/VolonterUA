from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.categories.models import Category


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, limit: int, offset: int) -> list[Category]:
        result = await self.session.execute(
            select(Category)
            .order_by(Category.name)
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars())

    async def get_by_ids(self, category_ids: Sequence[UUID]) -> list[Category]:
        if not category_ids:
            return []

        result = await self.session.execute(
            select(Category).where(Category.id.in_(category_ids))
        )
        return list(result.scalars())

    async def create(self, category: Category) -> Category:
        self.session.add(category)
        await self.session.flush()
        return category
