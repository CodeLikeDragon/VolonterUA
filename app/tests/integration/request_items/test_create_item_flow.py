import pytest
from sqlalchemy import select

from app.auth.schemas import RegisterRequest
from app.geo.cities.schemas import CityCreate
from app.geo.countries.schemas import CountryCreate
from app.requests.requests.schemas import RequestCreate
from app.requests.request_items.schemas import RequestItemCreate
from app.requests.request_items.models import RequestItem

from app.tests.helper import (
    get_auth_service,
    get_country_service,
    get_city_service,
    get_request_service,
    get_request_item_service,
)
from app.tests.fixtures.fixtures import verify_user_helper


@pytest.mark.asyncio
async def test_create_item_flow(session, verify_user_helper):
    auth_service = get_auth_service(session)
    country_service = get_country_service(session)
    city_service = get_city_service(session)
    request_service = get_request_service(session)
    item_service = get_request_item_service(session)

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
            country_id=country.id,
        )
    )

    request = await request_service.create_request(
        RequestCreate(
            title="Test",
            description="desc",
            city_id=city.id,
        ),
        user_id=user.id
    )

    item = await item_service.create_item(
        request_id=request.id,
        data=RequestItemCreate(
            name="Water",
            qty=10
        ),
        user_id=user.id
    )

    stmt = select(RequestItem).where(RequestItem.id == item.id)
    result = await session.execute(stmt)
    db_item = result.scalar_one()

    assert db_item.name == "Water"
    assert db_item.qty == 10
