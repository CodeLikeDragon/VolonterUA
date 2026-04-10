import pytest

from app.auth.schemas import RegisterRequest
from app.common.errors import NotFoundError
from app.common.pagination.schemas import PaginationParams
from app.geo.cities.schemas import CityCreate
from app.geo.countries.schemas import CountryCreate
from app.requests.request_offers.schemas import RequestOfferCreate
from app.requests.requests.schemas import RequestCreate
from app.tests.helper import get_request_offer_service, get_request_service, get_auth_service, get_city_service, \
    get_country_service
from app.tests.fixtures.fixtures import verify_user_helper


@pytest.mark.asyncio
async def test_get_offer_not_found(session):
    service = get_request_offer_service(session)

    with pytest.raises(NotFoundError):
        await service.get_request_offer("00000000-0000-0000-0000-000000000000")


@pytest.mark.asyncio
async def test_get_request_offers(session, verify_user_helper):
    request_service = get_request_service(session)
    offer_service = get_request_offer_service(session)
    auth_service = get_auth_service(session)
    city_service = get_city_service(session)
    country_service = get_country_service(session)

    # users
    owner = await auth_service.register(RegisterRequest(email="owner@test.com", password="123456"))
    helper_1 = await auth_service.register(RegisterRequest(email="helper1@test.com", password="123456"))
    helper_2 = await auth_service.register(RegisterRequest(email="helper2@test.com", password="123456"))

    await verify_user_helper(session, owner.email)
    await verify_user_helper(session, helper_1.email)
    await verify_user_helper(session, helper_2.email)

    # geo
    country = await country_service.create_country(CountryCreate(name="Germany", iso_code="DE"))
    city = await city_service.create_city(
        CityCreate(name="Berlin", region="Berlin", timezone="Europe/Berlin", country_id=country.id)
    )

    # request
    request = await request_service.create_request(
        RequestCreate(title="Test", city_id=city.id, description="desc"),
        user_id=owner.id,
    )

    # create offers (від helper)
    await offer_service.create_request_offer(
        user_id=helper_1.id,
        request_id=request.id,
        data=RequestOfferCreate(message="Offer 1"),
    )

    await offer_service.create_request_offer(
        user_id=helper_2.id,
        request_id=request.id,
        data=RequestOfferCreate(message="Offer 2"),
    )

    # act
    offers = await offer_service.get_request_offers(limit=10, offset=0)

    # assert
    assert len(offers) >= 2


@pytest.mark.asyncio
async def test_get_my_offers(session, verify_user_helper):
    request_service = get_request_service(session)
    offer_service = get_request_offer_service(session)
    auth_service = get_auth_service(session)
    city_service = get_city_service(session)
    country_service = get_country_service(session)

    # users
    owner = await auth_service.register(RegisterRequest(email="owner@test.com", password="123456"))
    user_me = await auth_service.register(RegisterRequest(email="helper1@test.com", password="123456"))
    helper = await auth_service.register(RegisterRequest(email="helper2@test.com", password="123456"))

    await verify_user_helper(session, owner.email)
    await verify_user_helper(session, user_me.email)
    await verify_user_helper(session, helper.email)

    # geo
    country = await country_service.create_country(CountryCreate(name="Germany", iso_code="DE"))
    city = await city_service.create_city(
        CityCreate(name="Berlin", region="Berlin", timezone="Europe/Berlin", country_id=country.id)
    )

    # request
    request = await request_service.create_request(
        RequestCreate(title="Test", city_id=city.id, description="desc"),
        user_id=owner.id,
    )

    # create offers (від helper)
    await offer_service.create_request_offer(
        user_id=user_me.id,
        request_id=request.id,
        data=RequestOfferCreate(message="Offer 1"),
    )

    await offer_service.create_request_offer(
        user_id=helper.id,
        request_id=request.id,
        data=RequestOfferCreate(message="Offer 2"),
    )

    # act
    params = PaginationParams(page=1, limit=10)
    offers = await offer_service.get_my_offers(user_id=user_me.id, pagination=params)

    # assert
    assert len(offers) == 1
    assert offers[0].user_id == user_me.id
    assert offers[0].request_id == request.id


@pytest.mark.asyncio
async def test_get_accepted_offers(session, verify_user_helper):
    request_service = get_request_service(session)
    offer_service = get_request_offer_service(session)
    auth_service = get_auth_service(session)
    city_service = get_city_service(session)
    country_service = get_country_service(session)

    # users
    owner = await auth_service.register(RegisterRequest(email="owner@test.com", password="123456"))
    helper = await auth_service.register(RegisterRequest(email="helper@test.com", password="123456"))

    await verify_user_helper(session, owner.email)
    await verify_user_helper(session, helper.email)

    # geo
    country = await country_service.create_country(CountryCreate(name="Germany", iso_code="DE"))
    city = await city_service.create_city(
        CityCreate(name="Berlin", region="Berlin", timezone="Europe/Berlin", country_id=country.id)
    )

    # request
    request = await request_service.create_request(
        RequestCreate(title="Test", city_id=city.id, description="desc"),
        user_id=owner.id,
    )

    # create offer
    offer = await offer_service.create_request_offer(
        user_id=helper.id,
        request_id=request.id,
        data=RequestOfferCreate(message="Help"),
    )

    # accept
    await offer_service.accept_offer(offer.id, owner.id)

    # act
    accepted = await offer_service.get_accepted_offers()

    # assert
    assert any(o.id == offer.id for o in accepted)


@pytest.mark.asyncio
async def test_get_declined_offers(session, verify_user_helper):
    request_service = get_request_service(session)
    offer_service = get_request_offer_service(session)
    auth_service = get_auth_service(session)
    city_service = get_city_service(session)
    country_service = get_country_service(session)

    # users
    owner = await auth_service.register(RegisterRequest(email="owner2@test.com", password="123456"))
    helper = await auth_service.register(RegisterRequest(email="helper2@test.com", password="123456"))

    await verify_user_helper(session, owner.email)
    await verify_user_helper(session, helper.email)

    # geo
    country = await country_service.create_country(CountryCreate(name="Germany", iso_code="DE"))
    city = await city_service.create_city(
        CityCreate(name="Berlin", region="Berlin", timezone="Europe/Berlin", country_id=country.id)
    )

    # request
    request = await request_service.create_request(
        RequestCreate(title="Test", city_id=city.id, description="desc"),
        user_id=owner.id,
    )

    # create offer
    offer = await offer_service.create_request_offer(
        user_id=helper.id,
        request_id=request.id,
        data=RequestOfferCreate(message="Help"),
    )

    # decline
    await offer_service.decline_offer(offer.id, owner.id)

    # act
    declined = await offer_service.get_declined_offers()

    # assert
    assert any(o.id == offer.id for o in declined)


@pytest.mark.asyncio
async def test_get_request_offers_pagination(session, verify_user_helper):
    request_service = get_request_service(session)
    offer_service = get_request_offer_service(session)
    auth_service = get_auth_service(session)
    city_service = get_city_service(session)
    country_service = get_country_service(session)

    # owner
    owner = await auth_service.register(RegisterRequest(email="owner@test.com", password="123456"))
    await verify_user_helper(session, owner.email)

    # helper
    helper_1 = await auth_service.register(RegisterRequest(email="helper_1@test.com", password="123456"))
    helper_2 = await auth_service.register(RegisterRequest(email="helper_2@test.com", password="123456"))
    helper_3 = await auth_service.register(RegisterRequest(email="helper_3@test.com", password="123456"))
    helper_4 = await auth_service.register(RegisterRequest(email="helper_4@test.com", password="123456"))
    helper_5 = await auth_service.register(RegisterRequest(email="helper_5@test.com", password="123456"))

    await verify_user_helper(session, helper_1.email)
    await verify_user_helper(session, helper_2.email)
    await verify_user_helper(session, helper_3.email)
    await verify_user_helper(session, helper_4.email)
    await verify_user_helper(session, helper_5.email)

    country = await country_service.create_country(CountryCreate(name="Germany", iso_code="DE"))
    city = await city_service.create_city(
        CityCreate(name="Berlin", region="Berlin", timezone="Europe/Berlin", country_id=country.id)
    )

    request = await request_service.create_request(
        RequestCreate(title="Test", city_id=city.id, description="desc"),
        user_id=owner.id,
    )

    helper_list = [helper_1, helper_2, helper_3, helper_4, helper_5]

    for i, helper in enumerate(helper_list):
        await offer_service.create_request_offer(
            user_id=helper.id,
            request_id=request.id,
            data=RequestOfferCreate(message=f"Offer {i}"),
        )

    offers = await offer_service.get_request_offers(limit=2, offset=0)

    assert len(offers) == 2
