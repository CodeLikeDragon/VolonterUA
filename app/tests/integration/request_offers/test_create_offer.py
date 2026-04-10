import pytest
from sqlalchemy import select

from app.auth.schemas import RegisterRequest
from app.geo.cities.schemas import CityCreate
from app.geo.countries.schemas import CountryCreate
from app.requests.requests.schemas import RequestCreate
from app.requests.request_offers.schemas import RequestOfferCreate
from app.requests.request_offers.models import RequestOffer

from app.tests.helper import (
    get_auth_service,
    get_country_service,
    get_city_service,
    get_request_service,
    get_request_offer_service,
)
from app.tests.fixtures.fixtures import verify_user_helper


@pytest.mark.asyncio
async def test_create_offer_flow(session, verify_user_helper):
    auth_service = get_auth_service(session)
    country_service = get_country_service(session)
    city_service = get_city_service(session)
    request_service = get_request_service(session)
    offer_service = get_request_offer_service(session)

    # owner
    owner = await auth_service.register(
        RegisterRequest(email="owner@test.com", password="123456")
    )

    # helper
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
        RequestCreate(
            title="Need help",
            description="desc",
            city_id=city.id,
        ),
        user_id=owner.id
    )

    offer = await offer_service.create_request_offer(
        user_id=helper.id,
        request_id=request.id,
        data=RequestOfferCreate(message="I can help"),
    )

    stmt = select(RequestOffer).where(RequestOffer.id == offer.id)
    result = await session.execute(stmt)
    db_offer = result.scalar_one()

    assert db_offer.message == "I can help"


from app.common.errors import ForbiddenError


@pytest.mark.asyncio
async def test_create_offer_forbidden_owner(session, verify_user_helper):
    auth_service = get_auth_service(session)
    request_service = get_request_service(session)
    offer_service = get_request_offer_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )
    await verify_user_helper(session)

    request = await request_service.create_request(
        RequestCreate(title="Test", description="desc"),
        user_id=user.id
    )

    with pytest.raises(ForbiddenError):
        await offer_service.create_request_offer(
            user_id=user.id,
            request_id=request.id,
            data=RequestOfferCreate(message="try"),
        )
