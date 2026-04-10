import pytest
from uuid import uuid4

from app.tests.helper import get_notification_service
from app.common.errors import NotFoundError


@pytest.mark.asyncio
async def test_mark_as_read_not_found(session):
    service = get_notification_service(session)

    with pytest.raises(NotFoundError):
        await service.mark_as_read(uuid4())
