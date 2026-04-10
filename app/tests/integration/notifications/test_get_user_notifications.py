import pytest
from uuid import uuid4

from app.auth.schemas import RegisterRequest
from app.tests.helper import get_auth_service, get_notification_service


@pytest.mark.asyncio
async def test_get_user_notifications_flow(session):
    auth_service = get_auth_service(session)
    service = get_notification_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )

    await service.notify_new_offer(user.id, uuid4())
    await service.notify_new_offer(user.id, uuid4())

    notifications = await service.get_user_notifications(user.id)

    assert len(notifications) == 2
