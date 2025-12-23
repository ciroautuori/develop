"""
Database Setup and Configuration

SQLAlchemy setup for PostgreSQL database with session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os

from src.infrastructure.logging import get_logger

logger = get_logger(__name__)

# Database URL from environment (PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback only for DEV if explicitly allowed, else Error
    if os.getenv("ENVIRONMENT", "development") == "development":
        DATABASE_URL = "postgresql://ironrep:ironrep@localhost:5432/ironrep"
        logger.warning("⚠️ using default local database URL")
    else:
        raise ValueError("DATABASE_URL env var is required in production!")

# Create engine for PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Check connection health
    echo=False  # Set to True for SQL logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def init_db():
    """Initialize database - create all tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database initialized successfully")


def get_db() -> Session:
    """
    Get database session for FastAPI dependency injection.

    Usage:
        @app.get("/")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    """
    Get database session context manager.

    Usage:
        with get_db_session() as db:
            db.add(obj)
            db.commit()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_db():
    """Drop all tables and recreate - USE WITH CAUTION!"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.warning("⚠️  Database reset completed")
