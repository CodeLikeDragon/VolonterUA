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

    await service.create_notification(user_id=user.id, title="Test", body="Test body")
    await service.create_notification(user_id=user.id, title="Test", body="Test body")

    count = await service.get_unread_notifications_count(user.id)

    assert count == 2
