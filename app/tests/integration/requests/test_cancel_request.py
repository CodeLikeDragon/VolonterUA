import pytest

from sqlalchemy import select
from datetime import datetime, timezone

from app.auth.schemas import RegisterRequest
from app.common.errors import ForbiddenError, ConflictError
from app.geo.countries.schemas import CountryCreate
from app.geo.cities.schemas import CityCreate
from app.requests.request_items.schemas import RequestItemCreate
from app.requests.request_offers.schemas import RequestOfferCreate
from app.requests.request_item_assignment.schemas import RequestItemAssignmentCreate
from app.requests.request_item_assignment.models import RequestItemAssignment
from app.requests.requests.schemas import RequestCreate

from app.tests.helper import (
    get_country_service,
    get_city_service,
    get_request_item_service,
    get_request_offer_service,
    get_request_item_assignment_service,
    get_auth_service,
    get_request_service
)
from app.tests.fixtures.fixtures import verify_user_helper


@pytest.mark.asyncio
async def test_cancel_request_flow(session, verify_user_helper):
    auth_service = get_auth_service(session)
    request_service = get_request_service(session)
    country_service = get_country_service(session)
    city_service = get_city_service(session)
    item_service = get_request_item_service(session)
    offer_service = get_request_offer_service(session)
    assignment_service = get_request_item_assignment_service(session)

    owner = await auth_service.register(
        RegisterRequest(email="owner@test.com", password="123456")
    )
    helper = await auth_service.register(
        RegisterRequest(email="helper@test.com", password="123456")
    )

    await verify_user_helper(session, email="owner@test.com")
    await verify_user_helper(session, email="helper@test.com")

    country = await country_service.create_country(
        CountryCreate(name="Germany", iso_code="DE")
    )

    city = await city_service.create_city(
        CityCreate(
            name="Berlin",
            region="Berlin",
            timezone="Europe/Berlin",
            country_id=country.id,
        )
    )

    request = await request_service.create_request(
        RequestCreate(title="Test", city_id=city.id),
        user_id=owner.id
    )

    item = await item_service.create_item(
        request_id=request.id,
        data=RequestItemCreate(name="Water", qty=5),
        user_id=owner.id
    )

    offer = await offer_service.create_request_offer(
        user_id=helper.id,
        request_id=request.id,
        data=RequestOfferCreate(message="help"),
    )

    # accept
    offer.accepted_at = datetime.now(timezone.utc)
    await session.commit()

    # assignment
    await assignment_service.create(
        request_item_id=item.id,
        data=RequestItemAssignmentCreate(
            offer_id=offer.id,
            qty_taken=2,
        ),
        user_id=helper.id,
    )

    # cancel
    canceled = await request_service.cancel_request(
        request_id=request.id,
        user_id=owner.id,
    )

    assert canceled.status.name == "CANCELED"


@pytest.mark.asyncio
async def test_cancel_request_removes_assignments(session, verify_user_helper):
    auth_service = get_auth_service(session)
    request_service = get_request_service(session)
    item_service = get_request_item_service(session)
    offer_service = get_request_offer_service(session)
    assignment_service = get_request_item_assignment_service(session)

    owner = await auth_service.register(
        RegisterRequest(email="owner@test.com", password="123456")
    )
    helper = await auth_service.register(
        RegisterRequest(email="helper@test.com", password="123456")
    )

    await verify_user_helper(session, email="owner@test.com")
    await verify_user_helper(session, email="helper@test.com")

    request = await request_service.create_request(
        RequestCreate(title="Test"),
        user_id=owner.id
    )

    item = await item_service.create_item(
        request_id=request.id,
        data=RequestItemCreate(name="Item", qty=5),
        user_id=owner.id
    )

    offer = await offer_service.create_request_offer(
        user_id=helper.id,
        request_id=request.id,
        data=RequestOfferCreate(message="help"),
    )

    offer.accepted_at = datetime.now(timezone.utc)
    await session.commit()

    assignment = await assignment_service.create(
        request_item_id=item.id,
        data=RequestItemAssignmentCreate(
            offer_id=offer.id,
            qty_taken=2,
        ),
        user_id=helper.id,
    )

    await request_service.cancel_request(request.id, owner.id)

    stmt = select(RequestItemAssignment).where(
        RequestItemAssignment.id == assignment.id
    )
    result = await session.execute(stmt)

    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_cancel_request_forbidden(session, verify_user_helper):
    auth_service = get_auth_service(session)
    request_service = get_request_service(session)

    owner = await auth_service.register(
        RegisterRequest(email="owner@test.com", password="123456")
    )
    other = await auth_service.register(
        RegisterRequest(email="other@test.com", password="123456")
    )

    await verify_user_helper(session, email="owner@test.com")
    await verify_user_helper(session, email="other@test.com")

    request = await request_service.create_request(
        RequestCreate(title="Test"),
        user_id=owner.id
    )

    with pytest.raises(ForbiddenError):
        await request_service.cancel_request(request.id, other.id)


@pytest.mark.asyncio
async def test_cancel_request_already_canceled(session, verify_user_helper):
    auth_service = get_auth_service(session)
    request_service = get_request_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )
    await verify_user_helper(session)

    request = await request_service.create_request(
        RequestCreate(title="Test"),
        user_id=user.id
    )

    await request_service.cancel_request(request.id, user.id)

    with pytest.raises(ConflictError):
        await request_service.cancel_request(request.id, user.id)
