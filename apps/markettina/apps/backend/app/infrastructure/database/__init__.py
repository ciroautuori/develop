"""Database Infrastructure
Gestisce connessioni, sessioni, transazioni.

LOW-001: Query performance logging and monitoring.
"""

from .query_logger import (
    get_query_performance_stats,
    log_query_performance,
    n1_detector,
    query_monitor,
    reset_query_performance_stats,
)
from .session import (
    AsyncSessionLocal,
    Base,
    SessionLocal,
    async_engine,
    engine,
    get_async_db,
    get_db,
)

__all__ = [
    "AsyncSessionLocal",
    "Base",
    "SessionLocal",
    "async_engine",
    "engine",
    "get_async_db",
    "get_db",
    "get_query_performance_stats",
    "log_query_performance",
    "n1_detector",
    "query_monitor",
    "reset_query_performance_stats",
]
