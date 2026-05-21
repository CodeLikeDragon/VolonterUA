from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.notifications.notification_preferences.models import NotificationPreference
from app.notifications.notification_preferences.schemas import NotificationPreferenceCreate


class NotificationPreferenceRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    # -----------------------------
    # CREATE
    # -----------------------------

    async def create(self, user_id: UUID, data: NotificationPreferenceCreate) -> NotificationPreference:
        notif_preference = NotificationPreference(
            user_id = user_id,
            city_id = data.city_id
        )
        self.session.add(notif_preference)
        await self.session.flush()

        return notif_preference

    # -----------------------------
    # GET
    # -----------------------------

    async def get(self, notif_preference_id: UUID) -> NotificationPreference | None:
        stmt = select(NotificationPreference).where(NotificationPreference.id == notif_preference_id)
        result = await self.session.execute(stmt)
        notif_preference = result.scalar_one_or_none()

        return notif_preference


    async def get_my_preferences(self, user_id: UUID) -> list[NotificationPreference]:
        stmt = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        result = await self.session.execute(stmt)
        notif_preferences = result.scalars().all()

        return notif_preferences


    async def get_by_city_id(self, city_id: UUID) -> List[NotificationPreference]:
        stmt = select(NotificationPreference).where(NotificationPreference.city_id == city_id)
        result = await self.session.execute(stmt)
        notif_preferences = result.scalars().all()

        return notif_preferences


    async def list(self, limit: int, offset: int) -> List[NotificationPreference]:
        stmt = (
            select(NotificationPreference)
            .order_by(NotificationPreference.user_id)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        notif_preferences = result.scalars().all()

        return notif_preferences

    # -----------------------------
    # DELETE
    # -----------------------------

    async def delete(self, notif_preference: NotificationPreference) -> None:
        await self.session.delete(notif_preference)
