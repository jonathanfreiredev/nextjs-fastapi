from httpx import AsyncClient


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def signup(
    client: AsyncClient,
    email: str = "jane@example.com",
    password: str = "supersecret",
    full_name: str = "Jane Doe",
) -> str:
    response = await client.post(
        "/auth/signup",
        json={"full_name": full_name, "email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]
