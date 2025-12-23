from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy import create_engine
from app.core.config import settings


class Base(DeclarativeBase):
    pass


# Create async engine with pooling
engine = create_async_engine(
    settings.database_url,
    echo=settings.sqlalchemy_echo,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    pool_pre_ping=True,
    future=True,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Create sync engine for CRUD operations
sync_engine = create_engine(
    settings.database_url.replace("postgresql+asyncpg://", "postgresql://"),
    echo=settings.sqlalchemy_echo,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    pool_pre_ping=True,
)

# Create sync session factory
SessionLocal = sessionmaker(
    sync_engine,
    class_=Session,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """Dependency to get async database session."""
    async with async_session_maker() as session:
        yield session


def get_sync_db() -> Session:
    """Dependency to get sync database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
