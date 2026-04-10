from __future__ import annotations

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.requests.request_items.models import RequestItem
from app.requests.request_items.schemas import RequestItemCreate
from app.requests.requests.models import Request


class RequestItemRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, request_id: UUID, data: RequestItemCreate) -> RequestItem:
        item = RequestItem(
            request_id=request_id,
            name=data.name,
            qty=data.qty,
            unit=data.unit,
            notes=data.notes,
        )
        self.session.add(item)
        await self.session.flush()
        return item


    async def get_by_id(self, item_id: UUID) -> RequestItem | None:
        result = await self.session.execute(
            select(RequestItem).where(RequestItem.id == item_id)
        )
        return result.scalar_one_or_none()


    async def get_for_update(self, item_id: UUID) -> RequestItem | None:
        stmt = (
            select(RequestItem)
            .where(RequestItem.id == item_id)
            .with_for_update()
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def get_by_request_id_for_update(self, request_id: UUID) -> list[RequestItem]:
        stmt = (
            select(RequestItem)
            .where(RequestItem.request_id == request_id)
            .with_for_update()
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def get_by_request_id(self, request_id: UUID) -> list[RequestItem]:
        stmt = (
            select(RequestItem)
            .where(RequestItem.request_id == request_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def list_all(self, limit: int, offset: int) -> list[RequestItem]:
        stmt = (
            select(RequestItem)
            .limit(limit)
            .offset(offset)
            .order_by(RequestItem.id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def get_user_items(self, user_id: UUID) -> list[RequestItem]:
        stmt = (
            select(RequestItem)
            .join(Request, RequestItem.request_id == Request.id)
            .where(Request.created_by == user_id)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def list_by_request(self, request_id: UUID) -> list[RequestItem]:
        result = await self.session.execute(
            select(RequestItem).where(RequestItem.request_id == request_id)
        )
        return result.scalars().all()


    async def update(self, item: RequestItem) -> RequestItem:
        self.session.add(item)
        await self.session.flush()
        return item


    async def delete(self, item: RequestItem) -> None:
        await self.session.delete(item)
