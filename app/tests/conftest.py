import asyncio
import os
from unittest.mock import AsyncMock
from urllib.parse import quote_plus

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.agent.client import llm_client
from app.db.models import Base

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_USER = os.getenv("POSTGRES_USER")
encoded_password = quote_plus(POSTGRES_PASSWORD)
TEST_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{encoded_password}@localhost:5432/test_db"



@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncSession:
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        async with session.begin():
            yield session


@pytest.fixture
def mock_llm(monkeypatch):
    async_mock = AsyncMock()

    monkeypatch.setattr(llm_client, "chat", async_mock)
    return async_mock
