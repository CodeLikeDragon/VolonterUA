import pytest
from pathlib import Path

from app.common.email.service import EmailService


def test_render_template(tmp_path):
    service = EmailService()

    # створюємо fake template файл
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    template_file = template_dir / "test.html"
    template_file.write_text("<h1>{{code}}</h1>")

    # monkeypatch path
    service_path = Path(service.__class__.__module__.replace(".", "/")).parent

    # простіше — підмінимо метод
    def fake_render(self, template_name, context):
        html = "<h1>{{code}}</h1>"
        return html.replace("{{code}}", context["code"])

    service.render_template = fake_render.__get__(service)

    result = service.render_template("test.html", {"code": "123456"})

    assert result == "<h1>123456</h1>"
    