"""Logging Middleware for FastAPI
Integrates structured logging with request/response cycle.
"""

import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.infrastructure.monitoring.logging import (
    clear_request_context,
    get_logger,
    set_request_context,
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request/response logging."""

    def __init__(self, app, service_name: str = "portfolio-backend"):
        super().__init__(app)
        self.service_name = service_name
        self.logger = get_logger("app.middleware")

        # Paths to exclude from logging (health checks, static files)
        self.exclude_paths = {"/health", "/metrics", "/static"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip logging for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Generate request ID and start timing
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # Extract client info
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "Unknown")

        # Set request context for structured logging
        set_request_context(request_id=request_id)

        # Log request start
        self.logger.info(
            "Request started",
            extra={
                "event_type": "request_start",
                "http_method": request.method,
                "http_path": request.url.path,
                "http_query": str(request.query_params) if request.query_params else None,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "content_type": request.headers.get("Content-Type"),
                "content_length": request.headers.get("Content-Length"),
            },
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate timing
            duration_ms = (time.time() - start_time) * 1000

            # Log successful request completion
            self.logger.info(
                "Request completed",
                extra={
                    "event_type": "request_complete",
                    "http_method": request.method,
                    "http_path": request.url.path,
                    "status_code": response.status_code,
                    "response_size": response.headers.get("Content-Length"),
                    "duration_ms": round(duration_ms, 2),
                },
            )

            # Log performance metrics if needed
            # Performance tracking can be added here if required

            # Add request ID to response headers for tracing
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as exc:
            # Calculate timing for failed requests
            duration_ms = (time.time() - start_time) * 1000

            # Log request error
            self.logger.error(
                "Request failed with exception",
                extra={
                    "event_type": "request_error",
                    "http_method": request.method,
                    "http_path": request.url.path,
                    "duration_ms": round(duration_ms, 2),
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc),
                },
                exc_info=True,
            )

            # Return structured error response
            error_response = JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "request_id": request_id,
                    "message": "An unexpected error occurred",
                },
            )
            error_response.headers["X-Request-ID"] = request_id

            return error_response

        finally:
            # Clear request context
            clear_request_context()

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address considering proxy headers."""
        # Check for forwarded IP headers (from load balancers, proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct client IP
        if hasattr(request.client, "host"):
            return request.client.host

        return "unknown"

class DatabaseLoggingMiddleware:
    """SQLAlchemy event listeners for database query logging."""

    def __init__(self):
        # Logger to track request metrics
        self.logger = get_logger("database.logging")

    def register_events(self, engine):
        """Register SQLAlchemy events for query logging."""
        from sqlalchemy import event

        @event.listens_for(engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            context._query_start_time = time.time()

        @event.listens_for(engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total_time = time.time() - context._query_start_time

            # Extract table name from SQL statement (basic parsing)
            table_name = self._extract_table_name(statement)
            query_type = statement.strip().split()[0].upper()

            # Log query performance
            self.logger.debug(
                f"Database query executed: {query_type} on {table_name}",
                extra={
                    "query_type": query_type,
                    "table_name": table_name,
                    "duration_ms": total_time * 1000,
                },
            )

    def _extract_table_name(self, statement: str) -> str:
        """Extract table name from SQL statement."""
        try:
            # Simple regex to extract table name (basic implementation)
            import re

            # Common patterns: SELECT FROM table, INSERT INTO table, UPDATE table, DELETE FROM table
            patterns = [
                r"FROM\s+(\w+)",
                r"UPDATE\s+(\w+)",
                r"INSERT\s+INTO\s+(\w+)",
                r"DELETE\s+FROM\s+(\w+)",
            ]

            for pattern in patterns:
                match = re.search(pattern, statement, re.IGNORECASE)
                if match:
                    return match.group(1)

            return "unknown"
        except:
            return "unknown"
