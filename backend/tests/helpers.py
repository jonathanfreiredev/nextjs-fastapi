from httpx import AsyncClient

DEFAULT_PASSWORD = "supersecret"


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def register(
    client: AsyncClient,
    email: str = "jane@example.com",
    password: str = DEFAULT_PASSWORD,
    full_name: str = "Jane Doe",
):
    response = await client.post(
        "/auth/register",
        json={"email": email, "password": password, "full_name": full_name},
    )
    assert response.status_code == 201, response.text
    return response.json()


async def login(
    client: AsyncClient,
    email: str = "jane@example.com",
    password: str = DEFAULT_PASSWORD,
) -> str:
    response = await client.post(
        "/auth/jwt/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


async def signup(
    client: AsyncClient,
    email: str = "jane@example.com",
    password: str = DEFAULT_PASSWORD,
    full_name: str = "Jane Doe",
) -> str:
    """Register a user and return a usable access token."""
    await register(client, email=email, password=password, full_name=full_name)
    return await login(client, email=email, password=password)
