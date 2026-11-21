from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.categories.models import Category, RequestCategory


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

    async def set_for_request(self, request_id: UUID, category_ids: Sequence[UUID]) -> None:
        await self.session.execute(
            delete(RequestCategory).where(RequestCategory.request_id == request_id)
        )
        for category_id in set(category_ids):
            self.session.add(RequestCategory(request_id=request_id, category_id=category_id))
        await self.session.flush()
