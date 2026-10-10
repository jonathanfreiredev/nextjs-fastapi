import pytest

from app.db.session import get_async_db_session
from app.main import app

pytestmark = pytest.mark.anyio


async def test_liveness_does_not_require_authentication(client):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_readiness_reports_the_database_is_up(client):
    response = await client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "up"}


async def test_readiness_reports_unavailable_when_the_database_is_down(client):
    class BrokenSession:
        async def execute(self, *args, **kwargs):
            raise RuntimeError("database is down")

    async def override_broken_session():
        yield BrokenSession()

    app.dependency_overrides[get_async_db_session] = override_broken_session

    response = await client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "database": "down"}
