import uuid
from typing import Annotated

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import email
from app.auth.constants import (
    RESET_PASSWORD_TOKEN_LIFETIME_SECONDS,
    VERIFICATION_TOKEN_LIFETIME_SECONDS,
)
from app.db.session import get_async_db_session
from app.settings import settings
from app.users.models import User


async def get_user_db(
    session: Annotated[AsyncSession, Depends(get_async_db_session)],
) -> SQLAlchemyUserDatabase:
    yield SQLAlchemyUserDatabase(session, User)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.auth_secret
    verification_token_secret = settings.auth_secret
    reset_password_token_lifetime_seconds = RESET_PASSWORD_TOKEN_LIFETIME_SECONDS
    verification_token_lifetime_seconds = VERIFICATION_TOKEN_LIFETIME_SECONDS

    async def on_after_register(self, user: User, request: Request | None = None) -> None:
        # Send the verification email as soon as the account is created.
        if not user.is_verified:
            await self.request_verify(user, request)

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ) -> None:
        await email.send_verification_email(user, token)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ) -> None:
        await email.send_reset_password_email(user, token)


async def get_user_manager(
    user_db: Annotated[SQLAlchemyUserDatabase, Depends(get_user_db)],
) -> UserManager:
    yield UserManager(user_db)
