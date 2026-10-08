from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

import jwt
import pytest
from fastapi import HTTPException

from app.auth import service as auth_service
from app.auth.constants import ALGORITHM, SECRET_KEY
from app.auth.security import get_password_hash
from app.users.models import User
from app.users.schemas import LoginUserDto

pytestmark = pytest.mark.anyio


def decode(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def make_user(
    email: str = "jane@example.com",
    full_name: str = "Jane Doe",
    password: str = "supersecret",
    tokens_valid_after: datetime | None = None,
) -> User:
    return User(
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
        tokens_valid_after=tokens_valid_after or datetime.now(UTC),
    )


def test_create_access_token_carries_the_subject_and_timestamps():
    token = auth_service.create_access_token({"sub": "jane@example.com"})

    payload = decode(token)
    assert payload["sub"] == "jane@example.com"
    assert "iat" in payload
    assert "exp" in payload


async def test_get_token_builds_a_bearer_token_for_the_user():
    user = make_user()

    token = await auth_service.get_token(user)

    payload = decode(token.access_token)
    assert token.token_type == "bearer"
    assert payload["sub"] == user.email
    assert payload["name"] == user.full_name


async def test_authenticate_user_returns_false_when_the_user_does_not_exist():
    with patch("app.users.service.get_user", new=AsyncMock(return_value=None)):
        result = await auth_service.authenticate_user(
            AsyncMock(), LoginUserDto(email="nobody@example.com", password="whatever123")
        )

    assert result is False


async def test_authenticate_user_returns_false_for_a_wrong_password():
    user = make_user(password="supersecret")

    with patch("app.users.service.get_user", new=AsyncMock(return_value=user)):
        result = await auth_service.authenticate_user(
            AsyncMock(), LoginUserDto(email=user.email, password="wrongpassword")
        )

    assert result is False


async def test_authenticate_user_returns_the_user_for_valid_credentials():
    user = make_user(password="supersecret")

    with patch("app.users.service.get_user", new=AsyncMock(return_value=user)):
        result = await auth_service.authenticate_user(
            AsyncMock(), LoginUserDto(email=user.email, password="supersecret")
        )

    assert result is user


async def test_verify_token_rejects_a_garbage_token():
    with pytest.raises(HTTPException) as exc:
        await auth_service.verify_token(AsyncMock(), "not-a-jwt")

    assert exc.value.status_code == 401


async def test_verify_token_rejects_an_expired_token():
    token = auth_service.create_access_token(
        {"sub": "jane@example.com"}, expires_delta=timedelta(minutes=-1)
    )

    with pytest.raises(HTTPException) as exc:
        await auth_service.verify_token(AsyncMock(), token)

    assert exc.value.status_code == 401


async def test_verify_token_rejects_a_token_issued_before_logout_all():
    # The user's tokens are only valid from the future, so any token issued now is invalid.
    user = make_user(tokens_valid_after=datetime.now(UTC) + timedelta(minutes=1))
    token = auth_service.create_access_token({"sub": user.email})

    with (
        patch("app.users.service.get_user", new=AsyncMock(return_value=user)),
        pytest.raises(HTTPException) as exc,
    ):
        await auth_service.verify_token(AsyncMock(), token)

    assert exc.value.status_code == 401


async def test_verify_token_rejects_a_token_for_a_deleted_user():
    token = auth_service.create_access_token({"sub": "ghost@example.com"})

    with (
        patch("app.users.service.get_user", new=AsyncMock(return_value=None)),
        pytest.raises(HTTPException) as exc,
    ):
        await auth_service.verify_token(AsyncMock(), token)

    assert exc.value.status_code == 401


async def test_verify_token_returns_the_user_for_a_valid_token():
    user = make_user(tokens_valid_after=datetime.now(UTC) - timedelta(minutes=1))
    token = auth_service.create_access_token({"sub": user.email})

    with patch("app.users.service.get_user", new=AsyncMock(return_value=user)):
        result = await auth_service.verify_token(AsyncMock(), token)

    assert result is user


async def test_logout_all_truncates_tokens_valid_after_to_seconds():
    user = make_user()

    with patch("app.users.service.get_user", new=AsyncMock(return_value=user)):
        await auth_service.logout_all_sessions(AsyncMock(), user.email)

    assert user.tokens_valid_after.microsecond == 0


async def test_token_issued_right_after_logout_all_is_still_valid():
    # Regression: with a microsecond `tokens_valid_after` vs a second-precision
    # `iat`, a token issued in the same second was rejected for up to 1 second.
    user = make_user()

    with patch("app.users.service.get_user", new=AsyncMock(return_value=user)):
        await auth_service.logout_all_sessions(AsyncMock(), user.email)

    token = auth_service.create_access_token({"sub": user.email})

    with patch("app.users.service.get_user", new=AsyncMock(return_value=user)):
        result = await auth_service.verify_token(AsyncMock(), token)

    assert result is user
