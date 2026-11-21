import pytest
from datetime import datetime, timedelta

from app.auth.schemas import RegisterRequest
from app.geo.cities.schemas import CityCreate
from app.geo.countries.schemas import CountryCreate
from app.requests.requests.schemas import RequestCreate, RequestFilters
from app.common.pagination.schemas import PaginationParams

from app.tests.helper import (
    get_request_service,
    get_city_service,
    get_country_service,
    get_auth_service,
)
from app.tests.fixtures.fixtures import verify_user_helper


# =========================
# Helper
# =========================

async def setup_base(session, verify_user_helper):
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
            country_id=country.id,
        )
    )

    return user, city


# =========================
# Tests
# =========================

@pytest.mark.asyncio
async def test_filter_by_status(session, verify_user_helper):
    service = get_request_service(session)

    user, city = await setup_base(session, verify_user_helper)

    await service.create_request(
        RequestCreate(title="A", description="desc", city_id=city.id),
        user_id=user.id,
    )

    filters = RequestFilters(status="NEW")
    pagination = PaginationParams(page=1, limit=10)

    result = await service.get_filtered_requests(filters, pagination)

    assert result.total >= 1
    assert all(r.status == "NEW" for r in result.items)


# -------------------------

@pytest.mark.asyncio
async def test_filter_by_city(session, verify_user_helper):
    service = get_request_service(session)
    city_service = get_city_service(session)

    user, city = await setup_base(session, verify_user_helper)

    other_city = await city_service.create_city(
        CityCreate(
            name="Munich",
            region="Bavaria",
            timezone="Europe/Berlin",
            country_id=city.country_id,
        )
    )

    await service.create_request(
        RequestCreate(title="Berlin req", description="desc", city_id=city.id),
        user_id=user.id,
    )

    await service.create_request(
        RequestCreate(title="Other", description="desc", city_id=other_city.id),
        user_id=user.id,
    )

    filters = RequestFilters(city_id=city.id)
    pagination = PaginationParams(page=1, limit=10)

    result = await service.get_filtered_requests(filters, pagination)

    assert result.total == 1
    assert result.items[0].city_id == city.id


# -------------------------

@pytest.mark.asyncio
async def test_search(session, verify_user_helper):
    service = get_request_service(session)

    user, city = await setup_base(session, verify_user_helper)

    await service.create_request(
        RequestCreate(title="ліки для лікарні", description="desc", city_id=city.id),
        user_id=user.id,
    )

    await service.create_request(
        RequestCreate(title="одяг", description="desc", city_id=city.id),
        user_id=user.id,
    )

    filters = RequestFilters(search="ліки")
    pagination = PaginationParams(page=1, limit=10)

    result = await service.get_filtered_requests(filters, pagination)

    assert result.total == 1
    assert "ліки" in result.items[0].title


# -------------------------

@pytest.mark.asyncio
async def test_has_assignee(session, verify_user_helper):
    service = get_request_service(session)

    user, city = await setup_base(session, verify_user_helper)

    r1 = await service.create_request(
        RequestCreate(title="assigned", description="desc", city_id=city.id),
        user_id=user.id,
    )

    await service.create_request(
        RequestCreate(title="not assigned", description="desc", city_id=city.id),
        user_id=user.id,
    )

    r1.assignee_id = user.id
    await session.flush()

    filters = RequestFilters(has_assignee=True)
    pagination = PaginationParams(page=1, limit=10)

    result = await service.get_filtered_requests(filters, pagination)

    assert result.total == 1
    assert result.items[0].assignee_id is not None


# -------------------------

@pytest.mark.asyncio
async def test_date_range(session, verify_user_helper):
    service = get_request_service(session)

    user, city = await setup_base(session, verify_user_helper)

    now = datetime.utcnow()

    old = await service.create_request(
        RequestCreate(title="old", description="desc", city_id=city.id),
        user_id=user.id,
    )
    old.created_at = now - timedelta(days=5)

    new = await service.create_request(
        RequestCreate(title="new", description="desc", city_id=city.id),
        user_id=user.id,
    )
    new.created_at = now

    await session.flush()

    filters = RequestFilters(
        created_from=now - timedelta(days=1),
        created_to=now + timedelta(days=1),
    )
    pagination = PaginationParams(page=1, limit=10)

    result = await service.get_filtered_requests(filters, pagination)

    assert result.total == 1
    assert result.items[0].title == "new"


# -------------------------

@pytest.mark.asyncio
async def test_pagination(session, verify_user_helper):
    service = get_request_service(session)

    user, city = await setup_base(session, verify_user_helper)

    for i in range(5):
        await service.create_request(
            RequestCreate(title=f"req {i}", description="desc", city_id=city.id),
            user_id=user.id,
        )

    filters = RequestFilters()
    pagination = PaginationParams(page=2, limit=2)

    result = await service.get_filtered_requests(filters, pagination)

    assert result.total == 5
    assert len(result.items) == 2
