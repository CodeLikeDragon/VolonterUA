import pytest

from app.common.errors import UnauthorizedError

from app.tests.helper import get_refresh_token_service


@pytest.mark.asyncio
async def test_refresh_invalid_token(session):
    service = get_refresh_token_service(session)

    with pytest.raises(UnauthorizedError):
        await service.refresh("invalid")
