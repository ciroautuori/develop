"""
Sentry Integration - Error tracking and performance monitoring.
Enterprise-grade monitoring for production.
"""

import logging
import os

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

logger = logging.getLogger(__name__)


def init_sentry(
    dsn: str = None,
    environment: str = "production",
    traces_sample_rate: float = 0.1,
    profiles_sample_rate: float = 0.1,
):
    """
    Initialize Sentry SDK for error tracking and performance monitoring.
    
    Args:
        dsn: Sentry DSN (from environment)
        environment: Environment name (production, staging, development)
        traces_sample_rate: Percentage of transactions to trace (0.0 to 1.0)
        profiles_sample_rate: Percentage of transactions to profile (0.0 to 1.0)
    """
    dsn = dsn or os.getenv("SENTRY_DSN")

    if not dsn:
        logger.warning("SENTRY_DSN not configured, skipping Sentry initialization")
        return

    try:
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,

            # Integrations
            integrations=[
                FastApiIntegration(
                    transaction_style="endpoint",
                ),
                SqlalchemyIntegration(),
                RedisIntegration(),
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR
                ),
            ],

            # Performance Monitoring
            traces_sample_rate=traces_sample_rate,
            profiles_sample_rate=profiles_sample_rate,

            # Error Sampling
            sample_rate=1.0,  # Capture 100% of errors

            # Release tracking
            release=os.getenv("RELEASE_VERSION", "1.0.0"),

            # Additional options
            attach_stacktrace=True,
            send_default_pii=False,  # GDPR compliance
            max_breadcrumbs=50,

            # Request data
            request_bodies="medium",

            # Before send hook (filter sensitive data)
            before_send=before_send_filter,
        )

        logger.info(f"Sentry initialized successfully for {environment}")

    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")


def before_send_filter(event, hint):
    """
    Filter sensitive data before sending to Sentry.
    
    Remove passwords, tokens, API keys from error reports.
    """
    # Filter sensitive keys
    sensitive_keys = [
        "password",
        "token",
        "secret",
        "api_key",
        "authorization",
        "cookie",
        "session",
    ]

    # Filter request data
    if "request" in event:
        # Headers
        if "headers" in event["request"]:
            for key in list(event["request"]["headers"].keys()):
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    event["request"]["headers"][key] = "[FILTERED]"

        # Cookies
        if "cookies" in event["request"]:
            event["request"]["cookies"] = "[FILTERED]"

        # POST data
        if "data" in event["request"]:
            if isinstance(event["request"]["data"], dict):
                for key in list(event["request"]["data"].keys()):
                    if any(sensitive in key.lower() for sensitive in sensitive_keys):
                        event["request"]["data"][key] = "[FILTERED]"

    # Filter extra data
    if "extra" in event:
        for key in list(event["extra"].keys()):
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                event["extra"][key] = "[FILTERED]"

    return event


def capture_exception(exception: Exception, context: dict = None):
    """
    Manually capture exception with context.
    
    Usage:
        try:
            risky_operation()
        except Exception as e:
            capture_exception(e, {"user_id": user.id})
    """
    if context:
        sentry_sdk.set_context("additional", context)

    sentry_sdk.capture_exception(exception)


def capture_message(message: str, level: str = "info", context: dict = None):
    """
    Capture custom message.
    
    Args:
        message: Message text
        level: Severity level (debug, info, warning, error, fatal)
        context: Additional context
    """
    if context:
        sentry_sdk.set_context("additional", context)

    sentry_sdk.capture_message(message, level=level)


def set_user(user_id: int, email: str = None, username: str = None):
    """
    Associate errors with a specific user.
    
    Args:
        user_id: User ID
        email: User email (optional)
        username: Username (optional)
    """
    sentry_sdk.set_user({
        "id": user_id,
        "email": email,
        "username": username,
    })


def add_breadcrumb(
    message: str,
    category: str = "default",
    level: str = "info",
    data: dict = None
):
    """
    Add breadcrumb for debugging context.
    
    Args:
        message: Breadcrumb message
        category: Category (navigation, http, db, etc.)
        level: Severity level
        data: Additional data
    """
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    )


def start_transaction(name: str, op: str = "http.server"):
    """
    Start a performance transaction.
    
    Usage:
        with start_transaction("user.login", "auth"):
            perform_login()
    """
    return sentry_sdk.start_transaction(name=name, op=op)


def set_tag(key: str, value: str):
    """Set a tag for error grouping and filtering."""
    sentry_sdk.set_tag(key, value)


def set_context(name: str, context: dict):
    """Set custom context for errors."""
    sentry_sdk.set_context(name, context)


# Performance monitoring decorators

def monitor_performance(operation_name: str):
    """
    Decorator to monitor function performance.
    
    Usage:
        @monitor_performance("database.query")
        def expensive_query():
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with sentry_sdk.start_span(op=operation_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator
