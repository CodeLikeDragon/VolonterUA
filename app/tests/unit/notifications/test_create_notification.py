import pytest
from sqlalchemy import select

from uuid import uuid4

from app.notifications.models import Notification
from app.tests.helper import get_notification_service, get_auth_service
from app.auth.schemas import RegisterRequest


@pytest.mark.asyncio
async def test_create_notification(session):
    service = get_notification_service(session)
    auth_service = get_auth_service(session)

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


@pytest.mark.asyncio
async def test_notify_offer_accepted(session):
    service = get_notification_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )

    notification = await service.notify_offer_accepted(
        helper_id=user.id,
        request_id=uuid4()
    )

    stmt = select(Notification).where(Notification.id == notification.id)
    result = await session.execute(stmt)
    db_notification = result.scalars().first()

    assert db_notification.id == notification.id
    assert db_notification.user_id == notification.user_id


@pytest.mark.asyncio
async def test_notify_offer_declined(session):
    service = get_notification_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )

    notification = await service.notify_offer_declined(
        helper_id=user.id,
        request_id=uuid4()
    )

    stmt = select(Notification).where(Notification.id == notification.id)
    result = await session.execute(stmt)
    db_notification = result.scalars().first()

    assert db_notification.id == notification.id
    assert db_notification.user_id == notification.user_id


@pytest.mark.asyncio
async def test_notify_assignment_created(session):
    service = get_notification_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )

    notification = await service.notify_assignment_created(
        user_id=user.id,
        request_id=uuid4()
    )

    stmt = select(Notification).where(Notification.id == notification.id)
    result = await session.execute(stmt)
    db_notification = result.scalars().first()

    assert db_notification.id == notification.id
    assert db_notification.user_id == notification.user_id
