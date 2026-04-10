import pytest

from app.auth.schemas import RegisterRequest
from app.common.pagination.schemas import PaginationParams
from app.geo.cities.schemas import CityCreate
from app.geo.countries.schemas import CountryCreate
from app.requests.requests.schemas import RequestCreate
from app.tests.helper import get_request_service, get_city_service, get_country_service, get_auth_service
from app.tests.fixtures.fixtures import verify_user_helper


@pytest.mark.asyncio
async def test_get_requests(session, verify_user_helper):
    service = get_request_service(session)
    auth_service = get_auth_service(session)
    city_service = get_city_service(session)
    country_service = get_country_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )

    await verify_user_helper(session)

    country = await country_service.create_country(
        CountryCreate(name="Germany", iso_code="DE")
    )

    city = await city_service.create_city(
        CityCreate(
            name="Berlin",
            region="Berlin",
            timezone="Europe/Berlin",
            country_id=country.id
        )
    )

    for i in range(5):
        await service.create_request(
            RequestCreate(
                title=f"Test {i}",
                city_id=city.id,
                description="desc",
            ),
            user_id=user.id
        )

    requests, total = await service.get_requests(limit=10, offset=0)

    assert len(requests) == 5
    assert total == 5


@pytest.mark.asyncio
async def test_get_full_request(session, verify_user_helper):
    service = get_request_service(session)
    auth_service = get_auth_service(session)
    city_service = get_city_service(session)
    country_service = get_country_service(session)

    user = await auth_service.register(
        RegisterRequest(email="test@test.com", password="123456")
    )

    await verify_user_helper(session)

    country = await country_service.create_country(
        CountryCreate(name="Germany", iso_code="DE")
    )

    city = await city_service.create_city(
        CityCreate(
            name="Berlin",
            region="Berlin",
            timezone="Europe/Berlin",
            country_id=country.id
        )
    )

    request = await service.create_request(
        RequestCreate(
            title=f"Test 1",
            city_id=city.id,
            description="desc",
        ),
        user_id=user.id
    )

    full_request = await service.get_full_request(request_id=request.id)

    # --- request ---
    assert full_request.request.id == request.id
    assert full_request.request.title == "Test 1"
    assert full_request.request.description == "desc"
    assert full_request.request.city_id == city.id
    assert full_request.request.created_by == user.id

    # --- creator ---
    assert full_request.request_creator.id == user.id

    # --- items ---
    assert isinstance(full_request.request_items, list)
    assert full_request.items_count == 0

    # --- offers ---
    assert isinstance(full_request.request_offers, list)
    assert full_request.offers_count == 0

    # --- assignments ---
    assert isinstance(full_request.request_item_assignments, list)
    assert full_request.assignments_count == 0

    # --- offer creators ---
    assert isinstance(full_request.request_offer_creators, dict)
    assert len(full_request.request_offer_creators) == 0


@pytest.mark.asyncio
async def test_get_user_requests(session, verify_user_helper):
    service = get_request_service(session)
    auth_service = get_auth_service(session)
    city_service = get_city_service(session)
    country_service = get_country_service(session)

    user1 = await auth_service.register(
        RegisterRequest(email="test_user1@test.com", password="123456")
    )
    await verify_user_helper(session, user1.email)

    user2 = await auth_service.register(
        RegisterRequest(email="test_user2@test.com", password="123456")
    )
    await verify_user_helper(session, user2.email)


    country = await country_service.create_country(
        CountryCreate(name="Germany", iso_code="DE")
    )

    city = await city_service.create_city(
        CityCreate(
            name="Berlin",
            region="Berlin",
            timezone="Europe/Berlin",
            country_id=country.id
        )
    )

    await service.create_request(
        RequestCreate(
            title="User1",
            city_id=city.id,
            description="desc"),
        user_id=user1.id
    )

    await service.create_request(
        RequestCreate(
            title="User2",
            city_id=city.id,
            description="desc"
        ),
        user_id=user2.id
    )

    user1_requests = await service.get_user_requests(user1.id, pagination=PaginationParams())

    assert len(user1_requests) == 1
    assert user1_requests[0].title == "User1"
