from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.auth.security import get_password_hash, verify_password
from app.users import service as users_service
from app.users.models import User
from app.users.schemas import CreateUserDto, UpdateUserDto, UpdateUserPasswordDto

pytestmark = pytest.mark.anyio


def fake_db() -> MagicMock:
    """A fake AsyncSession: `add` is sync, `commit`/`refresh` are async."""
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db


def fake_get_user(users_by_email: dict[str, User | None]):
    async def _get_user(db, email):
        return users_by_email.get(email)

    return _get_user


def make_user(email: str = "jane@example.com", password: str = "supersecret") -> User:
    return User(email=email, full_name="Jane Doe", hashed_password=get_password_hash(password))


async def test_create_user_rejects_an_email_that_already_exists():
    existing = make_user()

    with (
        patch("app.users.service.get_user", new=fake_get_user({existing.email: existing})),
        pytest.raises(HTTPException) as exc,
    ):
        await users_service.create_user(
            fake_db(),
            CreateUserDto(email=existing.email, full_name="Jane Doe", password="supersecret"),
        )

    assert exc.value.status_code == 409


async def test_create_user_hashes_the_password_and_persists():
    db = fake_db()

    with patch("app.users.service.get_user", new=fake_get_user({})):
        user = await users_service.create_user(
            db,
            CreateUserDto(email="jane@example.com", full_name="Jane Doe", password="supersecret"),
        )

    assert user.email == "jane@example.com"
    assert user.hashed_password != "supersecret"
    assert verify_password("supersecret", user.hashed_password)
    db.add.assert_called_once_with(user)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(user)


async def test_update_user_rejects_an_email_owned_by_someone_else():
    current = make_user(email="a@example.com")
    other = make_user(email="b@example.com")

    with (
        patch(
            "app.users.service.get_user",
            new=fake_get_user({current.email: current, other.email: other}),
        ),
        pytest.raises(HTTPException) as exc,
    ):
        await users_service.update_user(
            fake_db(),
            current.email,
            UpdateUserDto(email=other.email, full_name="A"),
        )

    assert exc.value.status_code == 409


async def test_update_user_applies_the_new_values():
    current = make_user(email="a@example.com")
    db = fake_db()

    with patch(
        "app.users.service.get_user",
        new=fake_get_user({current.email: current, "new@example.com": None}),
    ):
        user = await users_service.update_user(
            db,
            current.email,
            UpdateUserDto(email="new@example.com", full_name="Jane Smith"),
        )

    assert user.email == "new@example.com"
    assert user.full_name == "Jane Smith"
    db.commit.assert_awaited_once()


async def test_update_password_rejects_a_wrong_current_password():
    user = make_user(password="supersecret")

    with (
        patch("app.users.service.get_user", new=fake_get_user({user.email: user})),
        pytest.raises(HTTPException) as exc,
    ):
        await users_service.update_user_password(
            fake_db(),
            user.email,
            UpdateUserPasswordDto(old_password="wrongpassword", new_password="newsecret123"),
        )

    assert exc.value.status_code == 400


async def test_update_password_stores_a_hash_of_the_new_password():
    user = make_user(password="supersecret")
    db = fake_db()

    with patch("app.users.service.get_user", new=fake_get_user({user.email: user})):
        await users_service.update_user_password(
            db,
            user.email,
            UpdateUserPasswordDto(old_password="supersecret", new_password="newsecret123"),
        )

    assert verify_password("newsecret123", user.hashed_password)
    assert not verify_password("supersecret", user.hashed_password)
    db.commit.assert_awaited_once()
