import pytest
from sqlalchemy import select

from app.auth.schemas import RegisterRequest
from app.geo.cities.schemas import CityCreate
from app.geo.countries.schemas import CountryCreate
from app.requests.request_items.schemas import RequestItemCreate, RequestItemUpdate
from app.requests.requests.schemas import RequestCreate
from app.tests.helper import get_request_item_service, get_request_service, get_auth_service, get_city_service, \
    get_country_service
from app.tests.fixtures.fixtures import verify_user_helper


@pytest.mark.asyncio
async def test_update_item_success(session, verify_user_helper):
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

    item = await item_service.create_item(
        request.id,
        RequestItemCreate(name="Food", qty=10),
        user.id,
    )

    updated = await item_service.update_item(
        item.id,
        data=RequestItemUpdate(qty=20),
        user_id=user.id,
    )

    assert updated.qty == 20
