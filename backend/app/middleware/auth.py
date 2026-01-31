# backend/app/middleware/auth.py
"""
API Key authentication middleware.

This middleware validates API keys from request headers and
attaches authentication context to the request state.
"""

from typing import Callable, List, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import settings
from app.core.exceptions import AuthenticationError
from app.core.logging import get_logger
from app.core.security import hash_api_key, validate_api_key

logger = get_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API key authentication.
    
    This middleware:
    1. Extracts the API key from the configured header
    2. Validates the key against configured valid keys
    3. Attaches the key hash to request state for logging/rate limiting
    4. Allows configurable path exclusions (e.g., health endpoints)
    
    Excluded paths do not require authentication because they are
    used for health checks and monitoring.
    
    Attributes:
        excluded_paths: List of path prefixes that skip auth
        header_name: Name of the header containing the API key
    """
    
    def __init__(
        self,
        app,
        excluded_paths: Optional[List[str]] = None,
        header_name: Optional[str] = None,
    ) -> None:
        """
        Initialize the authentication middleware.
        
        Args:
            app: The ASGI application
            excluded_paths: Paths that don't require auth (default: health endpoints)
            header_name: Header name for API key (default: from settings)
        """
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/api/v1/health",
            "/api/v1/status",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        self.header_name = header_name or settings.api_key_header
        
        logger.info(
            "Auth middleware initialized",
            excluded_paths=self.excluded_paths,
            header_name=self.header_name,
        )
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """
        Process the request through authentication.
        
        Args:
            request: The incoming request
            call_next: The next middleware/handler in the chain
        
        Returns:
            The response from the handler or an error response
        """
        # Check if path is excluded from auth
        path = request.url.path
        if self._is_excluded(path):
            # Set a default key identifier for logging
            request.state.api_key_id = "no-auth-required"
            return await call_next(request)
        
        # Extract API key from header
        api_key = request.headers.get(self.header_name)
        
        try:
            # Validate the API key
            key_id = validate_api_key(api_key)
            
            # Attach key ID to request state for downstream use
            request.state.api_key_id = key_id
            
            logger.debug(
                "Request authenticated",
                key_id=key_id,
                path=path,
            )
            
            return await call_next(request)
            
        except AuthenticationError as e:
            logger.warning(
                "Authentication failed",
                path=path,
                error=str(e),
            )
            return JSONResponse(
                status_code=e.status_code,
                content=e.to_dict(),
            )
    
    def _is_excluded(self, path: str) -> bool:
        """
        Check if a path is excluded from authentication.
        
        Args:
            path: The request path
        
        Returns:
            True if the path is excluded, False otherwise
        """
        for excluded in self.excluded_paths:
            if path.startswith(excluded):
                return True
        return False
