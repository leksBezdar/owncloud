import asyncio
from typing import AsyncGenerator

import pytest
from async_asgi_testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from src.database import get_async_session, metadata
from src.config import (TEST_DB_HOST, TEST_DB_NAME, TEST_DB_PASS, TEST_DB_PORT,
                        TEST_DB_USER)
from src.main import app

# DATABASE
DATABASE_URL_TEST = f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASS}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
metadata.bind = engine_test

async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session

# @pytest.fixture(autouse=True, scope='session')
# async def prepare_database():
#     async with engine_test.begin() as conn:
#         await conn.run_sync(metadata.create_all)
#     yield
#     async with engine_test.begin() as conn:
#         await conn.run_sync(metadata.drop_all)

# SETUP
@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    

# @pytest.fixture(scope="session")
# async def ac() -> AsyncGenerator[AsyncClient, None]:
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         yield ac


@pytest.fixture
async def client():
    host, port = "127.0.0.1", "8000"
    scope = {"client": (host, port)}

    async with TestClient(
        app, scope=scope
    ) as client:
        yield client



