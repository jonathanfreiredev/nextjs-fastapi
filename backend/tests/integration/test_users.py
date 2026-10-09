import uuid

import pytest

from tests.auth_stub import mint_token
from tests.helpers import auth_header

pytestmark = pytest.mark.anyio


async def test_me_requires_authentication(client):
    response = await client.get("/users/me")

    assert response.status_code == 401


async def test_me_rejects_an_invalid_token(client):
    response = await client.get("/users/me", headers=auth_header("not-a-jwt"))

    assert response.status_code == 401


async def test_me_provisions_a_profile_from_the_token(client):
    token = mint_token(email="jane@example.com", full_name="Jane Doe")

    response = await client.get("/users/me", headers=auth_header(token))

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "jane@example.com"
    assert body["full_name"] == "Jane Doe"


async def test_provisioning_is_idempotent(client):
    token = mint_token(subject=uuid.uuid4())
    headers = auth_header(token)

    first = await client.get("/users/me", headers=headers)
    second = await client.get("/users/me", headers=headers)

    assert first.status_code == 200
    assert first.json()["id"] == second.json()["id"]


async def test_profile_email_is_kept_in_sync_with_the_token(client):
    subject = uuid.uuid4()

    old_token = mint_token(subject=subject, email="old@example.com")
    new_token = mint_token(subject=subject, email="new@example.com")

    await client.get("/users/me", headers=auth_header(old_token))
    response = await client.get("/users/me", headers=auth_header(new_token))

    assert response.json()["email"] == "new@example.com"


async def test_update_profile(client):
    token = mint_token(full_name="Jane Doe")

    response = await client.patch(
        "/users/me",
        json={"full_name": "Jane Smith"},
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Jane Smith"
