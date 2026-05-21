from typing import List
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import AuditEventService
from app.common.errors import NotFoundError, ConflictError, ForbiddenError
from app.geo.cities.repository import CityRepository
from app.notifications.notification_preferences.models import NotificationPreference
from app.notifications.notification_preferences.repository import NotificationPreferenceRepository
from app.notifications.notification_preferences.schemas import NotificationPreferenceCreate


class NotificationPreferencesService:

    def __init__(
        self,
        session: AsyncSession,
        repo: NotificationPreferenceRepository,
        city_repo: CityRepository,
        audit_service: AuditEventService
    ):
        self.session = session
        self.repo = repo
        self.city_repo = city_repo
        self.audit_service = audit_service

    # -----------------------------
    # CREATE
    # -----------------------------

    async def create_notification_preference(self, user_id: UUID, data: NotificationPreferenceCreate) -> NotificationPreference:
        city = await self.city_repo.get_by_id(data.city_id)
        if not city:
            raise NotFoundError("City not found")

        notif_prefer = await self.repo.create(user_id=user_id, data=data)

        try:
            await self.session.commit()
            await self.session.refresh(notif_prefer)

        except IntegrityError:
            await self.session.rollback()

            await self.audit_service.log_event(
                event="create_notification_preference_failed",
                user_id=user_id,
                data={
                    "city_id": data.city_id,
                }
            )
            raise ConflictError("You are already subscribed to this city")

        return notif_prefer

    # -----------------------------
    # GET
    # -----------------------------

    async def get_notif_preference(self, notif_preference_id: UUID) -> NotificationPreference:
        notif_pref = await self.repo.get(notif_preference_id=notif_preference_id)
        if not notif_pref:
            raise NotFoundError("Notification preference not found")
        return notif_pref


    async def get_my_preferences(self, user_id: UUID) -> List[NotificationPreference]:
        return await self.repo.get_my_preferences(user_id=user_id)


    async def get_by_city_id(self, city_id: UUID) -> List[NotificationPreference]:
        return await self.repo.get_by_city_id(city_id=city_id)


    async def get_list(self, limit: int = 50, offset: int = 0) -> List[NotificationPreference]:
        return await self.repo.list(limit=limit, offset=offset)

    # -----------------------------
    # DELETE
    # -----------------------------

    async def delete(self, notification_preference_id: UUID, current_user_id: UUID) -> None:
        notification_preference = await self.get_notif_preference(notification_preference_id)

        if notification_preference.user_id != current_user_id:
            raise ForbiddenError()

        await self.repo.delete(notification_preference)
        await self.session.commit()