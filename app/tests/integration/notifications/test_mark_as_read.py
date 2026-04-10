import pytest
from uuid import uuid4

from app.auth.schemas import RegisterRequest
from app.tests.helper import get_auth_service, get_notification_service


@pytest.mark.asyncio
async def test_mark_notification_as_read_flow(session):
    auth_service = get_auth_service(session)
    service = get_notification_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )

    notification = await service.notify_new_offer(user.id, uuid4())

    await service.mark_as_read(notification.id)

    assert notification.read_at is not None
