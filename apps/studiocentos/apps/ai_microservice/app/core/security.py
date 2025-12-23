"""
Security - API Key Authentication
"""

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# HTTP Bearer security scheme
security_scheme = HTTPBearer()


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security_scheme)
) -> str:
    """
    Verify API key from Authorization header

    Args:
        credentials: HTTP authorization credentials

    Returns:
        str: Valid API key

    Raises:
        HTTPException: If API key is invalid
    """
    api_key = credentials.credentials

    if api_key != settings.AI_SERVICE_API_KEY:
        logger.warning(
            "invalid_api_key_attempt",
            provided_key_prefix=api_key[:8] if api_key else "none"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return api_key
