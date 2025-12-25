"""Database Query Performance Logger.

LOW-001: Query performance logging for optimization and N+1 detection.
"""

import time
import logging
from typing import Any, Callable, Optional
from functools import wraps
from sqlalchemy.orm import Session
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Configure logger
logger = logging.getLogger("query_performance")
logger.setLevel(logging.INFO)

# Console handler for development
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - [%(duration).2fms] %(message)s"
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class QueryPerformanceMonitor:
    """Monitor and log slow database queries."""

    def __init__(self, slow_query_threshold_ms: int = 100):
        """Initialize query performance monitor.

        Args:
            slow_query_threshold_ms: Threshold in milliseconds for slow queries
        """
        self.slow_query_threshold_ms = slow_query_threshold_ms
        self.query_count = 0
        self.total_duration = 0.0
        self.slow_queries = []

    def log_query(self, query: str, duration_ms: float, params: Optional[dict] = None):
        """Log query execution details.

        Args:
            query: SQL query string
            duration_ms: Query execution duration in milliseconds
            params: Query parameters (optional)
        """
        self.query_count += 1
        self.total_duration += duration_ms

        # Log slow queries
        if duration_ms > self.slow_query_threshold_ms:
            self.slow_queries.append(
                {
                    "query": query[:500],  # Truncate long queries
                    "duration_ms": duration_ms,
                    "params": params,
                }
            )

            logger.warning(
                f"SLOW QUERY ({duration_ms:.2f}ms): {query[:200]}",
                extra={"duration": duration_ms},
            )
        else:
            logger.debug(
                f"Query executed ({duration_ms:.2f}ms): {query[:100]}",
                extra={"duration": duration_ms},
            )

    def get_stats(self) -> dict:
        """Get performance statistics.

        Returns:
            Dict with query statistics
        """
        avg_duration = self.total_duration / self.query_count if self.query_count > 0 else 0

        return {
            "total_queries": self.query_count,
            "total_duration_ms": self.total_duration,
            "average_duration_ms": avg_duration,
            "slow_queries_count": len(self.slow_queries),
            "slow_queries": self.slow_queries[-10:],  # Last 10 slow queries
        }

    def reset_stats(self):
        """Reset performance statistics."""
        self.query_count = 0
        self.total_duration = 0.0
        self.slow_queries = []


# Global monitor instance
query_monitor = QueryPerformanceMonitor(slow_query_threshold_ms=100)


def log_query_performance(func: Callable) -> Callable:
    """Decorator to log query performance for repository methods.

    Usage:
        @log_query_performance
        def get_user_by_id(self, user_id: int):
            ...
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.perf_counter()

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log method call
            method_name = f"{func.__qualname__}"
            logger.info(
                f"Repository method: {method_name} completed in {duration_ms:.2f}ms",
                extra={"duration": duration_ms},
            )

    return wrapper


def setup_sqlalchemy_query_logging(engine: Engine):
    """Setup SQLAlchemy query logging events.

    Args:
        engine: SQLAlchemy engine instance
    """

    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Event listener for query execution start."""
        conn.info.setdefault("query_start_time", []).append(time.perf_counter())

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Event listener for query execution completion."""
        total_time = time.perf_counter() - conn.info["query_start_time"].pop(-1)
        duration_ms = total_time * 1000

        # Log to monitor
        query_monitor.log_query(statement, duration_ms, parameters)


class N1DetectionMiddleware:
    """Middleware to detect N+1 query problems.

    Tracks queries per request to identify potential N+1 issues.
    """

    def __init__(self, threshold: int = 20):
        """Initialize N+1 detection.

        Args:
            threshold: Number of queries that triggers N+1 warning
        """
        self.threshold = threshold
        self.request_query_counts = {}

    def track_request_start(self, request_id: str):
        """Start tracking queries for a request.

        Args:
            request_id: Unique request identifier
        """
        self.request_query_counts[request_id] = 0

    def increment_query_count(self, request_id: str):
        """Increment query count for a request.

        Args:
            request_id: Unique request identifier
        """
        if request_id in self.request_query_counts:
            self.request_query_counts[request_id] += 1

            if self.request_query_counts[request_id] >= self.threshold:
                logger.warning(
                    f"⚠️ Potential N+1 detected: {self.request_query_counts[request_id]} "
                    f"queries in request {request_id}"
                )

    def track_request_end(self, request_id: str) -> int:
        """End tracking for a request and return query count.

        Args:
            request_id: Unique request identifier

        Returns:
            Total number of queries executed
        """
        count = self.request_query_counts.pop(request_id, 0)

        if count > 0:
            logger.info(f"Request {request_id[:8]}... executed {count} queries")

        return count


# Global N+1 detector
n1_detector = N1DetectionMiddleware(threshold=20)


def get_query_performance_stats() -> dict:
    """Get current query performance statistics.

    Returns:
        Dict with performance statistics
    """
    return query_monitor.get_stats()


def reset_query_performance_stats():
    """Reset query performance statistics."""
    query_monitor.reset_stats()
