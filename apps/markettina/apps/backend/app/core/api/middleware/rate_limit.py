"""Rate Limiting Middleware - Alias Module.

This module re-exports rate limiting functionality from app.core.rate_limiting
to maintain backward compatibility with existing imports.

Import paths supported:
- from app.core.api.middleware.rate_limit import rate_limit
- from app.core.rate_limiting import rate_limit
"""

from collections.abc import Callable
from functools import wraps
from typing import overload

from fastapi import HTTPException, Request, status

from app.core.rate_limiting import (
    RateLimitConfig,
    RateLimiter,
    RateLimitMiddleware,
    get_rate_limiter,
)


# Type overloads for better IDE support
@overload
def rate_limit(
    max_requests: int,
    window_seconds: int,
    per_user: bool = True,
    per_ip: bool = True,
) -> Callable: ...

@overload
def rate_limit(
    category: str,
    per_user: bool = True,
    per_ip: bool = True,
) -> Callable: ...


def rate_limit(
    max_requests: int | None = None,
    window_seconds: int | None = None,
    category: str | None = None,
    per_user: bool = True,
    per_ip: bool = True,
) -> Callable:
    """Rate limit decorator with dual signature support.
    
    Supports both legacy and new signature:
    
    Legacy usage (max_requests, window_seconds):
        @rate_limit(max_requests=5, window_seconds=900)
        async def login(...):
            pass
    
    New usage (category):
        @rate_limit(category="AUTH_LOGIN")
        async def login(...):
            pass
    
    Args:
        max_requests: Maximum requests allowed (legacy)
        window_seconds: Time window in seconds (legacy)
        category: Endpoint category from RateLimitConfig (new)
        per_user: Apply per-user limits
        per_ip: Apply per-IP limits
        
    Returns:
        Decorated function with rate limiting
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from kwargs
            request: Request | None = kwargs.get("request")
            current_user = kwargs.get("current_user")

            if not request:
                # No request context, skip rate limiting
                return await func(*args, **kwargs)

            # Get rate limiter instance
            limiter = await get_rate_limiter()

            # Determine rate limit parameters
            if max_requests is not None and window_seconds is not None:
                # Legacy signature: use custom limits
                limit_requests = max_requests
                limit_window = window_seconds
            elif category:
                # New signature: use category config
                config = getattr(RateLimitConfig, category, RateLimitConfig.DEFAULT)
                limit_requests = config["requests"]
                limit_window = config["window"]
            else:
                # Default config
                config = RateLimitConfig.DEFAULT
                limit_requests = config["requests"]
                limit_window = config["window"]

            # Check global IP limit
            if per_ip:
                client_ip = request.client.host if request.client else "unknown"

                # Use custom limits for IP check
                is_allowed, limit_info = await limiter.check_rate_limit(
                    f"ip:{client_ip}",
                    limit_requests,
                    limit_window
                )

                if not is_allowed:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail={"error": "Too many requests from this IP", **limit_info},
                        headers={
                            "X-RateLimit-Limit": str(limit_info.get("limit", 0)),
                            "X-RateLimit-Remaining": str(limit_info.get("remaining", 0)),
                            "X-RateLimit-Reset": str(limit_info.get("reset_in", 0)),
                            "Retry-After": str(limit_info.get("retry_after", 60)),
                        },
                    )

            # Check user-specific limit
            if per_user and current_user:
                user_id = current_user.id

                is_allowed, limit_info = await limiter.check_rate_limit(
                    f"user:{user_id}",
                    limit_requests,
                    limit_window
                )

                if not is_allowed:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail={"error": "Rate limit exceeded", **limit_info},
                        headers={
                            "X-RateLimit-Limit": str(limit_info.get("limit", 0)),
                            "X-RateLimit-Remaining": str(limit_info.get("remaining", 0)),
                            "X-RateLimit-Reset": str(limit_info.get("reset_in", 0)),
                            "Retry-After": str(limit_info.get("retry_after", 60)),
                        },
                    )

            # Execute route handler
            return await func(*args, **kwargs)

        return wrapper

    return decorator


__all__ = [
    "RateLimitConfig",
    "RateLimitMiddleware",
    "RateLimiter",
    "get_rate_limiter",
    "rate_limit",
]
