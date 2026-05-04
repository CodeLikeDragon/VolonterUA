from typing import Optional, Tuple
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import RequestStatus
from app.common.errors import NotFoundError, ForbiddenError, ConflictError, BadRequestError
from app.audit.service import AuditEventService
from app.common.pagination.schemas import PaginationParams
from app.requests.request_item_assignment.repository import RequestItemAssignmentRepository
from app.requests.request_items.repository import RequestItemRepository
from app.requests.request_offers.repository import RequestOfferRepository

from app.requests.requests.models import Request
from app.requests.requests.repository import RequestRepository
from app.requests.requests.schemas import RequestCreate, RequestUpdate, RequestFilters, RequestFiltersOut, \
    RequestFullOut, _RequestOut
from app.users.users.repository import UserRepository


class RequestService:

    def __init__(
        self,
        session: AsyncSession,
        repo: RequestRepository,
        item_repo: RequestItemRepository,
        offer_repo: RequestOfferRepository,
        assignment_repo: RequestItemAssignmentRepository,
        user_repo: UserRepository,
        audit_service: AuditEventService
    ):
        self.session = session
        self.repo = repo
        self.item_repo = item_repo
        self.offer_repo = offer_repo
        self.assignment_repo = assignment_repo
        self.user_repo = user_repo
        self.audit_service = audit_service

    # -----------------------------
    # CREATE
    # -----------------------------
    async def create_request(self, data: RequestCreate, user_id: UUID) -> Request:
        try:
            request = await self.repo.create(data, user_id)
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise ConflictError("Failed to create request")

        await self.audit_service.log_event(
            event="request_created",
            user_id=user_id,
            data={"request_id": str(request.id)},
        )

        return request

    # -----------------------------
    # GET
    # -----------------------------
    async def get_request(self, request_id: UUID) -> Request:
        request = await self.repo.get_by_id(request_id)

        if not request:
            raise NotFoundError("Request not found")

        return request


    async def get_requests(self, limit: int, offset: int):
        limit = min(limit, 100)

        requests = await self.repo.list(limit, offset)
        total = await self.repo.count()

        return requests, total


    async def get_user_requests(self, user_id: UUID, pagination: PaginationParams):
        return await self.repo.get_user_requests(user_id, pagination)


    async def get_filtered_requests(self, filters: RequestFilters, pagination: PaginationParams) -> RequestFiltersOut:
        return await self.repo.get_filtered(filters=filters, pagination=pagination)


    async def get_full_request(self, request_id: UUID):
        request = await self.repo.get_by_id(request_id)

        if not request:
            raise NotFoundError("Request not found")

        request_out = _RequestOut(
            id=request.id,
            title=request.title,
            description=request.description,
            city_id=request.city_id,
            address=request.address,
            status=request.status,
            created_by=request.created_by,
            assignee_id=request.assignee_id,
            created_at=request.created_at,
            updated_at=request.updated_at
        )

        # --- основні дані ---
        items = await self.item_repo.get_by_request_id(request_id)
        offers = await self.offer_repo.get_by_request_id(request_id)
        assignments = await self.assignment_repo.get_by_request_id(request_id)

        # --- creator ---
        request_creator = await self.user_repo.get_by_id(request.created_by)
        if not request_creator:
            raise NotFoundError("Request creator not found")

        # --- offer creators (оптимізовано) ---
        offer_user_ids = list({offer.user_id for offer in offers})

        offer_users = []
        if offer_user_ids:
            offer_users = await self.user_repo.get_by_ids(offer_user_ids)

        users_map = {user.id: user for user in offer_users}

        request_offer_creators = {
            user.id: user for user in offer_users
        }

        # --- counts ---
        offers_count = len(offers)
        items_count = len(items)
        assignments_count = len(assignments)

        return RequestFullOut(
            request=request_out,
            request_items=items,
            request_offers=offers,
            request_item_assignments=assignments,
            request_creator=request_creator,
            request_offer_creators=request_offer_creators,
            offers_count=offers_count,
            items_count=items_count,
            assignments_count=assignments_count
        )


    async def get_geo_requests(self, near: str, radius: float, pagination: PaginationParams) -> RequestFiltersOut:

        radius_km = self._parse_radius(radius)

        lat, lng = self._parse_near(near)
        return await self.repo.get_by_location(
            lat=lat,
            lng=lng,
            radius_km=radius_km,
            limit=pagination.limit,
            offset=pagination.offset
        )

        return await self.repo.list(limit=pagination.limit, offset=pagination.offset)


    def _parse_near(self, near: str) -> Tuple[float, float]:

        if not near:
            raise BadRequestError("Please provide required coordinates")

        try:
            lat_str, lng_str = near.split(",")
            lat = float(lat_str)
            lng = float(lng_str)
        except Exception:
            raise ValueError("Invalid near format. Use lat,lng")

        if not (-90 <= lat <= 90):
            raise ValueError("Invalid latitude")

        if not (-180 <= lng <= 180):
            raise ValueError("Invalid longitude")

        return lat, lng


    def _parse_radius(self, radius: float) -> float:

        try:
            radius = float(radius)
        except Exception:
            raise ValueError("Invalid radius")

        if radius < 0:
            raise BadRequestError("Please provide correct radius value")

        return float(radius)

    # -----------------------------
    # UPDATE
    # -----------------------------
    async def update_request(
        self,
        *,
        request_id: UUID,
        user_id: UUID,
        data: RequestUpdate,
    ) -> Request:

        request = await self.repo.get_for_update(request_id)

        if not request:
            raise NotFoundError("Request not found")

        if request.created_by != user_id:
            raise ForbiddenError("You cannot update this request")

        if request.status != RequestStatus.NEW:
            raise ConflictError("Cannot update non-active request")

        # partial update
        if data.title is not None:
            request.title = data.title

        if data.description is not None:
            request.description = data.description

        if data.address is not None:
            request.address = data.address

        if data.city_id is not None:
            request.city_id = data.city_id

        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        await self.audit_service.log_event(
            event="request_updated",
            user_id=user_id,
            data={"request_id": str(request.id)},
        )

        return request


    async def cancel_request(self, request_id: UUID, user_id) -> Request:
        request = await self.repo.get_for_update(request_id)
        if not request:
            raise NotFoundError("Request not found")

        if request.created_by != user_id:
            raise ForbiddenError("You cannot cancel this request")

        try:
            request.status = RequestStatus.CANCELED
            await self.session.commit()
            return request
        except Exception:
            await self.session.rollback()
            raise
