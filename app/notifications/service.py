from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.errors import NotFoundError
from app.common.pagination.schemas import PaginationParams
from app.notifications.models import Notification
from app.notifications.repository import NotificationsRepository
from app.notifications.utils import _create_and_commit


class NotificationService:

    def __init__(
        self,
        session: AsyncSession,
        repo: NotificationsRepository,
    ):
        self.session = session
        self.repo = repo


    async def get_my_notifications(self, user_id: UUID, pagination: PaginationParams) -> List[Notification]:
        return await self.repo.get_my_notifications(user_id=user_id, pagination=pagination)


    async def get_user_notification_by_id(self, notification_id: UUID, user_id: UUID) -> Notification:

        notification = await self.repo.get_by_id(notification_id)

        if not notification or notification.user_id != user_id:
            raise NotFoundError("Notification not found")

        return notification


    async def get_user_notifications(self, user_id: UUID, limit: int, offset: int) -> List[Notification]:
        return await self.repo.get_user_notifications(
            user_id=user_id,
            limit=limit,
            offset=offset
        )


    async def get_unread_notifications_count(self, user_id: UUID) -> int:
        return await self.repo.get_unread_count(user_id)


    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> Notification:

        notification = await self.get_user_notification_by_id(
            notification_id,
            user_id
        )

        if notification.read_at:
            return notification

        notification.read_at = datetime.now(timezone.utc)

        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        return notification

    # -----------------------------
    # DOMAIN EVENTS
    # -----------------------------


    async def notify_new_offer(self, request_owner_id: UUID, request_id: UUID) -> Notification:

        notification = Notification(
            user_id=request_owner_id,
            title="New offer",
            body="Someone offered help for your request",
            sent_at=datetime.now(timezone.utc),
            meta={
                "request_id": str(request_id),
                "type": "offer_created"
            }
        )

        return await _create_and_commit(self=self, notification=notification)


    async def notify_offer_accepted(self, helper_id: UUID, request_id: UUID) -> Notification:

        notification = Notification(
            user_id=helper_id,
            title="Offer accepted",
            body="Your help offer was accepted",
            sent_at=datetime.now(timezone.utc),
            meta={
                "request_id": str(request_id),
                "type": "offer_accepted"
            }
        )

        return await _create_and_commit(self=self, notification=notification)


    async def notify_offer_declined(self, helper_id: UUID, request_id: UUID) -> Notification:

        notification = Notification(
            user_id=helper_id,
            title="Offer declined",
            body="Your help offer was declined",
            sent_at=datetime.now(timezone.utc),
            meta={
                "request_id": str(request_id),
                "type": "offer_declined"
            }
        )

        return await _create_and_commit(self=self, notification=notification)


    async def notify_assignment_created(self, user_id: UUID, request_id: UUID) -> Notification:

        notification = Notification(
            user_id=user_id,
            title="You were assigned",
            body="You have been assigned to a request",
            sent_at=datetime.now(timezone.utc),
            meta={
                "request_id": str(request_id),
                "type": "assignment_created"
            }
        )

        return await _create_and_commit(self=self, notification=notification)
