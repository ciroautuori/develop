"""Structured Logging System
Addresses D4: Inconsistent Logging and Monitoring.
"""

import json
import logging
import os
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .log_scrubber import LogScrubber

# Context variables for request tracking
request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
user_id_ctx: ContextVar[int | None] = ContextVar("user_id", default=None)
tenant_id_ctx: ContextVar[str | None] = ContextVar("tenant_id", default=None)

class StructuredFormatter(logging.Formatter):
    """JSON structured logging formatter with request context."""

    def __init__(self, service_name: str = "portfolio-backend"):
        super().__init__()
        self.service_name = service_name
        self.hostname = os.getenv("HOSTNAME", "unknown")
        self.environment = os.getenv("ENVIRONMENT", "development")

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        # Base log structure
        log_entry = {
            # Timestamp and service info
            "timestamp": datetime.now(UTC).isoformat(),
            "service": self.service_name,
            "hostname": self.hostname,
            "environment": self.environment,
            # Log level and message (scrubbed for GDPR compliance)
            "level": record.levelname,
            "logger": record.name,
            "message": LogScrubber.scrub(record.getMessage()),
            # Code location
            "file": record.filename,
            "function": record.funcName,
            "line": record.lineno,
            # Request context (if available)
            "request_id": request_id_ctx.get(),
            "user_id": user_id_ctx.get(),
            "tenant_id": tenant_id_ctx.get(),
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        # Add extra fields from record
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "message",
                "getMessage",
            }:
                extra_fields[key] = value

        if extra_fields:
            # Scrub extra fields for PII
            log_entry["extra"] = LogScrubber.scrub_dict(extra_fields)

        # Remove None values to keep logs clean
        log_entry = {k: v for k, v in log_entry.items() if v is not None}

        return json.dumps(log_entry, default=str)

class SecurityLogger:
    """Specialized logger for security events."""

    def __init__(self):
        self.logger = logging.getLogger("security")

    def login_success(self, user_id: int, email: str, ip_address: str = None):
        """Log successful login."""
        self.logger.info(
            "User login successful",
            extra={
                "event_type": "auth_success",
                "auth_user_id": user_id,
                "auth_email": email,
                "client_ip": ip_address,
            },
        )

    def login_failure(self, email: str, reason: str, ip_address: str = None):
        """Log failed login attempt."""
        self.logger.warning(
            "User login failed",
            extra={
                "event_type": "auth_failure",
                "auth_email": email,
                "failure_reason": reason,
                "client_ip": ip_address,
            },
        )

    def permission_denied(self, user_id: int, resource: str, action: str):
        """Log permission denied events."""
        self.logger.warning(
            "Permission denied",
            extra={
                "event_type": "permission_denied",
                "auth_user_id": user_id,
                "resource": resource,
                "action": action,
            },
        )

    def data_access(self, user_id: int, resource_type: str, resource_id: str, action: str):
        """Log data access events."""
        self.logger.info(
            "Data access",
            extra={
                "event_type": "data_access",
                "auth_user_id": user_id,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "action": action,
            },
        )

    def rate_limit_exceeded(self, ip_address: str, endpoint: str):
        """Log rate limit violations."""
        self.logger.warning(
            "Rate limit exceeded",
            extra={
                "event_type": "rate_limit_exceeded",
                "client_ip": ip_address,
                "endpoint": endpoint,
            },
        )

class PerformanceLogger:
    """Specialized logger for performance monitoring."""

    def __init__(self):
        self.logger = logging.getLogger("performance")

    def request_timing(self, method: str, path: str, duration_ms: float, status_code: int):
        """Log request performance metrics."""
        self.logger.info(
            "Request completed",
            extra={
                "event_type": "request_timing",
                "http_method": method,
                "http_path": path,
                "duration_ms": round(duration_ms, 2),
                "status_code": status_code,
            },
        )

    def database_query(self, query_type: str, table_name: str, duration_ms: float):
        """Log database query performance."""
        self.logger.debug(
            "Database query executed",
            extra={
                "event_type": "db_query",
                "query_type": query_type,
                "table_name": table_name,
                "duration_ms": round(duration_ms, 2),
            },
        )

    def cache_operation(self, operation: str, cache_key: str, hit: bool = None):
        """Log cache operations."""
        extra_data = {
            "event_type": "cache_operation",
            "cache_operation": operation,
            "cache_key": cache_key,
        }
        if hit is not None:
            extra_data["cache_hit"] = hit

        self.logger.debug(f"Cache {operation}", extra=extra_data)

def setup_logging(
    level: str = "INFO", log_file: str | None = None, service_name: str = "portfolio-backend"
) -> dict[str, Any]:
    """Setup structured logging configuration.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        service_name: Service name for log entries

    Returns:
        Dictionary with logger instances
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create structured formatter
    formatter = StructuredFormatter(service_name)

    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)

    # Setup file handler if specified
    file_handler = None
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers.clear()  # Remove existing handlers
    root_logger.addHandler(console_handler)
    if file_handler:
        root_logger.addHandler(file_handler)

    # Configure specific loggers
    loggers = {
        "app": logging.getLogger("app"),
        "security": logging.getLogger("security"),
        "performance": logging.getLogger("performance"),
        "database": logging.getLogger("sqlalchemy.engine"),
    }

    # Set levels for specific loggers
    loggers["security"].setLevel(logging.INFO)  # Always log security events
    loggers["performance"].setLevel(logging.DEBUG if level == "DEBUG" else logging.INFO)
    loggers["database"].setLevel(logging.WARNING)  # Only log warnings/errors for DB

    # Silence noisy third-party loggers in production
    if os.getenv("ENVIRONMENT") == "production":
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("fastapi").setLevel(logging.WARNING)

    return {
        "app_logger": loggers["app"],
        "security_logger": SecurityLogger(),
        "performance_logger": PerformanceLogger(),
    }

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)

# Export context setters for middleware use
def set_request_context(request_id: str = None, user_id: int = None, tenant_id: str = None):
    """Set request context for structured logging."""
    if request_id:
        request_id_ctx.set(request_id)
    if user_id:
        user_id_ctx.set(user_id)
    if tenant_id:
        tenant_id_ctx.set(tenant_id)

def clear_request_context():
    """Clear request context."""
    request_id_ctx.set(None)
    user_id_ctx.set(None)
    tenant_id_ctx.set(None)
