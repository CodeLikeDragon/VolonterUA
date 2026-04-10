import pytest

from app.auth.schemas import RegisterRequest
from app.geo.countries.schemas import CountryCreate
from app.geo.cities.schemas import CityCreate
from app.requests.requests.schemas import RequestCreate
from app.requests.request_offers.schemas import RequestOfferCreate
from app.common.errors import ForbiddenError, ConflictError, NotFoundError

from app.tests.helper import (
    get_auth_service,
    get_request_service,
    get_request_offer_service,
    get_city_service,
    get_country_service,
)

from app.tests.fixtures.fixtures import verify_user_helper


@pytest.mark.asyncio
async def test_create_offer_success(session, verify_user_helper):
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
    city = await city_service.create_city(CityCreate(name="Berlin", region="Berlin", timezone="Europe/Berlin", country_id=country.id))

    request = await request_service.create_request(
        RequestCreate(title="Test", city_id=city.id, description="desc"),
        user_id=owner.id,
    )

    offer = await offer_service.create_request_offer(
        user_id=helper.id,
        request_id=request.id,
        data=RequestOfferCreate(message="Help"),
    )

    assert offer.message == "Help"


@pytest.mark.asyncio
async def test_create_offer_forbidden_self(session, verify_user_helper):
    auth = get_auth_service(session)
    request_service = get_request_service(session)
    offer_service = get_request_offer_service(session)

    user = await auth.register(RegisterRequest(email="test@test.com", password="123456"))
    await verify_user_helper(session, user.email)

    request = await request_service.create_request(
        RequestCreate(title="Test", city_id=None, description="desc"),
        user_id=user.id,
    )

    with pytest.raises(ForbiddenError):
        await offer_service.create_request_offer(
            user_id=user.id,
            request_id=request.id,
            data=RequestOfferCreate(message="Help"),
        )
