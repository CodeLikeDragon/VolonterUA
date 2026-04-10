import pytest

from app.tests.helper import get_email_verification_service


@pytest.fixture
def verify_user_helper(monkeypatch):
    async def _verify(session, email="test@test.com"):
        monkeypatch.setattr(
            "app.users.email_verifications.service.generate_otp_code",
            lambda: "123456"
        )

        service = get_email_verification_service(session)

        await service.request_verification(email)
        await service.verify_email(email, "123456")

    return _verify


@pytest.fixture(autouse=True)
def mock_email_service(monkeypatch):
    def fake_send_email(*args, **kwargs):
        return None

    monkeypatch.setattr(
        "app.common.email.service.EmailService.send_email",
        fake_send_email,
    )
