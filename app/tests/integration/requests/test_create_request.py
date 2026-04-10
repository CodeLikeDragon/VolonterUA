import pytest
from sqlalchemy import select

from app.auth.schemas import RegisterRequest
from app.requests.requests.schemas import RequestCreate
from app.requests.requests.models import Request

from app.tests.helper import get_auth_service, get_request_service
from app.tests.fixtures.fixtures import verify_user_helper


@pytest.mark.asyncio
async def test_create_request(session, verify_user_helper):
    auth_service = get_auth_service(session)
    request_service = get_request_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )
    await verify_user_helper(session)

    request = await request_service.create_request(
        RequestCreate(title="Test", description="desc"),
        user_id=user.id
    )

    stmt = select(Request).where(Request.id == request.id)
    result = await session.execute(stmt)
    db_request = result.scalar_one()

    assert db_request.title == "Test"
