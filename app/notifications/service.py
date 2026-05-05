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
