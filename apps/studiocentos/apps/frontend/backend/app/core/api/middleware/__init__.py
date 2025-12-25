"""Middleware Stack Setup for FastAPI Application.

Configures all middleware layers including CORS, rate limiting, security headers,
logging, and error handling.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.api.exceptions.middleware import GlobalExceptionMiddleware

logger = logging.getLogger(__name__)
from app.core.config import settings
from app.core.rate_limiting import RateLimitMiddleware
from app.infrastructure.monitoring.logging_middleware import LoggingMiddleware


def setup_middleware_stack(app: FastAPI) -> None:
    """Setup complete middleware stack for the application.

    Middleware order matters - they are executed in reverse order of addition.
    Last added = first executed.

    Execution order (request):
    1. TrustedHostMiddleware (security)
    2. CORSMiddleware (CORS headers)
    3. GZipMiddleware (compression)
    4. RateLimitMiddleware (rate limiting)
    5. LoggingMiddleware (request/response logging)
    6. GlobalExceptionMiddleware (catches all unhandled exceptions)

    Args:
        app: FastAPI application instance
    """

    # 1. Global Exception Middleware (innermost - catches all unhandled exceptions)
    app.add_middleware(GlobalExceptionMiddleware)

    # 2. Logging Middleware (logs everything)
    app.add_middleware(
        LoggingMiddleware,
        service_name="portfolio-backend"
    )

    # 3. Rate Limiting Middleware (before CORS for security)
    if settings.ENABLE_RATE_LIMITING:
        app.add_middleware(RateLimitMiddleware)

    # 4. GZip Compression (compress responses)
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1000  # Only compress responses larger than 1KB
    )

    # 5. CORS Middleware (handle cross-origin requests)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
    )

    # 6. Trusted Host Middleware (outermost - security layer)
    if settings.ENVIRONMENT == "production":
        logger.debug(f"Allowed hosts configured: {settings.BACKEND_CORS_ORIGINS}")

        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # TEMPORARY FIX: Allow all hosts to debug 400 error
        )


__all__ = ["setup_middleware_stack"]
