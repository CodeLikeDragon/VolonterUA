import pytest

from app.auth.schemas import RegisterRequest
from app.common.enums import RequestStatus
from app.geo.cities.schemas import CityCreate
from app.geo.countries.schemas import CountryCreate
from app.requests.request_item_assignment.schemas import RequestItemAssignmentCreate
from app.requests.request_items.schemas import RequestItemCreate
from app.requests.request_offers.schemas import RequestOfferCreate
from app.requests.requests.schemas import RequestCreate
from app.tests.helper import get_country_service, get_city_service, get_request_item_assignment_service, \
    get_request_offer_service, get_request_item_service, get_request_service, get_auth_service
from app.tests.fixtures.fixtures import verify_user_helper


@pytest.mark.asyncio
async def test_assignment_changes_request_status(session, verify_user_helper):
    auth = get_auth_service(session)
    request_service = get_request_service(session)
    item_service = get_request_item_service(session)
    offer_service = get_request_offer_service(session)
    assignment_service = get_request_item_assignment_service(session)
    city_service = get_city_service(session)
    country_service = get_country_service(session)

    owner = await auth.register(RegisterRequest(email="owner@test.com", password="123456"))
    helper = await auth.register(RegisterRequest(email="helper@test.com", password="123456"))

    await verify_user_helper(session, owner.email)
    await verify_user_helper(session, helper.email)

    country = await country_service.create_country(CountryCreate(name="DE", iso_code="DE"))
    city = await city_service.create_city(
        CityCreate(name="Berlin", region="Berlin", timezone="Europe/Berlin", country_id=country.id)
    )

    request = await request_service.create_request(
        RequestCreate(title="Test", city_id=city.id, description="desc"),
        user_id=owner.id
    )

    item = await item_service.create_item(
        request.id,
        RequestItemCreate(name="Food", qty=10),
        owner.id
    )

    offer = await offer_service.create_request_offer(
        user_id=helper.id,
        request_id=request.id,
        data=RequestOfferCreate(message="Help")
    )

    await offer_service.accept_offer(offer.id, owner.id)

    await assignment_service.create(
        item.id,
        RequestItemAssignmentCreate(offer_id=offer.id, qty_taken=5),
        helper.id
    )

    updated_request = await request_service.get_request(request.id)

    assert updated_request.status == RequestStatus.IN_PROGRESS
