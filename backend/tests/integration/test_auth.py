import asyncio

import pytest

from tests.helpers import auth_header, signup, signup_tokens

pytestmark = pytest.mark.anyio

PAYLOAD = {
    "full_name": "Jane Doe",
    "email": "jane@example.com",
    "password": "supersecret",
}


async def test_signup_returns_a_token_pair(client):
    response = await client.post("/auth/signup", json=PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]


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


async def test_refresh_returns_a_new_usable_access_token(client):
    tokens = await signup_tokens(client)

    response = await client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

    assert response.status_code == 200
    new_tokens = response.json()
    assert new_tokens["refresh_token"] != tokens["refresh_token"]

    me = await client.get("/users/me/", headers=auth_header(new_tokens["access_token"]))
    assert me.status_code == 200


async def test_refresh_rotates_and_revokes_the_previous_token(client):
    tokens = await signup_tokens(client)

    first = await client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert first.status_code == 200

    # Reusing the original refresh token must fail (it was rotated out).
    replay = await client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert replay.status_code == 401


async def test_refresh_with_an_invalid_token_is_rejected(client):
    response = await client.post("/auth/refresh", json={"refresh_token": "not-a-real-token"})

    assert response.status_code == 401


async def test_logout_revokes_the_refresh_token(client):
    tokens = await signup_tokens(client)

    logout = await client.post("/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert logout.status_code == 200

    response = await client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 401


async def test_logout_all_invalidates_previous_tokens(client):
    token = await signup(client)
    headers = auth_header(token)

    assert (await client.get("/users/me/", headers=headers)).status_code == 200

    # `iat` and `tokens_valid_after` are both second-precision, so the token and
    # the logout must land in different seconds to be distinguishable.
    await asyncio.sleep(1.05)

    assert (await client.post("/auth/logout-all", headers=headers)).status_code == 200

    assert (await client.get("/users/me/", headers=headers)).status_code == 401
