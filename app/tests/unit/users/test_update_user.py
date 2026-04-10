import pytest

from app.users.users.schemas import UserCreate, UserUpdate
from app.tests.helper import get_user_service


@pytest.mark.asyncio
async def test_update_user(session):
    service = get_user_service(session)

    user = await service.create_user(UserCreate(email="test@test.com"))

    updated = await service.update_user(
        user.id,
        UserUpdate(first_name="John")
    )

    assert updated.first_name == "John"
