from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination.schemas import PaginationParams
from app.notifications.notifications.models import Notification


class NotificationsRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_my_notifications(self, user_id: UUID, pagination: PaginationParams) -> list[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .limit(pagination.limit)
            .offset(pagination.offset)
            .order_by(Notification.sent_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def get_by_id(self, notification_id: UUID) -> Notification | None:
        stmt = select(Notification).where(Notification.id == notification_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def get_user_notifications(self, user_id: UUID):
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.sent_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def get_unread_count(self, user_id: UUID) -> int:
        stmt = (
            select(func.count(Notification.id))
            .where(
                Notification.user_id == user_id,
                Notification.read_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()


    async def create(self, notification: Notification):
        self.session.add(notification)
        return notification
