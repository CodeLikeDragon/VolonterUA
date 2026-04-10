import pytest
from uuid import uuid4

from app.auth.schemas import RegisterRequest
from app.tests.helper import get_auth_service, get_notification_service


@pytest.mark.asyncio
async def test_unread_notifications_count_flow(session):
    auth_service = get_auth_service(session)
    service = get_notification_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )

    await service.notify_new_offer(user.id, uuid4())
    await service.notify_new_offer(user.id, uuid4())

    count = await service.get_unread_notifications_count(user.id)

    assert count == 2
