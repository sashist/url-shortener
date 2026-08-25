from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from testcontainers.community.postgres import PostgresContainer

from src.api.deps import get_db
from src.core.config import settings
from src.main import app


@pytest.fixture(scope="session", autouse=True)
def check_test_mode() -> None:
    assert settings.MODE == "TEST", "Tests must be run in TEST mode"


@pytest.fixture(autouse=True)
def mock_redis():
    with patch("src.services.links.redis_manager") as mock:
        mock.get = AsyncMock(return_value=None)
        mock.set = AsyncMock(return_value=True)
        mock.delete = AsyncMock(return_value=True)
        yield mock


@pytest.fixture(autouse=True)
def mock_rabbitmq():
    with patch("src.api.links.rabbit_manager") as mock:
        mock.publish_event = AsyncMock(return_value=True)
        yield mock


@pytest.fixture(scope="session")
def postgres_container(check_test_mode) -> PostgresContainer:
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest_asyncio.fixture(scope="session")
async def db_engine(
    postgres_container: PostgresContainer,
) -> AsyncGenerator[AsyncEngine, None]:
    async_url = postgres_container.get_connection_url(driver="asyncpg")
    engine = create_async_engine(async_url, echo=False, poolclass=NullPool)

    def do_upgrade(connection):
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")

    async with engine.begin() as conn:
        await conn.run_sync(do_upgrade)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database(
    db_engine: AsyncEngine,
) -> AsyncGenerator[None, None]:
    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="session")
async def ac(setup_database) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="session", autouse=True)
async def register_user(ac: AsyncClient, setup_database):
    await ac.post(
        "/api/v1/auth/register", json={"email": "moonlord@ex.com", "password": "password123"}
    )


@pytest_asyncio.fixture(scope="session")
async def authenticated_ac(register_user, setup_database) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.post(
            "/api/v1/auth/login", json={"email": "moonlord@ex.com", "password": "password123"}
        )
        token = res.json()["access_token"]
        client.headers["Authorization"] = f"Bearer {token}"
        yield client
