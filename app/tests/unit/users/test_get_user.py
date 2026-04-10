import pytest
from uuid import uuid4

from app.common.errors import NotFoundError
from app.tests.helper import get_user_service


@pytest.mark.asyncio
async def test_get_user_not_found(session):
    service = get_user_service(session)

    with pytest.raises(NotFoundError):
        await service.get_user(uuid4())
