import pytest

from app.common.errors import NotFoundError
from app.tests.helper import get_user_service
from app.users.users.schemas import UserUpdate, UserCreate, UserMeUpdate


@pytest.mark.asyncio
async def test_update_user(session):
    service = get_user_service(session)

    user = await service.create_user(
        UserCreate(email="test@test.com")
    )

    updated = await service.update_user(
        user_id=user.id,
        data=UserUpdate(first_name="Updated")
    )

    assert updated.first_name == "Updated"


@pytest.mark.asyncio
async def test_update_user_invalid_city(session):
    service = get_user_service(session)

    user = await service.create_user(
        UserCreate(email="test@test.com")
    )

    from uuid import uuid4

    with pytest.raises(NotFoundError):
        await service.update_user(
            user_id=user.id,
            data=UserUpdate(city_id=uuid4())
        )


@pytest.mark.asyncio
async def test_update_me(session):
    service = get_user_service(session)

    user = await service.create_user(
        UserCreate(email="test@test.com")
    )

    updated = await service.update_me(
        user_id=user.id,
        data=UserMeUpdate(first_name="Me")
    )

    assert updated.first_name == "Me"
