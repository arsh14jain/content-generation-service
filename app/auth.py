from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from typing import Optional
import logging

from config import config

logger = logging.getLogger(__name__)

# Define API key security scheme for OpenAPI documentation
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Depends(api_key_header)) -> None:
    """
    Verify API key from X-API-Key header.
    Raises HTTPException if key is missing or invalid.
    """
    if not api_key:
        logger.warning("Missing API key in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if api_key != config.API_KEY:
        logger.warning(f"Invalid API key: {api_key[:8] if len(api_key) >= 8 else 'short_key'}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Log successful authentication for monitoring
    logger.debug("Valid API key provided")

def get_api_key_dependency():
    """
    Dependency function to verify API key.
    Use this in route handlers that require authentication.
    """
    return Depends(verify_api_key)

# Alternative: Check if API key is properly configured
def is_api_key_configured() -> bool:
    """Check if API key is properly configured (not default value)"""
    return config.API_KEY != "your_secure_api_key_here" and len(config.API_KEY) >= 16