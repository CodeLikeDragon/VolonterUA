import pytest

from sqlalchemy import select

from app.auth.schemas import RegisterRequest
from app.geo.cities.schemas import CityCreate
from app.geo.countries.schemas import CountryCreate
from app.requests.request_items.models import RequestItem
from app.requests.requests.schemas import RequestCreate
from app.requests.request_items.schemas import RequestItemCreate
from app.common.errors import NotFoundError, ForbiddenError, BadRequestError, ConflictError
from app.common.enums import RequestStatus
from app.tests.helper import (
    get_request_service,
    get_request_item_service,
    get_city_service,
    get_country_service,
    get_auth_service,
)
from app.tests.fixtures.fixtures import verify_user_helper


@pytest.mark.asyncio
async def test_create_item_success(session, verify_user_helper):
    request_service = get_request_service(session)
    item_service = get_request_item_service(session)
    auth_service = get_auth_service(session)
    city_service = get_city_service(session)
    country_service = get_country_service(session)

    user = await auth_service.register(RegisterRequest(email="test@test.com", password="123456"))
    await verify_user_helper(session, user.email)

    country = await country_service.create_country(CountryCreate(name="Germany", iso_code="DE"))
    city = await city_service.create_city(CityCreate(name="Berlin", region="Berlin", timezone="Europe/Berlin", country_id=country.id))

    request = await request_service.create_request(
        RequestCreate(title="Test", city_id=city.id, description="desc"),
        user_id=user.id,
    )

    await item_service.create_item(
        request.id,
        RequestItemCreate(name="Food", qty=10),
        user.id,
    )

    stmt = select(RequestItem)
    result = await session.execute(stmt)
    item = result.scalars().first()

    assert item.name == "Food"
    assert item.qty == 10


@pytest.mark.asyncio
async def test_create_item_invalid_qty(session, verify_user_helper):
    item_service = get_request_item_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(RegisterRequest(email="test@test.com", password="123456"))
    await verify_user_helper(session, user.email)

    with pytest.raises(BadRequestError):
        await item_service.create_item(
            request_id="00000000-0000-0000-0000-000000000000",
            data=RequestItemCreate(name="Food", qty=0),
            user_id=user.id,
        )


@pytest.mark.asyncio
async def test_create_item_forbidden(session, verify_user_helper):
    request_service = get_request_service(session)
    item_service = get_request_item_service(session)
    auth_service = get_auth_service(session)
    city_service = get_city_service(session)
    country_service = get_country_service(session)

    user1 = await auth_service.register(RegisterRequest(email="u1@test.com", password="123456"))
    user2 = await auth_service.register(RegisterRequest(email="u2@test.com", password="123456"))

    await verify_user_helper(session, user1.email)
    await verify_user_helper(session, user2.email)

    country = await country_service.create_country(CountryCreate(name="Germany", iso_code="DE"))
    city = await city_service.create_city(CityCreate(name="Berlin", region="Berlin", timezone="Europe/Berlin", country_id=country.id))

    request = await request_service.create_request(
        RequestCreate(title="Test", city_id=city.id, description="desc"),
        user_id=user1.id,
    )

    with pytest.raises(ForbiddenError):
        await item_service.create_item(
            request.id,
            RequestItemCreate(name="Food", qty=10),
            user2.id,
        )
