import pytest

from uuid import uuid4

from app.common.errors import NotFoundError
from app.common.pagination.schemas import PaginationParams
from app.tests.helper import get_notification_service, get_auth_service
from app.auth.schemas import RegisterRequest


@pytest.mark.asyncio
async def test_get_my_notifications(session):
    service = get_notification_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )

    notification = await service.notify_new_offer(
        request_owner_id=user.id,
        request_id=uuid4()
    )

    pagination_params = PaginationParams(
        page=1,
        limit=5
    )

    notifications = await service.get_my_notifications(user_id=user.id, pagination=pagination_params)

    assert len(notifications) == 1
    assert notifications[0].id == notification.id


@pytest.mark.asyncio
async def test_get_notification_by_id(session):
    service = get_notification_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )

    notification = await service.notify_new_offer(
        request_owner_id=user.id,
        request_id=uuid4()
    )

    result = await service.get_user_notification_by_id(notification_id=notification.id, user_id=user.id)

    assert result.id == notification.id


@pytest.mark.asyncio
async def test_get_notification_not_found(session):
    service = get_notification_service(session)

    with pytest.raises(NotFoundError):
        await service.get_user_notification_by_id(uuid4(), uuid4())


@pytest.mark.asyncio
async def test_unread_count(session):
    service = get_notification_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )

    await service.notify_new_offer(user.id, uuid4())
    await service.notify_new_offer(user.id, uuid4())

    count = await service.get_unread_notifications_count(user.id)

    assert count == 2
