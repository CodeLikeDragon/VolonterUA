import pytest
from uuid import uuid4
from sqlalchemy import select

from app.audit.models import AuditEvent
from app.auth.schemas import RegisterRequest
from app.tests.helper import get_audit_service, get_auth_service


@pytest.mark.asyncio
async def test_log_event(session):
    service = get_audit_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await service.log_event(
        event="test_event",
        user_id=user.id,
        data={"key": "value"}
    )

    stmt = select(AuditEvent)
    result = await session.execute(stmt)
    audit = result.scalars().first()

    assert audit is not None


@pytest.mark.asyncio
async def test_log_event_without_user(session):
    service = get_audit_service(session)

    await service.log_event(
        event="anonymous_event"
    )

    stmt = select(AuditEvent)
    result = await session.execute(stmt)
    audit = result.scalars().first()

    assert audit.user_id is None
    assert audit.event == "anonymous_event"
