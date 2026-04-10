import pytest

from app.auth.schemas import RegisterRequest
from app.requests.requests.schemas import RequestCreate
from app.requests.request_items.schemas import RequestItemCreate

from app.tests.helper import (
    get_auth_service,
    get_request_service,
    get_request_item_service,
)
from app.tests.fixtures.fixtures import verify_user_helper
from app.common.errors import NotFoundError


@pytest.mark.asyncio
async def test_delete_item_flow(session, verify_user_helper):
    auth_service = get_auth_service(session)
    request_service = get_request_service(session)
    item_service = get_request_item_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )
    await verify_user_helper(session)

    request = await request_service.create_request(
        RequestCreate(title="Test", description="desc"),
        user_id=user.id
    )

    item = await item_service.create_item(
        request_id=request.id,
        data=RequestItemCreate(name="Item", qty=5),
        user_id=user.id
    )

    await item_service.delete_item(item.id, user_id=user.id)

    with pytest.raises(NotFoundError):
        await item_service.get_item(item.id)
