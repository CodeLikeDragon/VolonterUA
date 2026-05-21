from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.common.pagination.pagination import get_pagination_params
from app.common.pagination.schemas import PaginationParams
from app.core.deps import get_notification_preferences_service, get_current_user_id
from app.notifications.notification_preferences.schemas import NotificationPreferenceOut, NotificationPreferenceCreate
from app.notifications.notification_preferences.service import NotificationPreferencesService

router = APIRouter(prefix="/notification-preferences", tags=["Notifications | Notification Preferences"])


@router.post("", response_model=NotificationPreferenceOut)
async def create_notification_preference(
    data: NotificationPreferenceCreate,
    user_id: UUID = Depends(get_current_user_id),
    service: NotificationPreferencesService = Depends(get_notification_preferences_service)
):
    return await service.create_notification_preference(user_id=user_id, data=data)


@router.get("/me", response_model=List[NotificationPreferenceOut])
async def get_user_notification_preferences(
    user_id: UUID = Depends(get_current_user_id),
    service: NotificationPreferencesService = Depends(get_notification_preferences_service)
):
    return await service.get_my_preferences(user_id)


@router.get("/cities/{city_id}", response_model=List[NotificationPreferenceOut])
async def get_cities_notification_preferences(
    city_id: UUID,
    service: NotificationPreferencesService = Depends(get_notification_preferences_service)
):
    return await service.get_by_city_id(city_id)


@router.get("/{notif_pref_id}", response_model=NotificationPreferenceOut)
async def get_notification_preference(
    notif_pref_id: UUID,
    service: NotificationPreferencesService = Depends(get_notification_preferences_service)
):
    return await service.get_notif_preference(notif_pref_id)


@router.get("", response_model=List[NotificationPreferenceOut])
async def get_all_notification_preferences(
    pagination: PaginationParams = Depends(get_pagination_params),
    service: NotificationPreferencesService = Depends(get_notification_preferences_service)
):
    return await service.get_list(limit=pagination.limit, offset=pagination.offset)


@router.delete("/{notification_preference_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification_preference(
    notification_preference_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: NotificationPreferencesService = Depends(get_notification_preferences_service)
):
    return await service.delete(notification_preference_id=notification_preference_id, current_user_id=user_id)
