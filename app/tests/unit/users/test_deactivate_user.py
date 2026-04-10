import pytest

from app.users.users.schemas import UserCreate
from app.tests.helper import get_user_service


@pytest.mark.asyncio
async def test_deactivate_user(session):
    service = get_user_service(session)

    user = await service.create_user(UserCreate(email="test@test.com"))

    await service.deactivate_user(user.id)

    assert user.is_active is False
