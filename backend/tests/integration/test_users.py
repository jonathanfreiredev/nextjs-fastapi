import pytest

from tests.helpers import auth_header, signup

pytestmark = pytest.mark.anyio


async def test_me_requires_authentication(client):
    response = await client.get("/users/me/")

    # HTTPBearer returns 401 when no credentials are provided.
    assert response.status_code == 401


async def test_me_returns_the_current_user(client):
    token = await signup(client, email="jane@example.com", full_name="Jane Doe")

    response = await client.get("/users/me/", headers=auth_header(token))

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "jane@example.com"
    assert body["full_name"] == "Jane Doe"


async def test_update_profile(client):
    token = await signup(client, email="jane@example.com", full_name="Jane Doe")

    response = await client.put(
        "/users/me/",
        json={"full_name": "Jane Smith", "email": "jane.smith@example.com"},
        headers=auth_header(token),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] == "Jane Smith"
    assert body["email"] == "jane.smith@example.com"


async def test_update_profile_to_an_existing_email_conflicts(client):
    token_a = await signup(client, email="a@example.com", full_name="A")
    await signup(client, email="b@example.com", full_name="B")

    response = await client.put(
        "/users/me/",
        json={"full_name": "A", "email": "b@example.com"},
        headers=auth_header(token_a),
    )

    assert response.status_code == 409


async def test_change_password_with_wrong_current_password(client):
    token = await signup(client, password="supersecret")

    response = await client.put(
        "/users/me/password/",
        json={"old_password": "wrongpassword", "new_password": "newsecret123"},
        headers=auth_header(token),
    )

    assert response.status_code == 400


async def test_change_password_then_login_with_the_new_one(client):
    token = await signup(client, password="supersecret")
    headers = auth_header(token)

    changed = await client.put(
        "/users/me/password/",
        json={"old_password": "supersecret", "new_password": "newsecret123"},
        headers=headers,
    )
    assert changed.status_code == 200

    old_login = await client.post(
        "/auth/login", json={"email": "jane@example.com", "password": "supersecret"}
    )
    assert old_login.status_code == 401

    new_login = await client.post(
        "/auth/login", json={"email": "jane@example.com", "password": "newsecret123"}
    )
    assert new_login.status_code == 200


async def test_changing_email_invalidates_the_old_token(client):
    token = await signup(client, email="old@example.com")
    headers = auth_header(token)

    response = await client.put(
        "/users/me/",
        json={"full_name": "Jane", "email": "new@example.com"},
        headers=headers,
    )
    assert response.status_code == 200

    # The old token's subject is the old email, so it no longer resolves.
    assert (await client.get("/users/me/", headers=headers)).status_code == 401
