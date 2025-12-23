import redis.asyncio as redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException, status
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Redis connection for rate limiting
redis_client = None

async def get_redis_client():
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.from_url(
                getattr(settings, 'redis_url', 'redis://localhost:6379'),
                encoding="utf-8",
                decode_responses=True,
                health_check_interval=30,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={}
            )
            await redis_client.ping()
            logger.info("Redis connection established for rate limiting")
        except Exception as e:
            logger.warning(f"Redis not available, falling back to memory: {e}")
            redis_client = None
    return redis_client

# Rate limiter configuration
def get_rate_limiter_key(request: Request):
    """Custom key function for rate limiting"""
    client_ip = get_remote_address(request)
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Extract username from JWT if present
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            from app.core.security import verify_token
            token = auth_header.split(" ")[1]
            payload = verify_token(token)
            if payload and payload.get("sub"):
                return f"user:{payload['sub']}:{client_ip}"
        except Exception:
            pass
    
    return f"ip:{client_ip}:{hash(user_agent) % 10000}"

# Initialize limiter
limiter = Limiter(
    key_func=get_rate_limiter_key,
    default_limits=["1000/hour"],
    storage_uri=getattr(settings, 'redis_url', 'memory://'),
    strategy="moving-window"
)

# Custom rate limit exceeded handler
async def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    logger.warning(
        f"Rate limit exceeded for {get_remote_address(request)} "
        f"on {request.url.path} - {exc.detail}"
    )
    
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": "Rate limit exceeded",
            "message": "Troppi tentativi. Riprova più tardi.",
            "retry_after": exc.retry_after
        },
        headers={"Retry-After": str(exc.retry_after)} if exc.retry_after else {}
    )

# Security middleware for suspicious activity detection
class SecurityMiddleware:
    def __init__(self):
        self.suspicious_patterns = [
            "admin", "wp-admin", "phpmyadmin", ".env", "config",
            "backup", "sql", "dump", "password", "passwd"
        ]
        
    async def detect_suspicious_activity(self, request: Request):
        """Detect potentially malicious requests"""
        path = request.url.path.lower()
        query = str(request.url.query).lower()
        
        # Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            if pattern in path or pattern in query:
                logger.warning(
                    f"Suspicious activity detected from {get_remote_address(request)}: "
                    f"{request.method} {request.url}"
                )
                
                # Increase rate limit penalty for suspicious IPs
                client_ip = get_remote_address(request)
                redis_client = await get_redis_client()
                if redis_client:
                    try:
                        suspicious_key = f"suspicious:{client_ip}"
                        await redis_client.incr(suspicious_key)
                        await redis_client.expire(suspicious_key, 3600)  # 1 hour
                        
                        suspicious_count = await redis_client.get(suspicious_key)
                        if suspicious_count and int(suspicious_count) > 5:
                            raise HTTPException(
                                status_code=status.HTTP_403_FORBIDDEN,
                                detail="Access denied due to suspicious activity"
                            )
                    except Exception as e:
                        logger.error(f"Redis error in security middleware: {e}")
                
                break

security_middleware = SecurityMiddleware()
