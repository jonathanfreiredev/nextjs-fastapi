import asyncio

import pytest

from tests.helpers import auth_header, signup

pytestmark = pytest.mark.anyio

PAYLOAD = {
    "full_name": "Jane Doe",
    "email": "jane@example.com",
    "password": "supersecret",
}


async def test_signup_returns_token(client):
    response = await client.post("/auth/signup", json=PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


async def test_signup_with_duplicate_email_conflicts(client):
    await client.post("/auth/signup", json=PAYLOAD)

    response = await client.post("/auth/signup", json=PAYLOAD)

    assert response.status_code == 409


async def test_login_with_correct_credentials(client):
    await client.post("/auth/signup", json=PAYLOAD)

    response = await client.post(
        "/auth/login",
        json={"email": PAYLOAD["email"], "password": PAYLOAD["password"]},
    )

    assert response.status_code == 200
    assert response.json()["access_token"]


async def test_login_with_wrong_password(client):
    await client.post("/auth/signup", json=PAYLOAD)

    response = await client.post(
        "/auth/login",
        json={"email": PAYLOAD["email"], "password": "wrongpassword"},
    )

    assert response.status_code == 401


async def test_login_with_unknown_email(client):
    response = await client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "whatever123"},
    )

    assert response.status_code == 401


async def test_update_token_returns_a_usable_token(client):
    token = await signup(client)

    response = await client.post("/auth/update-token", headers=auth_header(token))

    assert response.status_code == 200
    new_token = response.json()["access_token"]

    me = await client.get("/users/me/", headers=auth_header(new_token))
    assert me.status_code == 200


async def test_logout_all_invalidates_previous_tokens(client):
    token = await signup(client)
    headers = auth_header(token)

    assert (await client.get("/users/me/", headers=headers)).status_code == 200

    # `iat` and `tokens_valid_after` are both second-precision, so the token and
    # the logout must land in different seconds to be distinguishable.
    await asyncio.sleep(1.05)

    assert (await client.post("/auth/logout-all", headers=headers)).status_code == 200

    assert (await client.get("/users/me/", headers=headers)).status_code == 401
