import pytest

from app.auth.schemas import RegisterRequest
from app.geo.cities.schemas import CityCreate
from app.geo.countries.schemas import CountryCreate
from app.requests.requests.schemas import RequestCreate
from app.common.errors import NotFoundError, ForbiddenError
from app.common.enums import RequestStatus
from app.tests.helper import get_request_service, get_city_service, get_country_service, get_auth_service
from app.tests.fixtures.fixtures import verify_user_helper


@pytest.mark.asyncio
async def test_cancel_request_success(session, verify_user_helper):
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

    country = await country_service.create_country(
        CountryCreate(
            name="Germany",
            iso_code="DE"
        )
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
            title="Test",
            city_id=city.id,
            description="desc"
        ),
        user_id=user.id
    )

    canceled = await service.cancel_request(request.id, user.id)

    assert canceled.status == RequestStatus.CANCELED


@pytest.mark.asyncio
async def test_cancel_request_not_found(session):
    service = get_request_service(session)

    with pytest.raises(NotFoundError):
        await service.cancel_request(
            "00000000-0000-0000-0000-000000000000",
            "00000000-0000-0000-0000-000000000000",
        )


@pytest.mark.asyncio
async def test_cancel_request_forbidden(session, verify_user_helper):
    service = get_request_service(session)
    auth_service = get_auth_service(session)
    city_service = get_city_service(session)
    country_service = get_country_service(session)

    user1 = await auth_service.register(
        RegisterRequest(email="test1@test.com", password="123456")
    )
    user2 = await auth_service.register(
        RegisterRequest(email="test2@test.com", password="123456")
    )

    await verify_user_helper(session, user1.email)
    await verify_user_helper(session, user2.email)

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

    request = await service.create_request(
        RequestCreate(
            title="Test",
            city_id=city.id,
            description="desc"
        ),
        user_id=user1.id
    )

    with pytest.raises(ForbiddenError):
        await service.cancel_request(request.id, user2.id)
