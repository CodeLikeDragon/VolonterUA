import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

from app.common.errors import EmailSendError
from app.core.config import settings


class EmailService:

    def render_template(self, template_name: str, context: dict) -> str:

        template_path = Path(__file__).parent / "templates" / template_name

        with open(template_path, "r", encoding="utf-8") as file:
            html = file.read()

        for key, value in context.items():
            html = html.replace(f"{{{{{key}}}}}", str(value))

        return html


    def send_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        context: dict
    ):
        try:
            html_content = self.render_template(template_name, context)

            message = MIMEMultipart()
            message["From"] = settings.SMTP_USER
            message["To"] = to_email
            message["Subject"] = subject
            message.attach(MIMEText(html_content, "html"))

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_USER, to_email, message.as_string())

        except Exception as e:
            raise EmailSendError(str(e)) from e
