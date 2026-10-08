from httpx import AsyncClient


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def signup_tokens(
    client: AsyncClient,
    email: str = "jane@example.com",
    password: str = "supersecret",
    full_name: str = "Jane Doe",
) -> dict[str, str]:
    response = await client.post(
        "/auth/signup",
        json={"full_name": full_name, "email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()


async def signup(
    client: AsyncClient,
    email: str = "jane@example.com",
    password: str = "supersecret",
    full_name: str = "Jane Doe",
) -> str:
    tokens = await signup_tokens(client, email=email, password=password, full_name=full_name)
    return tokens["access_token"]
