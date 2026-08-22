from httpx import AsyncClient


async def test_create_link(authenticated_ac: AsyncClient):
    response = await authenticated_ac.post(
        "/api/v1/links/", json={"original_url": "https://example.com"}
    )
    assert response.status_code == 201
    assert response.json()["original_url"] == "https://example.com/"
    assert "short_code" in response.json()


async def test_create_link_without_scheme(authenticated_ac: AsyncClient):
    response = await authenticated_ac.post(
        "/api/v1/links/", json={"original_url": "chat.deepseek.com"}
    )
    assert response.status_code == 201
    assert response.json()["original_url"] == "https://chat.deepseek.com/"


async def test_create_link_invalid_url(authenticated_ac: AsyncClient):
    response = await authenticated_ac.post(
        "/api/v1/links/", json={"original_url": "invalid url with spaces"}
    )
    assert response.status_code == 422


async def test_create_link_unauthenticated(ac: AsyncClient):
    response = await ac.post("/api/v1/links/", json={"original_url": "https://example.com"})
    assert response.status_code == 401


async def test_get_user_links(authenticated_ac: AsyncClient):
    response = await authenticated_ac.get("/api/v1/links/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["original_url"] == "https://example.com/"


async def test_to_original_url(authenticated_ac: AsyncClient):
    create_response = await authenticated_ac.post(
        "/api/v1/links/", json={"original_url": "https://ya.ru"}
    )
    assert create_response.status_code == 201
    short_code = create_response.json()["short_code"]

    get_response = await authenticated_ac.get(
        f"/{short_code}", follow_redirects=False
    )
    assert get_response.status_code == 307
    assert get_response.url != "https://ya.ru/"
    assert get_response.headers["location"] == "https://ya.ru/"


async def test_redirect_not_found(authenticated_ac: AsyncClient):
    response = await authenticated_ac.get("/nonexistent", follow_redirects=False)
    assert response.status_code == 404
    assert response.json()["detail"] == "Link not found"


async def test_get_link_stats(authenticated_ac: AsyncClient):
    create_response = await authenticated_ac.post(
        "/api/v1/links/", json={"original_url": "https://stats-test.com"}
    )
    assert create_response.status_code == 201
    short_code = create_response.json()["short_code"]

    stats_response = await authenticated_ac.get(f"/api/v1/links/{short_code}/stats")
    assert stats_response.status_code == 200
    assert isinstance(stats_response.json(), list)
