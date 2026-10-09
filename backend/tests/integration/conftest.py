import os
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.db.models import Base
from app.db.session import get_async_db_session
from app.main import app
from app.settings import settings


def _test_database_url() -> str:
    """Point at a dedicated test database next to the development one.

    Override with the TEST_DATABASE_URL environment variable when needed.
    """
    if override := os.environ.get("TEST_DATABASE_URL"):
        return override

    base_url, _, _ = settings.database_url.rpartition("/")
    return f"{base_url}/app_test"


TEST_DATABASE_URL = _test_database_url()


@pytest.fixture
def email_outbox(monkeypatch) -> dict[str, list[tuple[str, str]]]:
    """Capture verification and reset emails instead of sending them."""
    import app.auth.email as auth_email

    outbox: dict[str, list[tuple[str, str]]] = {"verify": [], "reset": []}

    async def fake_send_verification_email(user, token):
        outbox["verify"].append((user.email, token))

    async def fake_send_reset_password_email(user, token):
        outbox["reset"].append((user.email, token))

    monkeypatch.setattr(auth_email, "send_verification_email", fake_send_verification_email)
    monkeypatch.setattr(auth_email, "send_reset_password_email", fake_send_reset_password_email)

    return outbox


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    # A fresh engine per test keeps each test isolated and avoids sharing
    # connections across event loops. NullPool means no connection is cached.
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        yield session

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    # Swap the real database session for the test one, without touching the app.
    async def override_get_session() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_async_db_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client

    app.dependency_overrides.pop(get_async_db_session, None)
