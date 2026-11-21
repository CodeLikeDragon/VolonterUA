from uuid import uuid4

import pytest

from app.auth.schemas import RegisterRequest
from app.common.errors import NotFoundError
from app.common.pagination.schemas import PaginationParams
from app.categories.schemas import CategoryCreate
from app.requests.requests.schemas import RequestCreate, RequestFilters, RequestUpdate
from app.tests.fixtures.fixtures import verify_user_helper
from app.tests.helper import get_auth_service, get_category_service, get_request_service


@pytest.mark.asyncio
async def test_request_categories_can_be_created_filtered_and_replaced(session, verify_user_helper):
    auth_service = get_auth_service(session)
    category_service = get_category_service(session)
    request_service = get_request_service(session)

    user = await auth_service.register(
        RegisterRequest(email="categories@test.com", password="123456")
    )
    await verify_user_helper(session, user.email)

    food = await category_service.create_category(
        CategoryCreate(name="Food", slug="food")
    )
    medicine = await category_service.create_category(
        CategoryCreate(name="Medicine", slug="medicine")
    )

    request = await request_service.create_request(
        RequestCreate(title="Need supplies", category_ids=[food.id, medicine.id]),
        user_id=user.id,
    )

    stored = await request_service.get_request(request.id)
    assert {category.id for category in stored.categories} == {food.id, medicine.id}

    filtered = await request_service.get_filtered_requests(
        RequestFilters(category_ids=[food.id]),
        PaginationParams(page=1, limit=10),
    )
    assert filtered.total == 1
    assert filtered.items[0].id == request.id
    assert {category.id for category in filtered.items[0].categories} == {food.id, medicine.id}

    updated = await request_service.update_request(
        request_id=request.id,
        user_id=user.id,
        data=RequestUpdate(category_ids=[medicine.id]),
    )
    assert [category.id for category in updated.categories] == [medicine.id]


@pytest.mark.asyncio
async def test_request_cannot_reference_a_missing_category(session, verify_user_helper):
    auth_service = get_auth_service(session)
    request_service = get_request_service(session)

    user = await auth_service.register(
        RegisterRequest(email="missing-category@test.com", password="123456")
    )
    await verify_user_helper(session, user.email)

    with pytest.raises(NotFoundError):
        await request_service.create_request(
            RequestCreate(title="Need supplies", category_ids=[uuid4()]),
            user_id=user.id,
        )
