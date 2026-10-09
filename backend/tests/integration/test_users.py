import pytest

from tests.helpers import auth_header, signup

pytestmark = pytest.mark.anyio


async def test_me_requires_authentication(client):
    response = await client.get("/users/me")

    assert response.status_code == 401


async def test_me_returns_the_current_user(client):
    token = await signup(client, email="jane@example.com", full_name="Jane Doe")

    response = await client.get("/users/me", headers=auth_header(token))

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "jane@example.com"
    assert body["full_name"] == "Jane Doe"


async def test_update_profile(client):
    token = await signup(client, email="jane@example.com", full_name="Jane Doe")

    response = await client.patch(
        "/users/me",
        json={"full_name": "Jane Smith", "email": "jane.smith@example.com"},
        headers=auth_header(token),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] == "Jane Smith"
    assert body["email"] == "jane.smith@example.com"


async def test_changing_email_keeps_the_token_valid(client):
    # `sub` is the user id (not the email), so the token survives an email change.
    token = await signup(client, email="old@example.com")
    headers = auth_header(token)

    response = await client.patch(
        "/users/me",
        json={"email": "new@example.com"},
        headers=headers,
    )
    assert response.status_code == 200

    assert (await client.get("/users/me", headers=headers)).status_code == 200


async def test_update_profile_to_an_existing_email_is_rejected(client):
    token_a = await signup(client, email="a@example.com", full_name="A")
    await signup(client, email="b@example.com", full_name="B")

    response = await client.patch(
        "/users/me",
        json={"email": "b@example.com"},
        headers=auth_header(token_a),
    )

    assert response.status_code == 400


async def test_change_password_with_wrong_current_password(client):
    token = await signup(client, password="supersecret")

    response = await client.put(
        "/users/me/password/",
        json={"old_password": "wrongpassword", "new_password": "newsecret123"},
        headers=auth_header(token),
    )

    assert response.status_code == 400


async def test_change_password_then_login_with_the_new_one(client):
    token = await signup(client, email="jane@example.com", password="supersecret")

    changed = await client.put(
        "/users/me/password/",
        json={"old_password": "supersecret", "new_password": "newsecret123"},
        headers=auth_header(token),
    )
    assert changed.status_code == 200

    old_login = await client.post(
        "/auth/jwt/login",
        data={"username": "jane@example.com", "password": "supersecret"},
    )
    assert old_login.status_code == 400

    new_login = await client.post(
        "/auth/jwt/login",
        data={"username": "jane@example.com", "password": "newsecret123"},
    )
    assert new_login.status_code == 200
