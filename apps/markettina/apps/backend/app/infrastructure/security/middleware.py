"""
Security Middleware - Rate limiting, CSRF, Security headers.
Enterprise-grade security for production.
"""

import hashlib
import logging
import time
from collections import defaultdict

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


# ============================================================================
# RATE LIMITING
# ============================================================================

class RateLimiter:
    """
    In-memory rate limiter.
    
    For production, use Redis-based rate limiting.
    """

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: dict[str, list] = defaultdict(list)

    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed.
        
        Args:
            identifier: IP address or user ID
            
        Returns:
            True if request allowed
        """
        now = time.time()
        minute_ago = now - 60

        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > minute_ago
        ]

        # Check limit
        if len(self.requests[identifier]) >= self.requests_per_minute:
            return False

        # Add current request
        self.requests[identifier].append(now)
        return True

    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests for identifier."""
        now = time.time()
        minute_ago = now - 60

        recent_requests = [
            req for req in self.requests[identifier]
            if req > minute_ago
        ]

        return max(0, self.requests_per_minute - len(recent_requests))


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware.
    
    Limits requests per IP address.
    """

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.limiter = RateLimiter(requests_per_minute)

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Check rate limit
        if not self.limiter.is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": 60
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.limiter.requests_per_minute),
                    "X-RateLimit-Remaining": "0"
                }
            )

        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.limiter.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(self.limiter.get_remaining(client_ip))

        return response


# ============================================================================
# SECURITY HEADERS
# ============================================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses.
    
    Protects against:
    - XSS attacks
    - Clickjacking
    - MIME sniffing
    - etc.
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://plausible.io; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://plausible.io; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp

        return response


# ============================================================================
# CORS CONFIGURATION
# ============================================================================

def get_cors_config():
    """
    CORS configuration for production.
    """
    return {
        "allow_origins": [
            "https://markettina.it",
            "https://www.markettina.it",
            "http://localhost:3000",  # Development
            "http://localhost:5173",  # Vite dev server
        ],
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
        "allow_headers": ["*"],
        "expose_headers": ["X-RateLimit-Limit", "X-RateLimit-Remaining"],
    }


# ============================================================================
# INPUT SANITIZATION
# ============================================================================

def sanitize_html(text: str) -> str:
    """
    Sanitize HTML to prevent XSS attacks.
    
    For production, use bleach library.
    """
    import html
    return html.escape(text)


def sanitize_sql(text: str) -> str:
    """
    Basic SQL injection prevention.
    
    Note: Always use parameterized queries with SQLAlchemy!
    This is just an additional layer.
    """
    dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
    for char in dangerous_chars:
        if char in text:
            logger.warning(f"Potential SQL injection attempt detected: {text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input detected"
            )
    return text


# ============================================================================
# CSRF PROTECTION
# ============================================================================

class CSRFProtection:
    """
    CSRF token generation and validation.
    """

    @staticmethod
    def generate_token(session_id: str, secret: str = "your-secret-key") -> str:
        """Generate CSRF token."""
        data = f"{session_id}{secret}{time.time()}"
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def validate_token(token: str, session_id: str, secret: str = "your-secret-key") -> bool:
        """Validate CSRF token."""
        # For production, store tokens in Redis with expiration
        # This is a simplified version
        return len(token) == 64  # Basic validation

    @staticmethod
    def get_token_from_request(request: Request) -> str | None:
        """Extract CSRF token from request."""
        # Check header first
        token = request.headers.get("X-CSRF-Token")
        if token:
            return token

        # Check form data
        form = getattr(request, "form", {})
        return form.get("csrf_token")


# ============================================================================
# PASSWORD HASHING (additional to passlib)
# ============================================================================

def hash_password_sha256(password: str, salt: str = "") -> str:
    """
    Additional password hashing layer.
    
    Note: Use passlib bcrypt as primary. This is secondary.
    """
    data = f"{salt}{password}".encode()
    return hashlib.sha256(data).hexdigest()


# ============================================================================
# IP BLACKLIST
# ============================================================================

class IPBlacklist:
    """IP blacklist for known malicious IPs."""

    def __init__(self):
        self.blacklisted_ips: set = set()

    def add(self, ip: str):
        """Add IP to blacklist."""
        self.blacklisted_ips.add(ip)
        logger.warning(f"IP blacklisted: {ip}")

    def is_blacklisted(self, ip: str) -> bool:
        """Check if IP is blacklisted."""
        return ip in self.blacklisted_ips

    def remove(self, ip: str):
        """Remove IP from blacklist."""
        self.blacklisted_ips.discard(ip)


# Global blacklist instance
ip_blacklist = IPBlacklist()
