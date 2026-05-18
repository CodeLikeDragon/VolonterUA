from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.chats.messages.models import Message
from app.common.errors import NotFoundError
from app.common.pagination.schemas import PaginationParams
from app.notifications.notifications.models import Notification
from app.notifications.repository import NotificationsRepository


class NotificationService:

    def __init__(
        self,
        session: AsyncSession,
        repo: NotificationsRepository,
    ):
        self.session = session
        self.repo = repo


    async def create_smart_notification(
        self,
        recipient: UUID,
        data: Message
    ) -> Notification:

        notification = Notification(
            user_id=recipient,
            title="New message",
            body=data.text or "Sent an attachment",
            sent_at=datetime.now(timezone.utc),
            meta={
                "chat_id": str(data.chat_id),
                "message_id": str(data.id),
                "created_at": data.created_at.isoformat()
            }
        )
        notification = await self.repo.create(notification)

        await self.session.commit()

        return notification


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
