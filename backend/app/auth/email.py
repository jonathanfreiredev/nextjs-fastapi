import logging

from app.settings import settings
from app.users.models import User

logger = logging.getLogger(__name__)


async def send_email(to: str, subject: str, body: str) -> None:
    """Deliver an email.

    In development the message is written to the logs. In production, replace
    this with a real provider (Resend, Amazon SES, SMTP...).
    """
    logger.info("Email to %s | %s\n%s", to, subject, body)


async def send_verification_email(user: User, token: str) -> None:
    link = f"{settings.frontend_url}/verify-email?token={token}"
    await send_email(user.email, "Verify your email", f"Verify your email: {link}")


async def send_reset_password_email(user: User, token: str) -> None:
    link = f"{settings.frontend_url}/reset-password?token={token}"
    await send_email(user.email, "Reset your password", f"Reset your password: {link}")
