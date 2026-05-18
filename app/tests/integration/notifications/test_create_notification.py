import pytest
from sqlalchemy import select
from uuid import uuid4

from app.auth.schemas import RegisterRequest
from app.notifications.notifications.models import Notification
from app.tests.helper import get_auth_service, get_notification_service


@pytest.mark.asyncio
async def test_notify_new_offer_flow(session):
    auth_service = get_auth_service(session)
    service = get_notification_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )

    notification = await service.notify_new_offer(
        request_owner_id=user.id,
        request_id=uuid4()
    )

    stmt = select(Notification).where(Notification.id == notification.id)
    result = await session.execute(stmt)
    db_notification = result.scalars().first()

    assert db_notification is not None
    assert db_notification.user_id == user.id
