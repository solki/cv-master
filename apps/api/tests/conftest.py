import pytest
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient, ASGITransport

# Force test settings before importing app modules
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

from app.main import create_app
from app.db.base import Base
from app.db.session import get_db


@pytest.fixture(scope="session")
def _engine():
    """Create test database engine."""
    engine = create_async_engine(
        os.environ["DATABASE_URL"],
        echo=False,
    )
    return engine


@pytest.fixture(scope="session")
async def _create_tables(_engine):
    """Create all tables before tests."""
    async with _engine.begin() as conn:
        # Skip embedding table - requires pgvector
        await conn.run_sync(
            lambda sync_conn: Base.metadata.create_all(
                sync_conn,
                tables=[t for t in Base.metadata.sorted_tables if t.name != "embeddings"],
            )
        )
    yield
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    # Clean up test db file
    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest.fixture
async def _db_session(_engine, _create_tables):
    """Create a database session for each test."""
    session_factory = async_sessionmaker(
        _engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest.fixture
def app(_engine, _db_session):
    """Create a FastAPI test application with test DB override."""
    test_app = create_app()

    async def override_get_db():
        async with async_sessionmaker(
            _engine, class_=AsyncSession, expire_on_commit=False
        )() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    test_app.dependency_overrides[get_db] = override_get_db
    return test_app


@pytest.fixture
async def async_client(app):
    """Async HTTP client for testing API endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
