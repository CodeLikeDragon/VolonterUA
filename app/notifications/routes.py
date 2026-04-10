from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.common.pagination.schemas import PaginationParams
from app.core.deps import get_notification_service, get_current_user_id, get_current_user
from app.notifications.schemas import NotificationOut
from app.notifications.service import NotificationService
from app.common.errors import NotFoundError
from app.users.users.models import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationOut])
async def get_my_notifications(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: UUID = Depends(get_current_user_id),
    service: NotificationService = Depends(get_notification_service)
):
    return await service.get_user_notifications(
        user_id=user_id,
        limit=limit,
        offset=offset,
    )


@router.get("/me")
async def get_my_notifications(
    pagination: PaginationParams = Depends(),
    user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    return await service.get_my_notifications(user.id, pagination)


@router.get("/unread-count", response_model=int)
async def get_unread_notifications_count(
    user_id: UUID = Depends(get_current_user_id),
    service: NotificationService = Depends(get_notification_service)
):
    return await service.get_unread_notifications_count(user_id)


@router.get("/{notification_id}", response_model=NotificationOut)
async def get_notification_by_id(
    notification_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: NotificationService = Depends(get_notification_service)
):
    return await service.get_user_notification_by_id(
        notification_id=notification_id,
        user_id=user_id
    )


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationOut,
    status_code=status.HTTP_200_OK,
)
async def mark_as_read(
    notification_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: NotificationService = Depends(get_notification_service)
):
    return await service.mark_as_read(
        notification_id=notification_id,
        user_id=user_id
    )
