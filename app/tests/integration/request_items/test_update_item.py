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
from app.requests.request_items.schemas import RequestItemUpdate


@pytest.mark.asyncio
async def test_update_item_flow(session, verify_user_helper):
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

    updated = await item_service.update_item(
        item_id=item.id,
        data=RequestItemUpdate(qty=10),
        user_id=user.id
    )

    assert updated.qty == 10
