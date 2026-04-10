import uuid

import pytest
from sqlalchemy import select

from app.auth.schemas import RegisterRequest
from app.common.errors import ConflictError
from app.geo.cities.schemas import CityCreate
from app.geo.countries.schemas import CountryCreate
from app.requests.requests.models import Request
from app.requests.requests.schemas import RequestCreate
from app.tests.helper import get_request_service, get_city_service, get_country_service, get_auth_service
from app.tests.fixtures.fixtures import verify_user_helper


@pytest.mark.asyncio
async def test_create_request(session, verify_user_helper):
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

    assert request.title == "TestRequest"
    assert request.city_id == city.id
    assert request.description == "Request description"


@pytest.mark.asyncio
async def test_create_request_invalid_city(session, verify_user_helper):
    service = get_request_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await verify_user_helper(session)

    with pytest.raises(ConflictError):
        await service.create_request(
            RequestCreate(
                title="Test",
                city_id="00000000-0000-0000-0000-000000000000",
                description="desc",
            ),
            user_id=user.id,
        )