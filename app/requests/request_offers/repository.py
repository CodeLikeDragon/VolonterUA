from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination.schemas import PaginationParams
from app.requests.request_offers.models import RequestOffer
from app.requests.request_offers.schemas import RequestOfferCreate


class RequestOfferRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        *,
        user_id: UUID,
        request_id: UUID,
        data: RequestOfferCreate,
    ) -> RequestOffer:

        offer = RequestOffer(
            user_id=user_id,
            request_id=request_id,
            message=data.message,
        )

        self.session.add(offer)
        await self.session.flush()

        return offer


    async def get_my_offers(self, user_id: UUID, pagination: PaginationParams) -> list[RequestOffer]:
        stmt = (select(RequestOffer)
                .where(RequestOffer.user_id == user_id)
                .limit(pagination.limit)
                .offset(pagination.offset)
                .order_by(RequestOffer.id)
                )
        result = await self.session.execute(stmt)
        offers = result.scalars().all()

        return offers



    async def get_for_update(self, offer_id: UUID) -> RequestOffer | None:
        stmt = (
            select(RequestOffer)
            .where(RequestOffer.id == offer_id)
            .with_for_update()
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def get_by_id(self, offer_id: UUID) -> RequestOffer | None:
        stmt = select(RequestOffer).where(RequestOffer.id == offer_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def get_by_request_id(self, request_id: UUID) -> list[RequestOffer]:
        stmt = select(RequestOffer).where(RequestOffer.request_id == request_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def list_request_offers(self, limit: int, offset: int) -> list[RequestOffer]:
        stmt = (
            select(RequestOffer)
            .offset(offset).
            limit(limit)
            .order_by(RequestOffer.id)
        )
        result = await self.session.execute(stmt)
        offers = result.scalars().all()
        return offers


    async def list_accepted(self) -> list[RequestOffer]:
        stmt = select(RequestOffer).where(RequestOffer.accepted_at.is_not(None))
        result = await self.session.execute(stmt)
        offers = result.scalars().all()
        return offers


    async def list_declined(self) -> list[RequestOffer]:
        stmt = select(RequestOffer).where(RequestOffer.declined_at.is_not(None))
        result = await self.session.execute(stmt)
        offers = result.scalars().all()
        return offers


    async def delete(self, offer: RequestOffer) -> None:
        await self.session.delete(offer)
