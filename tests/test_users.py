from decimal import Decimal

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from database import get_session
from src.main import app
from users.models import Base


@pytest_asyncio.fixture(scope="function")
async def async_client():

    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    test_session_maker = async_sessionmaker(bind=test_engine)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_session():
        async with test_session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_register_user(async_client):
    response = await async_client.post(
        "/api/v1/register", json={"login": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["login"] == "testuser"
    assert "id" in data


@pytest.mark.asyncio
async def test_login_user(async_client):
    await async_client.post(
        "/api/v1/register", json={"login": "testuser", "password": "testpass"}
    )

    response = await async_client.post(
        "/api/v1/token", json={"login": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_token_refresh(async_client):
    await async_client.post(
        "/api/v1/register", json={"login": "testuser", "password": "testpass"}
    )
    login_response = await async_client.post(
        "/api/v1/token", json={"login": "testuser", "password": "testpass"}
    )
    refresh_token = login_response.json()["refresh_token"]

    response = await async_client.post(
        "/api/v1/token/refresh", json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_access_protected_route(async_client):
    await async_client.post(
        "/api/v1/register", json={"login": "testuser", "password": "testpass"}
    )
    login_response = await async_client.post(
        "/api/v1/token", json={"login": "testuser", "password": "testpass"}
    )
    access_token = login_response.json()["access_token"]

    response = await async_client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["login"] == "testuser"


@pytest.mark.asyncio
async def test_register_existing_user(async_client):
    await async_client.post(
        "/api/v1/register", json={"login": "testuser", "password": "testpass"}
    )
    response = await async_client.post(
        "/api/v1/register", json={"login": "testuser", "password": "testpass"}
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this login already exists"


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client):
    await async_client.post(
        "/api/v1/register", json={"login": "testuser", "password": "testpass"}
    )
    response = await async_client.post(
        "/api/v1/token", json={"login": "testuser", "password": "wrongpass"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "invalid login or password"


@pytest.mark.asyncio
async def test_access_protected_route_without_token(async_client):
    response = await async_client.get("/api/v1/users/me")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_add_money(async_client):
    register_response = await async_client.post(
        "/api/v1/register", json={"login": "testuser", "password": "testpass"}
    )
    user_id = register_response.json()["id"]
    login_response = await async_client.post(
        "/api/v1/token", json={"login": "testuser", "password": "testpass"}
    )
    access_token = login_response.json()["access_token"]

    response = await async_client.post(
        f"/api/v1/users/{user_id}/add_money",
        json={"amount": 100.50},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response = await async_client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert Decimal(data["money_balance"]) == Decimal("100.5")
