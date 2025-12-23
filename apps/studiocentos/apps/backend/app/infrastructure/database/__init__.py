"""Database Infrastructure
Gestisce connessioni, sessioni, transazioni.

LOW-001: Query performance logging and monitoring.
"""

from .session import Base, SessionLocal, engine, get_db
from .query_logger import (
    get_query_performance_stats,
    reset_query_performance_stats,
    log_query_performance,
    query_monitor,
    n1_detector,
)

__all__ = [
    "engine",
    "SessionLocal",
    "get_db",
    "Base",
    "get_query_performance_stats",
    "reset_query_performance_stats",
    "log_query_performance",
    "query_monitor",
    "n1_detector",
]
