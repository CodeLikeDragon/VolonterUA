import pytest
from unittest.mock import MagicMock

from app.common.email.service import EmailService
from app.common.errors import EmailSendError

pytestmark = pytest.mark.real_email


@pytest.mark.asyncio
async def test_send_email(monkeypatch):
    service = EmailService()

    # mock render_template
    monkeypatch.setattr(
        service,
        "render_template",
        lambda template_name, context: "<h1>123456</h1>"
    )

    smtp_mock = MagicMock()

    # mock SMTP context manager
    class FakeSMTP:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return smtp_mock

        def __exit__(self, exc_type, exc, tb):
            pass

    monkeypatch.setattr("smtplib.SMTP", FakeSMTP)

    service.send_email(
        to_email="test@test.com",
        subject="Test",
        template_name="test.html",
        context={"code": "123456"}
    )

    # перевіряємо виклики
    assert smtp_mock.starttls.called
    assert smtp_mock.login.called
    assert smtp_mock.sendmail.called


@pytest.mark.asyncio
async def test_send_email_fail(monkeypatch):
    service = EmailService()

    monkeypatch.setattr(
        service,
        "render_template",
        lambda *args, **kwargs: "<h1>123</h1>"
    )

    class FakeSMTP:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            raise Exception("SMTP failed")

        def __exit__(self, exc_type, exc, tb):
            pass

    monkeypatch.setattr("smtplib.SMTP", FakeSMTP)

    with pytest.raises(EmailSendError):
        service.send_email(
            to_email="test@test.com",
            subject="Test",
            template_name="test.html",
            context={}
        )
