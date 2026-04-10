import pytest

from uuid import uuid4

from app.tests.helper import get_notification_service, get_auth_service
from app.auth.schemas import RegisterRequest


@pytest.mark.asyncio
async def test_mark_as_read(session):
    service = get_notification_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )

    notification = await service.notify_new_offer(
        request_owner_id=user.id,
        request_id=uuid4()
    )

    await service.mark_as_read(notification_id=notification.id, user_id=user.id)

    assert notification.read_at is not None
