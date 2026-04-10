import pytest

from app.auth.schemas import RegisterRequest
from app.requests.requests.schemas import RequestCreate
from app.requests.request_offers.schemas import RequestOfferCreate

from app.tests.helper import (
    get_auth_service,
    get_request_service,
    get_request_offer_service
)
from app.tests.fixtures.fixtures import verify_user_helper


@pytest.mark.asyncio
async def test_decline_offer_flow(session, verify_user_helper):
    auth_service = get_auth_service(session)
    request_service = get_request_service(session)
    offer_service = get_request_offer_service(session)

    owner = await auth_service.register(
        RegisterRequest(email="owner@test.com", password="123456")
    )
    helper = await auth_service.register(
        RegisterRequest(email="helper@test.com", password="123456")
    )

    await verify_user_helper(session, email="owner@test.com")
    await verify_user_helper(session, email="helper@test.com")

    request = await request_service.create_request(
        RequestCreate(title="Test", description="desc"),
        user_id=owner.id
    )

    offer = await offer_service.create_request_offer(
        user_id=helper.id,
        request_id=request.id,
        data=RequestOfferCreate(message="help"),
    )

    declined = await offer_service.decline_offer(
        offer_id=offer.id,
        user_id=owner.id,
    )

    assert declined.declined_at is not None


from app.common.errors import NotFoundError


@pytest.mark.asyncio
async def test_delete_offer_flow(session, verify_user_helper):
    auth_service = get_auth_service(session)
    request_service = get_request_service(session)
    offer_service = get_request_offer_service(session)

    owner = await auth_service.register(
        RegisterRequest(email="owner@test.com", password="123456")
    )
    helper = await auth_service.register(
        RegisterRequest(email="helper@test.com", password="123456")
    )

    await verify_user_helper(session, email="owner@test.com")
    await verify_user_helper(session, email="helper@test.com")

    request = await request_service.create_request(
        RequestCreate(title="Test", description="desc"),
        user_id=owner.id
    )

    offer = await offer_service.create_request_offer(
        user_id=helper.id,
        request_id=request.id,
        data=RequestOfferCreate(message="help"),
    )

    await offer_service.delete_request_offer(
        offer_id=offer.id,
        user_id=helper.id,
    )

    with pytest.raises(NotFoundError):
        await offer_service.get_request_offer(offer.id)
