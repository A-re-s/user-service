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
