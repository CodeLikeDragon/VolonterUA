import pytest

from app.tests.helper import get_user_service
from app.users.users.schemas import UserCreate


@pytest.mark.asyncio
async def test_deactivate_user(session):
    service = get_user_service(session)

    user = await service.create_user(
        UserCreate(email="test@test.com")
    )

    await service.deactivate_user(user.id)

    result = await service.get_user(user.id)

    assert result.is_active is False
