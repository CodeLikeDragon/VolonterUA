import pytest
from sqlalchemy import select

from app.auth.schemas import RegisterRequest
from app.common.errors import NotFoundError
from app.geo.cities.schemas import CityCreate
from app.geo.countries.schemas import CountryCreate
from app.requests.request_items.models import RequestItem
from app.requests.request_items.schemas import RequestItemCreate
from app.requests.requests.schemas import RequestCreate
from app.tests.helper import get_request_item_service, get_request_service, get_auth_service, get_city_service, \
    get_country_service
from app.tests.fixtures.fixtures import verify_user_helper



@pytest.mark.asyncio
async def test_get_request_item(session, verify_user_helper):
    request_service = get_request_service(session)
    item_service = get_request_item_service(session)
    auth_service = get_auth_service(session)
    city_service = get_city_service(session)
    country_service = get_country_service(session)

    user = await auth_service.register(RegisterRequest(email="test@test.com", password="123456"))
    await verify_user_helper(session, user.email)

    country = await country_service.create_country(CountryCreate(name="Germany", iso_code="DE"))
    city = await city_service.create_city(
        CityCreate(name="Berlin", region="Berlin", timezone="Europe/Berlin", country_id=country.id))

    request = await request_service.create_request(
        RequestCreate(title="Test", city_id=city.id, description="desc"),
        user_id=user.id,
    )

    await item_service.create_item(
        request.id,
        RequestItemCreate(name="Food", qty=10),
        user.id,
    )

    stmt = select(RequestItem).where(RequestItem.request_id == request.id)
    result = await session.execute(stmt)
    item_db = result.scalars().first()

    item = await item_service.get_item(item_db.id)
    assert item.id == item_db.id
    assert item.request_id == item_db.request_id
    assert item.name == "Food"
    assert item.qty == 10


@pytest.mark.asyncio
async def test_get_item_not_found(session):
    service = get_request_item_service(session)

    with pytest.raises(NotFoundError):
        await service.get_item("00000000-0000-0000-0000-000000000000")


@pytest.mark.asyncio
async def test_get_all_items(session, verify_user_helper):
    request_service = get_request_service(session)
    item_service = get_request_item_service(session)
    auth_service = get_auth_service(session)
    city_service = get_city_service(session)
    country_service = get_country_service(session)

    # user
    user = await auth_service.register(RegisterRequest(email="all@test.com", password="123456"))
    await verify_user_helper(session, user.email)

    # geo
    country = await country_service.create_country(CountryCreate(name="Germany", iso_code="DE"))
    city = await city_service.create_city(
        CityCreate(name="Berlin", region="Berlin", timezone="Europe/Berlin", country_id=country.id)
    )

    # request
    request = await request_service.create_request(
        RequestCreate(title="Test", city_id=city.id, description="desc"),
        user_id=user.id,
    )

    # create items
    await item_service.create_item(request.id, RequestItemCreate(name="Food", qty=10), user.id)
    await item_service.create_item(request.id, RequestItemCreate(name="Water", qty=5), user.id)

    # act
    items = await item_service.get_all_items(limit=10, offset=0)

    # assert
    assert len(items) >= 2
    names = [i.name for i in items]
    assert "Food" in names
    assert "Water" in names


@pytest.mark.asyncio
async def test_get_user_items(session, verify_user_helper):
    request_service = get_request_service(session)
    item_service = get_request_item_service(session)
    auth_service = get_auth_service(session)
    city_service = get_city_service(session)
    country_service = get_country_service(session)

    # users
    user1 = await auth_service.register(RegisterRequest(email="user1@test.com", password="123456"))
    user2 = await auth_service.register(RegisterRequest(email="user2@test.com", password="123456"))

    await verify_user_helper(session, user1.email)
    await verify_user_helper(session, user2.email)

    # geo
    country = await country_service.create_country(CountryCreate(name="Germany", iso_code="DE"))
    city = await city_service.create_city(
        CityCreate(name="Berlin", region="Berlin", timezone="Europe/Berlin", country_id=country.id)
    )

    # request user1
    request1 = await request_service.create_request(
        RequestCreate(title="User1 Request", city_id=city.id, description="desc"),
        user_id=user1.id,
    )

    # request user2
    request2 = await request_service.create_request(
        RequestCreate(title="User2 Request", city_id=city.id, description="desc"),
        user_id=user2.id,
    )

    # items
    await item_service.create_item(request1.id, RequestItemCreate(name="Food", qty=10), user1.id)
    await item_service.create_item(request2.id, RequestItemCreate(name="Water", qty=5), user2.id)

    # act
    user1_items = await item_service.get_user_items(user1.id)

    # assert
    assert len(user1_items) == 1
    assert user1_items[0].name == "Food"


@pytest.mark.asyncio
async def test_get_user_items_empty(session, verify_user_helper):
    item_service = get_request_item_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(RegisterRequest(email="empty@test.com", password="123456"))
    await verify_user_helper(session, user.email)

    items = await item_service.get_user_items(user.id)

    assert items == []
