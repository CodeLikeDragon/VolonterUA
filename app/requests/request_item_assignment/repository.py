from uuid import UUID
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination.schemas import PaginationParams
from app.requests.request_item_assignment.models import RequestItemAssignment
from app.requests.request_items.models import RequestItem
from app.requests.request_offers.models import RequestOffer


class RequestItemAssignmentRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(
        self,
        *,
        request_item_id: UUID,
        offer_id: UUID,
        qty_taken: Decimal,
    ) -> RequestItemAssignment:

        assignment = RequestItemAssignment(
            request_item_id=request_item_id,
            offer_id=offer_id,
            qty_taken=qty_taken,
        )

        self.session.add(assignment)
        await self.session.flush()

        return assignment


    async def get_my_assignments(self, user_id: UUID, pagination: PaginationParams) -> list[RequestItemAssignment]:
        stmt = (
            select(RequestItemAssignment)
            .join(RequestItem, RequestItemAssignment.request_item_id == RequestItem.id)
            .join(RequestOffer, RequestItemAssignment.offer_id == RequestOffer.id)
            .where(RequestOffer.user_id == user_id)
            .limit(pagination.limit)
            .offset(pagination.offset)
            .order_by(RequestItemAssignment.taken_at.asc())
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def get(self, assignment_id: UUID) -> RequestItemAssignment | None:
        result = await self.session.execute(
            select(RequestItemAssignment).where(RequestItemAssignment.id == assignment_id)
        )
        return result.scalar_one_or_none()


    async def get_for_update(self, assignment_id: UUID) -> RequestItemAssignment | None:
        result = await self.session.execute(
            select(RequestItemAssignment)
            .where(RequestItemAssignment.id == assignment_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()


    async def get_by_request_item_id(self, request_item_id: UUID) -> list[RequestItemAssignment]:
        result = await self.session.execute(
            select(RequestItemAssignment)
            .where(RequestItemAssignment.request_item_id == request_item_id)
            .order_by(RequestItemAssignment.taken_at.asc())
        )
        return result.scalars().all()


    async def get_by_offer_id(self, offer_id: UUID) -> list[RequestItemAssignment]:
        result = await self.session.execute(
            select(RequestItemAssignment)
            .where(RequestItemAssignment.offer_id == offer_id)
        )
        return result.scalars().all()


    async def get_by_request_id(self, request_id: UUID) -> list[RequestItemAssignment]:
        result = await self.session.execute(
            select(RequestItemAssignment)
            .join(RequestItem, RequestItemAssignment.request_item_id == RequestItem.id)
            .where(RequestItem.id == request_id)
        )
        return result.scalars().all()


    async def get_list(self, limit: int, offset: int):
        result = await self.session.execute(
            select(RequestItemAssignment)
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()


    async def delete(self, assignment: RequestItemAssignment) -> None:
        await self.session.delete(assignment)
        await self.session.flush()
