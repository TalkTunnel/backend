import smtplib
from email.message import EmailMessage

from src.core.config import settings


class EmailService:
    @staticmethod
    def _validate_smtp_config() -> None:
        required = [
            settings.SMTP_HOST,
            settings.SMTP_USER,
            settings.SMTP_PASSWORD,
            settings.SMTP_FROM,
        ]
        if any(not value for value in required):
            raise ValueError("SMTP settings are not configured")

    def send_otp_email(self, to_email: str, otp_code: str) -> None:
        self._validate_smtp_config()

        message = EmailMessage()
        message["Subject"] = "Your verification code"
        message["From"] = settings.SMTP_FROM
        message["To"] = to_email
        message.set_content(
            f"Your verification code is: {otp_code}\n"
            f"The code expires in {settings.OTP_TTL_SECONDS // 60} minutes."
        )

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(message)
