from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import AuditEventService
from app.common.errors import NotFoundError, BadRequestError
from app.requests.request_items.models import RequestItem
from app.requests.request_items.repository import RequestItemRepository
from app.requests.request_items.schemas import RequestItemCreate, RequestItemUpdate
from app.requests.request_items.utils import validate_request
from app.requests.requests.repository import RequestRepository


class RequestItemService:

    def __init__(
        self,
        session: AsyncSession,
        item_repo: RequestItemRepository,
        request_repo: RequestRepository,
        audit_service: AuditEventService,
    ):
        self.session = session
        self.item_repo = item_repo
        self.request_repo = request_repo
        self.audit_service = audit_service

    # -----------------------------
    # GET
    # -----------------------------

    async def get_item(self, item_id: UUID) -> RequestItem:
        item = await self.item_repo.get_by_id(item_id)
        if not item:
            raise NotFoundError("Item not found")
        return item


    async def get_all_items(self, limit: int, offset: int):
        return await self.item_repo.list_all(limit=limit, offset=offset)


    async def get_user_items(self, user_id: UUID):
        return await self.item_repo.get_user_items(user_id)

    # -----------------------------
    # CREATE
    # -----------------------------

    async def create_item(
        self,
        request_id: UUID,
        data: RequestItemCreate,
        user_id: UUID,
    ) -> RequestItem:

        if data.qty is None or data.qty <= 0:
            raise BadRequestError("Quantity must be greater than zero")

        request = await self.request_repo.get_by_id(request_id)
        validate_request(request=request, user_id=user_id)

        try:
            item = await self.item_repo.create(request_id, data)

            await self.session.commit()

        except SQLAlchemyError:
            await self.session.rollback()
            raise

        try:
            await self.audit_service.log_event(
                event="request_item_created",
                user_id=user_id,
                data={"item_id": str(item.id)},
            )
        except Exception:
            pass

        return item

    # -----------------------------
    # UPDATE
    # -----------------------------

    async def update_item(
        self,
        item_id: UUID,
        data: RequestItemUpdate,
        user_id: UUID,
    ) -> RequestItem:

        item = await self.get_item(item_id)
        request = await self.request_repo.get_by_id(item.request_id)

        validate_request(request=request, user_id=user_id)

        updates = data.model_dump(exclude_unset=True)

        if not updates:
            return item

        if "qty" in updates:
            if updates["qty"] is None or updates["qty"] <= 0:
                raise BadRequestError("Quantity must be greater than zero")

        try:
            for key, value in updates.items():
                setattr(item, key, value)

            await self.item_repo.update(item)

            await self.session.commit()

        except SQLAlchemyError:
            await self.session.rollback()
            raise

        try:
            await self.audit_service.log_event(
                event="request_item_updated",
                user_id=user_id,
                data={"item_id": str(item.id)},
            )
        except Exception:
            pass

        return item

    # -----------------------------
    # DELETE
    # -----------------------------

    async def delete_item(
        self,
        item_id: UUID,
        user_id: UUID,
    ) -> None:

        item = await self.get_item(item_id)
        request = await self.request_repo.get_by_id(item.request_id)

        validate_request(request=request, user_id=user_id)

        try:
            await self.item_repo.delete(item)
            await self.session.commit()

        except SQLAlchemyError:
            await self.session.rollback()
            raise

        try:
            await self.audit_service.log_event(
                event="request_item_deleted",
                user_id=user_id,
                data={"item_id": str(item.id)},
            )
        except Exception:
            pass
