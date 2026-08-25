from httpx import AsyncClient

from src.core.security import create_access_token, decode_token


async def test_register(ac: AsyncClient):
    response = await ac.post(
        "/api/v1/auth/register", json={"email": "testuser@example.com", "password": "testpass"}
    )
    assert response.status_code == 201


async def test_register_duplicate_email(ac: AsyncClient):
    response = await ac.post(
        "/api/v1/auth/register", json={"email": "testuser@example.com", "password": "testpass"}
    )
    assert response.status_code == 400


async def test_login(ac: AsyncClient):
    response = await ac.post(
        "/api/v1/auth/register",
        json={"email": "testuser2@example.com", "password": "testpass"},
    )
    assert response.status_code == 201

    response = await ac.post(
        "/api/v1/auth/login", json={"email": "testuser2@example.com", "password": "testpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.cookies
    assert ac.cookies["refresh_token"]


async def test_get_me(authenticated_ac: AsyncClient):
    response = await authenticated_ac.get("/api/v1/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "full_name" in data
    assert "id" in data


async def test_refresh(authenticated_ac: AsyncClient):
    response = await authenticated_ac.post("/api/v1/auth/refresh")
    old_token = authenticated_ac.headers["Authorization"]
    assert response.status_code == 200
    data = response.json()
    new_token = data["access_token"]
    assert new_token != old_token
    assert "access_token" in data


async def test_get_me_unauthenticated(ac: AsyncClient):
    response = await ac.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_logout(authenticated_ac: AsyncClient):
    response = await authenticated_ac.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.json() == {"message": "Logged out successfully"}



def test_decode_and_encode_access_token():
    data = {"user_id": 1}
    jwt_token = create_access_token(data)
    assert jwt_token
    assert isinstance(jwt_token, str)

    payload = decode_token(jwt_token)
    assert payload
    assert payload["user_id"] == data["user_id"]
