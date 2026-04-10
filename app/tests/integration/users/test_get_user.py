from uuid import uuid4

import pytest

from app.common.errors import NotFoundError
from app.tests.helper import get_user_service
from app.users.users.schemas import UserCreate


@pytest.mark.asyncio
async def test_get_user(session):
    service = get_user_service(session)

    user = await service.create_user(
        UserCreate(email="test@test.com")
    )

    result = await service.get_user(user.id)

    assert result.id == user.id


@pytest.mark.asyncio
async def test_get_user_not_found(session):
    service = get_user_service(session)

    with pytest.raises(NotFoundError):
        await service.get_user(uuid4())
