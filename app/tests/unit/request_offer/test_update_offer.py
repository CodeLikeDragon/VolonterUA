import pytest

from app.common.errors import ForbiddenError
from app.auth.schemas import RegisterRequest
from app.geo.cities.schemas import CityCreate
from app.geo.countries.schemas import CountryCreate
from app.requests.request_offers.schemas import RequestOfferCreate, RequestOfferUpdate
from app.requests.requests.schemas import RequestCreate
from app.tests.helper import get_country_service, get_city_service, get_request_offer_service, get_request_service, \
    get_auth_service
from app.tests.fixtures.fixtures import verify_user_helper


@pytest.mark.asyncio
async def test_update_offer_success(session, verify_user_helper):
    auth = get_auth_service(session)
    request_service = get_request_service(session)
    offer_service = get_request_offer_service(session)
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
        user_id=owner.id,
    )

    offer = await offer_service.create_request_offer(
        user_id=helper.id,
        request_id=request.id,
        data=RequestOfferCreate(message="Help"),
    )

    updated = await offer_service.update_request_offer(
        offer_id=offer.id,
        user_id=helper.id,
        data=RequestOfferUpdate(message="Updated"),
    )

    assert updated.message == "Updated"


@pytest.mark.asyncio
async def test_update_offer_forbidden(session, verify_user_helper):
    auth = get_auth_service(session)
    request_service = get_request_service(session)
    offer_service = get_request_offer_service(session)
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
        user_id=owner.id,
    )

    offer = await offer_service.create_request_offer(
        user_id=helper.id,
        request_id=request.id,
        data=RequestOfferCreate(message="Help"),
    )

    with pytest.raises(ForbiddenError):
        await offer_service.update_request_offer(
            offer_id=offer.id,
            user_id=owner.id,
            data=RequestOfferUpdate(message="Hack"),
        )
