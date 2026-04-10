import pytest
from sqlalchemy import select

from app.auth.schemas import RegisterRequest
from app.common.pagination.schemas import PaginationParams
from app.geo.cities.schemas import CityCreate
from app.geo.countries.schemas import CountryCreate
from app.requests.requests.models import Request
from app.requests.requests.schemas import RequestCreate, RequestUpdate
from app.tests.helper import get_request_service, get_city_service, get_country_service, get_auth_service
from app.tests.fixtures.fixtures import verify_user_helper


@pytest.mark.asyncio
async def test_update_request(session, verify_user_helper):
    service = get_request_service(session)
    auth_service = get_auth_service(session)
    city_service = get_city_service(session)
    country_service = get_country_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await verify_user_helper(session)

    await auth_service.login(
        email="test@test.com",
        password="123456"
    )

    country = await country_service.create_country(
        CountryCreate(
            name="Germany",
            iso_code="DE"
        )
    )

    city = await city_service.create_city(
        data=CityCreate(
            name="Berlin",
            region="Berlin",
            timezone="Europe/Berlin",
            country_id=country.id,
        )
    )

    request = await service.create_request(
        RequestCreate(
            title="TestRequest",
            city_id=city.id,
            description="Request description",
        ),
        user_id=user.id
    )

    stmt = select(Request).where(Request.id == request.id)
    result = await session.execute(stmt)
    request = result.scalars().first()

    new_city = await city_service.create_city(
        data=CityCreate(
            name="Hamburg",
            region="Hamburg",
            timezone="Europe/Berlin",
            country_id=country.id,
        )
    )

    update_data = RequestUpdate(
        title="TestUpdate",
        description="Request description updated",
        city_id=new_city.id,
    )
    updated_request = await service.update_request(request_id=request.id, user_id=user.id, data=update_data)

    assert updated_request.title == "TestUpdate"
    assert updated_request.description == "Request description updated"
    assert updated_request.city_id == new_city.id
