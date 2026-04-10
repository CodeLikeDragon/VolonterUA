import pytest
from sqlalchemy import select

from app.audit.models import AuditEvent
from app.auth.schemas import RegisterRequest
from app.tests.helper import get_auth_service
from app.tests.fixtures.fixtures import verify_user_helper


@pytest.mark.asyncio
async def test_audit_event_on_register(session):
    auth_service = get_auth_service(session)

    await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    stmt = select(AuditEvent)
    result = await session.execute(stmt)
    events = result.scalars().all()

    assert len(events) > 0


@pytest.mark.asyncio
async def test_audit_event_on_login(session, verify_user_helper):
    auth_service = get_auth_service(session)

    await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await verify_user_helper(session)

    await auth_service.login(
        email="test@test.com",
        password="123456"
    )

    stmt = select(AuditEvent).where(
        AuditEvent.event == "login_success"
    )
    result = await session.execute(stmt)
    event = result.scalars().first()

    assert event is not None
