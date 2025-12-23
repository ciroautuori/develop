import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings

# Database URL from settings - NO hardcoded credentials
DATABASE_URL = settings.DATABASE_URL

# Connection pool configuration
POOL_CONFIG = {
    # Pool size: number of connections to maintain in the pool
    "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
    # Max overflow: additional connections beyond pool_size
    "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
    # Pool timeout: seconds to wait for a connection
    "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
    # Pool recycle: seconds before connection is recreated
    "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "3600")),  # 1 hour
    # Pool pre-ping: validate connections before use
    "pool_pre_ping": os.getenv("DB_POOL_PRE_PING", "true").lower() == "true",
    # Poolclass: use QueuePool for PostgreSQL
    "poolclass": QueuePool,
}

# Creazione engine per la connessione al database con connection pooling
engine = create_engine(
    DATABASE_URL,
    **POOL_CONFIG,
    # Additional engine options
    echo=os.getenv("DB_ECHO", "false").lower() == "true",  # Log SQL queries
    future=True,  # Use SQLAlchemy 2.0 style
)

# LOW-001: Setup query performance logging
if os.getenv("ENABLE_QUERY_LOGGING", "false").lower() == "true":
    from app.infrastructure.database.query_logger import setup_sqlalchemy_query_logging

    setup_sqlalchemy_query_logging(engine)

# Definizione della sessione locale per la gestione delle transazioni
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Definizione della base della ORM per la gestione delle entità
Base = declarative_base()

# Funzione per ottenere una sessione locale per la gestione delle transazioni
def get_db():
    # Usa sempre la SessionLocal di questo modulo.
    # Nota: app.main aggiorna database.SessionLocal quando ricrea l'engine,
    # quindi qui apriamo semplicemente una nuova sessione.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# ASYNC DATABASE SUPPORT
# ============================================================================

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Convert sync URL to async URL (postgresql:// -> postgresql+asyncpg://)
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create Async Engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    **{k: v for k, v in POOL_CONFIG.items() if k != "poolclass"},  # Filter incompatible args if any
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    future=True,
)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

async def get_async_db():
    """
    Get async database session.
    """
    async with AsyncSessionLocal() as session:
        yield session
