import jwt
import pytest

from app.auth.constants import ALGORITHM
from app.auth.keys import public_key
from tests.helpers import auth_header, register, signup

pytestmark = pytest.mark.anyio

PAYLOAD = {"email": "jane@example.com", "password": "supersecret", "full_name": "Jane Doe"}


async def test_register_creates_an_unverified_user_and_sends_a_verification_email(
    client, email_outbox
):
    response = await client.post("/auth/register", json=PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == PAYLOAD["email"]
    assert body["full_name"] == PAYLOAD["full_name"]
    assert body["is_verified"] is False
    assert len(email_outbox["verify"]) == 1


async def test_register_with_duplicate_email_is_rejected(client):
    await register(client)

    response = await client.post("/auth/register", json=PAYLOAD)

    assert response.status_code == 400


async def test_login_returns_an_rs256_access_token(client):
    await register(client)

    response = await client.post(
        "/auth/jwt/login",
        data={"username": PAYLOAD["email"], "password": PAYLOAD["password"]},
    )

    assert response.status_code == 200
    token = response.json()["access_token"]

    header = jwt.get_unverified_header(token)
    assert header["alg"] == ALGORITHM
    assert header["kid"]

    payload = jwt.decode(token, public_key, algorithms=[ALGORITHM], audience="fastapi-users:auth")
    assert payload["aud"] == ["fastapi-users:auth"]
    assert payload["sub"]


async def test_login_with_wrong_password_is_rejected(client):
    await register(client)

    response = await client.post(
        "/auth/jwt/login",
        data={"username": PAYLOAD["email"], "password": "wrongpassword"},
    )

    assert response.status_code == 400


async def test_login_with_unknown_email_is_rejected(client):
    response = await client.post(
        "/auth/jwt/login",
        data={"username": "nobody@example.com", "password": "whatever123"},
    )

    assert response.status_code == 400


async def test_logout_returns_no_content(client):
    token = await signup(client)

    response = await client.post("/auth/jwt/logout", headers=auth_header(token))

    assert response.status_code == 204


async def test_jwks_exposes_the_rs256_public_key(client):
    response = await client.get("/.well-known/jwks.json")

    assert response.status_code == 200
    key = response.json()["keys"][0]
    assert key["kty"] == "RSA"
    assert key["alg"] == "RS256"
    assert key["kid"]


async def test_email_verification_flow(client, email_outbox):
    await register(client)
    _, token = email_outbox["verify"][0]

    response = await client.post("/auth/verify", json={"token": token})

    assert response.status_code == 200
    assert response.json()["is_verified"] is True

    # A verification token is single successful use only.
    reused = await client.post("/auth/verify", json={"token": token})
    assert reused.status_code == 400


async def test_forgot_and_reset_password_flow(client, email_outbox):
    await register(client)

    forgot = await client.post("/auth/forgot-password", json={"email": PAYLOAD["email"]})
    assert forgot.status_code == 202

    _, token = email_outbox["reset"][0]
    reset = await client.post(
        "/auth/reset-password",
        json={"token": token, "password": "newsecret123"},
    )
    assert reset.status_code == 200

    old_login = await client.post(
        "/auth/jwt/login",
        data={"username": PAYLOAD["email"], "password": PAYLOAD["password"]},
    )
    assert old_login.status_code == 400

    new_login = await client.post(
        "/auth/jwt/login",
        data={"username": PAYLOAD["email"], "password": "newsecret123"},
    )
    assert new_login.status_code == 200
