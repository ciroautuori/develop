"""Application Startup Events Module
Handles database initialization and startup procedures.
"""

import logging
import os
import time

import psycopg2
from sqlalchemy import create_engine, text

from app.infrastructure import database
from app.infrastructure.database.session import POOL_CONFIG, Base
from app.infrastructure.monitoring.db_monitor import create_db_monitor
from app.infrastructure.monitoring.logging_middleware import DatabaseLoggingMiddleware
from app.infrastructure.scheduler import start_all_schedulers, stop_all_schedulers

logger = logging.getLogger("portfolio-backend")

class StartupManager:
    """Manages application startup procedures including database initialization."""

    def __init__(self):
        self.db_monitor = None
        self.db_logging = None

    async def ensure_database_connection(self) -> bool:
        """Ensure database connection with retry logic.

        Returns:
            True if connection successful, False otherwise
        """
        db_url = os.getenv("DATABASE_URL")
        max_retries = int(os.getenv("DB_MAX_RETRIES", "10"))
        retry_delay = int(os.getenv("DB_RETRY_DELAY", "2"))

        for attempt in range(max_retries):
            try:
                logger.info(f"Attempt {attempt + 1}/{max_retries}: Testing database connection...")

                # Test database connection with psycopg2
                conn = psycopg2.connect(db_url)
                with conn.cursor() as cur:
                    cur.execute("SELECT current_user, current_database(), version();")
                    user, db, version = cur.fetchone()
                    logger.info(f"✅ psycopg2: Connected as: {user}, DB: {db}")
                conn.close()

                # Test SQLAlchemy engine connection
                try:
                    # Force engine disposal to clear connection pool
                    database.engine.dispose()

                    with database.engine.connect() as sqlalchemy_conn:
                        result = sqlalchemy_conn.execute(
                            text("SELECT current_user, current_database()")
                        )
                        sa_user, sa_db = result.fetchone()
                        logger.info(f"✅ SQLAlchemy: Connected as: {sa_user}, DB: {sa_db}")
                    return True

                except Exception as sa_error:
                    logger.error(f"❌ SQLAlchemy engine failed: {sa_error}")

                    if "password authentication failed" in str(sa_error):
                        # Try to recreate engine with current DATABASE_URL
                        if self._recreate_engine(db_url):
                            return True
                    return False

            except psycopg2.Error as e:
                logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error("❌ Failed to connect to database after all retries")
                    return False

            except Exception as e:
                logger.error(f"Unexpected error in database connection: {e}")
                return False

        return False

    def _recreate_engine(self, db_url: str) -> bool:
        """Recreate SQLAlchemy engine with fresh connection.

        Args:
            db_url: Database connection URL

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Recreating SQLAlchemy engine with fresh URL...")

            # Create new engine with correct URL
            new_engine = create_engine(db_url, **POOL_CONFIG, echo=False, future=True)

            # Test the new engine
            with new_engine.connect() as fresh_conn:
                result = fresh_conn.execute(text("SELECT current_user, current_database()"))
                sa_user, sa_db = result.fetchone()
                logger.info(f"✅ SQLAlchemy (recreated): Connected as: {sa_user}, DB: {sa_db}")

            # Replace the old engine globally
            database.engine.dispose()  # Clean up old engine
            database.engine = new_engine

            # Update SessionLocal to use new engine
            from app.infrastructure.database import SessionLocal

            SessionLocal.configure(bind=new_engine)

            logger.info("✅ Database engine and session updated globally")
            return True

        except Exception as recreate_error:
            logger.error(f"❌ Engine recreation failed: {recreate_error}")
            return False

    async def initialize_database(self) -> bool:
        """Initialize database tables and monitoring.

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("🚀 Starting database initialization...")

            # First ensure database connection
            db_ready = await self.ensure_database_connection()

            if db_ready:
                # Create database tables
                Base.metadata.create_all(bind=database.engine)

                # Setup database logging
                self.db_logging = DatabaseLoggingMiddleware()
                self.db_logging.register_events(database.engine)

                # Setup database monitoring
                self.db_monitor = create_db_monitor(database.engine)

                logger.info("✅ Database initialized successfully")

                # Avvia schedulers (post scheduler, etc.)
                try:
                    await start_all_schedulers()
                    logger.info("✅ All schedulers started successfully")
                except Exception as sched_error:
                    logger.warning(f"⚠️ Scheduler startup failed: {sched_error}")

                return True
            logger.warning("⚠️ Database connection failed, running in degraded mode")
            return False

        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            # Don't crash the app, continue without DB (degraded mode)
            return False

    async def shutdown_procedures(self) -> None:
        """Perform cleanup procedures on application shutdown."""
        logger.info("🛑 Application shutting down...")

        # Stop all schedulers
        try:
            await stop_all_schedulers()
            logger.info("✅ All schedulers stopped")
        except Exception as e:
            logger.warning(f"⚠️ Scheduler shutdown error: {e}")

        # Dispose database engine
        if hasattr(database, "engine"):
            database.engine.dispose()
            logger.info("✅ Database engine disposed")

    def get_db_monitor(self):
        """Get the database monitor instance.

        Returns:
            Database monitor instance or None
        """
        return self.db_monitor

# Global startup manager instance
startup_manager = StartupManager()
