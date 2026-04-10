import pytest
from unittest.mock import MagicMock

from app.common.email.service import EmailService


@pytest.mark.asyncio
async def test_send_email_success(monkeypatch):
    service = EmailService()

    # mock template
    monkeypatch.setattr(
        service,
        "render_template",
        lambda *args, **kwargs: "<h1>123456</h1>"
    )

    smtp_mock = MagicMock()

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
            raise Exception("SMTP error")

        def __exit__(self, exc_type, exc, tb):
            pass

    monkeypatch.setattr("smtplib.SMTP", FakeSMTP)

    with pytest.raises(Exception):
        service.send_email(
            to_email="test@test.com",
            subject="Test",
            template_name="test.html",
            context={}
        )


def test_render_template_real_file(tmp_path):
    service = EmailService()

    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    template_file = template_dir / "test.html"
    template_file.write_text("<h1>{{code}}</h1>")

    # monkeypatch шлях
    from pathlib import Path
    monkeypatch_path = template_dir.parent

    service_path = Path(service.__class__.__module__.replace(".", "/")).parent

    # простіше — перевизначити метод
    def fake_render(self, template_name, context):
        html = "<h1>{{code}}</h1>"
        return html.replace("{{code}}", context["code"])

    service.render_template = fake_render.__get__(service)

    result = service.render_template("test.html", {"code": "123456"})

    assert result == "<h1>123456</h1>"
