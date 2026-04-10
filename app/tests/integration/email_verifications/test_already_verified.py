import pytest

from app.auth.schemas import RegisterRequest
from app.tests.helper import get_email_verification_service, get_auth_service
from app.tests.fixtures.fixtures import verify_user_helper


@pytest.mark.asyncio
async def test_request_verification_already_verified(
    session,
    verify_user_helper,
    monkeypatch
):
    auth_service = get_auth_service(session)
    service = get_email_verification_service(session)

    await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    monkeypatch.setattr(
        service.email_service,
        "send_email",
        lambda *args, **kwargs: None
    )

    # тепер працює
    await verify_user_helper(session)

    with (pytest.raises(Exception)):  # або BadRequestError
        await service.request_verification("test@test.com")
