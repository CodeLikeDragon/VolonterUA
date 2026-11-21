import pytest
from sqlalchemy import select

from uuid import uuid4

from app.notifications.notifications.models import Notification
from app.tests.helper import get_notification_service, get_auth_service
from app.auth.schemas import RegisterRequest


@pytest.mark.asyncio
async def test_create_notification(session):
    service = get_notification_service(session)
    auth_service = get_auth_service(session)
    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )

    notification = await service.create_notification(
        user_id=user.id,
        title="New offer",
        body="You have a new offer",
        meta={"request_id": str(uuid4())},
    )

    assert notification.id is not None
    assert notification.user_id == user.id
    assert notification.title == "New offer"
    assert notification.read_at is None
