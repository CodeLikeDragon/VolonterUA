import pytest
from uuid import uuid4

from app.common.errors import NotFoundError
from app.tests.helper import get_request_service


@pytest.mark.asyncio
async def test_get_request_not_found(session):
    service = get_request_service(session)

    with pytest.raises(NotFoundError):
        await service.get_request(uuid4())
