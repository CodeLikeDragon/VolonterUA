from datetime import datetime, timezone

import pytest

from app.auth.schemas import RegisterRequest
from app.common.errors import NotFoundError
from app.geo.cities.schemas import CityCreate
from app.geo.countries.schemas import CountryCreate
from app.requests.request_item_assignment.schemas import RequestItemAssignmentCreate
from app.requests.request_items.schemas import RequestItemCreate
from app.requests.request_offers.schemas import RequestOfferCreate
from app.requests.requests.schemas import RequestCreate

from app.tests.helper import (
    get_auth_service,
    get_country_service,
    get_city_service,
    get_request_service,
    get_request_item_service,
    get_request_offer_service,
    get_request_item_assignment_service,
)
from app.tests.fixtures.fixtures import verify_user_helper


@pytest.mark.asyncio
async def test_delete_assignment_flow(session, verify_user_helper):
    auth_service = get_auth_service(session)
    country_service = get_country_service(session)
    city_service = get_city_service(session)
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
        RequestCreate(title="Test", description="desc", city_id=city.id),
        user_id=owner.id
    )

    item = await item_service.create_item(
        data=RequestItemCreate(name="Item", qty=5),
        request_id=request.id,
        user_id=owner.id
    )

    offer = await offer_service.create_request_offer(
        data=RequestOfferCreate(message="help"),
        user_id=helper.id,
        request_id=request.id
    )

    offer.accepted_at = datetime.now(timezone.utc)
    await session.commit()

    assignment = await assignment_service.create(
        request_item_id=item.id,
        data=RequestItemAssignmentCreate(
            offer_id=offer.id,
            qty_taken=1,
        ),
        user_id=helper.id,
    )

    await assignment_service.delete(assignment.id)

    with pytest.raises(NotFoundError):
        await assignment_service.get_assignment_by_id(assignment.id)
