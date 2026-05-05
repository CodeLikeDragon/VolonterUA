from typing import List
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import AuditEventService
from app.common.enums import RequestStatus
from app.common.errors import NotFoundError, BadRequestError, ConflictError
from app.common.pagination.schemas import PaginationParams
from app.notifications.service import NotificationService
from app.notifications.tasks import create_notification

from app.requests.request_item_assignment.models import RequestItemAssignment
from app.requests.request_item_assignment.repository import RequestItemAssignmentRepository
from app.requests.request_item_assignment.schemas import RequestItemAssignmentUpdate, RequestItemAssignmentCreate
from app.requests.request_item_assignment.utils import _recalculate_request_status

from app.requests.request_items.repository import RequestItemRepository
from app.requests.request_offers.repository import RequestOfferRepository
from app.requests.requests.repository import RequestRepository


class RequestItemAssignmentService:

    def __init__(
        self,
        session: AsyncSession,
        repo: RequestItemAssignmentRepository,
        request_repo: RequestRepository,
        item_repo: RequestItemRepository,
        offer_repo: RequestOfferRepository,
        notification_service: NotificationService,
        audit_service: AuditEventService,
    ):
        self.session = session
        self.repo = repo
        self.request_repo = request_repo
        self.item_repo = item_repo
        self.offer_repo = offer_repo
        self.notification_service = notification_service
        self.audit_service = audit_service

    # -----------------------------
    # CREATE
    # -----------------------------

    async def create(
        self,
        request_item_id: UUID,
        data: RequestItemAssignmentCreate,
        user_id: UUID,
    ) -> RequestItemAssignment:

        if data.qty_taken <= 0:
            raise BadRequestError("Quantity must be greater than zero")

        item = await self.item_repo.get_for_update(request_item_id)
        if not item:
            raise NotFoundError("Request item not found")

        offer = await self.offer_repo.get_for_update(data.offer_id)
        if not offer:
            raise NotFoundError("Offer not found")

        if offer.request_id != item.request_id:
            raise ConflictError("Offer does not belong to this request")

        if not offer.accepted_at:
            raise ConflictError("Offer is not accepted")

        request = await self.request_repo.get_for_update(item.request_id)

        if request.status not in [RequestStatus.NEW, RequestStatus.IN_PROGRESS]:
            raise ConflictError("Request is not active")

        remaining = item.qty - item.assigned_qty

        if data.qty_taken > remaining:
            raise ConflictError("Not enough quantity available")

        try:
            assignment = await self.repo.create(
                request_item_id=request_item_id,
                offer_id=data.offer_id,
                qty_taken=data.qty_taken,
            )

            item.assigned_qty += data.qty_taken

            await _recalculate_request_status(self=self, request_id=request.id)

            await self.session.commit()

        except SQLAlchemyError:
            await self.session.rollback()
            raise


        create_notification.delay(
            user_id=str(user_id),
            title="You were assigned",
            body="You have been assigned to a request",
            meta={
                "request_id": str(request.id),
                "type": "Created"
            }
        )

        create_notification.delay(
            user_id=str(request.created_by),
            title="You have a new assignment",
            body=f"Assignment for your request '{request.title}' has been created.",
            meta={
                "request_id": str(request.id),
                "type": "Created"
            }
        )

        # audit (safe)
        try:
            await self.audit_service.log_event(
                event="assignment_created",
                user_id=user_id,
                data={"assignment_id": str(assignment.id)},
            )
        except Exception:
            pass

        return assignment

    # -----------------------------
    # GET
    # -----------------------------

    async def get_my_assignments(self, user_id: UUID, pagination: PaginationParams) -> List[RequestItemAssignment]:
        return await self.repo.get_my_assignments(user_id, pagination)


    async def get_assignment_by_id(self, assignment_id: UUID) -> RequestItemAssignment:
        assignment = await self.repo.get(assignment_id)

        if not assignment:
            raise NotFoundError("Assignment not found")

        return assignment


    async def get_assignments_by_request_item_id(self, req_item_id: UUID) -> list[RequestItemAssignment]:
        return await self.repo.get_by_request_item_id(req_item_id)


    async def get_assignments_by_offer_id(self, offer_id: UUID) -> list[RequestItemAssignment]:
        return await self.repo.get_by_offer_id(offer_id)


    async def get_assignments(self, limit: int, offset: int) -> list[RequestItemAssignment]:
        return await self.repo.get_list(limit=limit, offset=offset)

    # -----------------------------
    # UPDATE
    # -----------------------------

    async def update_assignment(
        self,
        assignment_id: UUID,
        data: RequestItemAssignmentUpdate,
        user_id: UUID,
    ) -> RequestItemAssignment:

        assignment = await self.repo.get_for_update(assignment_id)
        if not assignment:
            raise NotFoundError("Assignment not found")

        if data.qty_taken is None or data.qty_taken == assignment.qty_taken:
            return assignment

        if data.qty_taken <= 0:
            raise BadRequestError("Quantity must be greater than zero")

        item = await self.item_repo.get_for_update(assignment.request_item_id)
        if not item:
            raise NotFoundError("Item not found")

        request = await self.request_repo.get_for_update(item.request_id)

        if request.status not in [RequestStatus.NEW, RequestStatus.IN_PROGRESS]:
            raise ConflictError("Request is not active")

        old_qty = assignment.qty_taken
        new_qty = data.qty_taken
        delta = new_qty - old_qty

        remaining = item.qty - item.assigned_qty

        if delta > remaining:
            raise ConflictError("Not enough quantity")

        try:
            assignment.qty_taken = new_qty
            item.assigned_qty += delta

            await _recalculate_request_status(self=self, request_id=item.request_id)

            await self.session.commit()

        except SQLAlchemyError:
            await self.session.rollback()
            raise

        try:
            await self.audit_service.log_event(
                event="assignment_updated",
                user_id=user_id,
                data={"assignment_id": str(assignment.id)},
            )
        except Exception:
            pass

        return assignment

    # -----------------------------
    # DELETE
    # -----------------------------

    async def delete(self, assignment_id: UUID, user_id: UUID):

        assignment = await self.repo.get_for_update(assignment_id)
        if not assignment:
            raise NotFoundError("Assignment not found")

        item = await self.item_repo.get_for_update(assignment.request_item_id)
        if not item:
            raise NotFoundError("Item not found")

        request = await self.request_repo.get_for_update(item.request_id)

        if request.status not in [RequestStatus.NEW, RequestStatus.IN_PROGRESS]:
            raise ConflictError("Request is not active")

        try:
            item.assigned_qty = max(0, item.assigned_qty - assignment.qty_taken)

            request_id = item.request_id

            await self.repo.delete(assignment)

            await _recalculate_request_status(self=self, request_id=request_id)

            await self.session.commit()

        except SQLAlchemyError:
            await self.session.rollback()
            raise

        try:
            await self.audit_service.log_event(
                event="assignment_deleted",
                user_id=user_id,
                data={"assignment_id": str(assignment_id)},
            )
        except Exception:
            pass
