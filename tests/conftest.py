import asyncio
from asyncio import AbstractEventLoop
from typing import AsyncGenerator, Generator, TypeAlias

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker


from src.database import Base
from src.database import get_async_session ,async_session_maker

from src.config import (TEST_DB_HOST, TEST_DB_PORT, TEST_DB_NAME, TEST_DB_USER, TEST_DB_PASS)

from src.main import app

# DATABASE
DATABASE_URL= f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASS}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"


SessionMaker: TypeAlias = sessionmaker[AsyncSession]


@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
    

@pytest.fixture(scope="session")
def client(app: FastAPI) -> TestClient:
    return TestClient(app)

@pytest.fixture(scope="session")
def app() -> FastAPI:
    app = create_app(config)
    initialise_routers(app)

    return app

@pytest.fixture(scope="session")
def engine() -> AsyncEngine:
    engine = create_async_engine(DATABASE_URL, echo=False)
    return engine


@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialise_test_db(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)