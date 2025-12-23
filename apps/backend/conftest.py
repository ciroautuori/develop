import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

# Import the actual database connection to reuse the real engine for tests
from app.database.database import async_session_maker, get_db
from app.main import app

# Import cache system
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_cache():
    """Setup cache for tests."""
    try:
        # Try to connect to Redis for cache
        redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
        FastAPICache.init(RedisBackend(redis_client), prefix="test-cache:")
    except Exception:
        # If Redis fails, use in-memory backend
        from fastapi_cache.backends.inmemory import InMemoryBackend
        FastAPICache.init(InMemoryBackend(), prefix="test-cache:")
    
    yield
    
    # Cleanup cache
    try:
        await FastAPICache.clear()
    except Exception:
        pass


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Create a database session using the real PostgreSQL container."""
    async with async_session_maker() as session:
        # Clean up any test data BEFORE starting the test
        from sqlalchemy import text
        
        # CLEAN EVERYTHING - Complete database reset for tests
        try:
            # Delete ALL data from ALL tables for clean tests
            await session.execute(text("DELETE FROM bando_logs"))
            await session.execute(text("DELETE FROM bando_configs"))  
            await session.execute(text("DELETE FROM bandi"))
            
            # Reset sequences to start from 1
            await session.execute(text("ALTER SEQUENCE bandi_id_seq RESTART WITH 1"))
            await session.execute(text("ALTER SEQUENCE bando_configs_id_seq RESTART WITH 1"))
            await session.execute(text("ALTER SEQUENCE bando_logs_id_seq RESTART WITH 1"))
            
            await session.commit()
        except Exception as e:
            # If cleanup fails, rollback and continue
            await session.rollback()
            print(f"Cleanup warning: {e}")  # Debug info
        
        try:
            yield session
        finally:
            # Always rollback any uncommitted changes
            await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """Create a test client with database override and cache."""
    
    # Use in-memory backend for tests (more reliable)
    from fastapi_cache.backends.inmemory import InMemoryBackend
    FastAPICache.init(InMemoryBackend(), prefix="test-cache:")
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()
    
    # Cleanup cache
    try:
        await FastAPICache.clear()
    except Exception:
        pass


@pytest.fixture
def sample_bando_data() -> dict:
    """Sample bando data for tests."""
    return {
        "title": "Test Bando Alfabetizzazione Digitale",
        "ente": "Test Ente",
        "link": "https://example.com/test-bando",
        "fonte": "comune_salerno",
        "status": "attivo",
        "descrizione": "Test descrizione per alfabetizzazione digitale",
        "keyword_match": "alfabetizzazione digitale"
    }


@pytest.fixture
def sample_config_data() -> dict:
    """Sample bando config data for tests."""
    return {
        "name": "Test Config",
        "email_enabled": True,
        "email_username": "test@example.com",
        "email_recipient": "admin@example.com",
        "keywords": ["alfabetizzazione digitale", "inclusione sociale"],
        "fonte_enabled": {
            "comune_salerno": True,
            "regione_campania": True,
            "csv_salerno": False,
            "fondazione_comunita": False
        }
    }


# Mock data for API tests
@pytest.fixture
def mock_admin_token() -> str:
    """Mock admin token for testing protected endpoints."""
    return "test-admin-token-123"


@pytest.fixture
def auth_headers(mock_admin_token: str) -> dict:
    """Authentication headers for admin endpoints."""
    return {"Authorization": f"Bearer {mock_admin_token}"}


@pytest.fixture
def sample_bando_data() -> dict:
    """Sample bando data for tests."""
    return {
        "title": "Test Bando Alfabetizzazione Digitale",
        "ente": "Test Ente",
        "link": "https://example.com/test-bando",
        "fonte": "comune_salerno",
        "status": "attivo",
        "descrizione": "Test descrizione per alfabetizzazione digitale",
        "keyword_match": "alfabetizzazione digitale"
    }


@pytest.fixture
def sample_config_data() -> dict:
    """Sample bando config data for tests."""
    return {
        "name": "Test Config",
        "email_enabled": True,
        "email_username": "test@example.com",
        "email_recipient": "admin@example.com",
        "keywords": ["alfabetizzazione digitale", "inclusione sociale"],
        "fonte_enabled": {
            "comune_salerno": True,
            "regione_campania": True,
            "csv_salerno": False,
            "fondazione_comunita": False
        }
    }


# Mock data for API tests
@pytest.fixture
def mock_admin_token() -> str:
    """Mock admin token for testing protected endpoints."""
    return "test-admin-token-123"


@pytest.fixture
def auth_headers(mock_admin_token: str) -> dict:
    """Authentication headers for admin endpoints."""
    return {"Authorization": f"Bearer {mock_admin_token}"}
