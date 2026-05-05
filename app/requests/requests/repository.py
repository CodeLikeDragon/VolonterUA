from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from math import radians, sin, cos, asin, sqrt

from app.common.pagination.schemas import PaginationParams
from app.requests.request_items.models import RequestItem
from app.requests.request_items.schemas import RequestItemOut
from app.requests.requests.models import Request
from app.requests.requests.schemas import RequestCreate, RequestFilters, RequestFiltersOut, RequestOut, _RequestOut


class RequestRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def count(self) -> int:
        stmt = select(func.count(Request.id))
        result = await self.session.execute(stmt)
        return result.scalar_one()


    async def create(self, data: RequestCreate, user_id: UUID) -> Request:
        request = Request(
            title=data.title,
            description=data.description,
            city_id=data.city_id,
            address=data.address,
            created_by=user_id,
            latitude=data.latitude,
            longitude=data.longitude
        )
        self.session.add(request)
        await self.session.flush()
        return request


    async def get_for_update(self, request_id: UUID) -> Request | None:
        stmt = (
            select(Request)
            .where(Request.id == request_id)
            .with_for_update()
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def get_by_id(self, request_id: UUID) -> Request | None:
        stmt = (
            select(Request)
            .where(Request.id == request_id)
            .options(
                selectinload(Request.items),
                selectinload(Request.offers),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def list(self, limit: int, offset: int) -> List[Request]:
        stmt = (
            select(Request)
            .options(
                selectinload(Request.items),
                selectinload(Request.offers),
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def get_user_requests(self, user_id: UUID, pagination: PaginationParams):
        stmt = (
            select(Request)
            .where(Request.created_by == user_id)
            .options(
                selectinload(Request.items),
                selectinload(Request.offers),
            )
            .limit(pagination.limit)
            .offset(pagination.offset)
            .order_by(Request.created_at)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def update(self, request: Request):
        return request


    async def get_filtered(self, filters: RequestFilters, pagination: PaginationParams) -> RequestFiltersOut:

        query = select(Request).options(
            selectinload(Request.items),
            selectinload(Request.offers)
        )

        # filters
        if filters.city_id:
            query = query.where(Request.city_id == filters.city_id)

        if filters.status:
            query = query.where(Request.status == filters.status)

        if filters.search:
            query = query.where(
                or_(
                    Request.title.ilike(f"%{filters.search}%"),
                    Request.description.ilike(f"%{filters.search}%"),
                )
            )

        if filters.has_assignee is True:
            query = query.where(Request.assignee_id.is_not(None))
        elif filters.has_assignee is False:
            query = query.where(Request.assignee_id.is_(None))

        if filters.created_by:
            query = query.where(Request.created_by == filters.created_by)

        if filters.assignee_id:
            query = query.where(Request.assignee_id == filters.assignee_id)

        if filters.created_from:
            query = query.where(Request.created_at >= filters.created_from)

        if filters.created_to:
            query = query.where(Request.created_at <= filters.created_to)

        # sorting
        order_column = Request.created_at

        if filters.order == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        # total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query)

        # pagination
        query = query.limit(pagination.limit).offset(pagination.offset)

        result = await self.session.execute(query)
        filtered_requests: list[Request] = result.scalars().all()

        # items (requests)

        items = [
            RequestOut.model_validate(req)
            for req in filtered_requests
        ]


        return RequestFiltersOut(
            items=items,
            total=total,
            page=pagination.page,
            limit=pagination.limit
        )


    async def get_by_location(self, lat: float, lng: float, radius_km: float, limit: int, offset: int) -> List[Request]:

        result = await self.session.execute(select(Request))
        requests = result.scalars().all()

        return [
            r for r in requests

            if r.latitude is not None
            and r.longitude is not None
            and self._distance(lat, lng, r.latitude, r.longitude) <= radius_km
        ]


    def _distance(self, lat1, lon1, lat2, lon2) -> float:

        # Haversine formula
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        dlon = lon2 - lon1

        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  # km

        return c * r
