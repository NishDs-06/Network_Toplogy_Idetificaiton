# backend/app/middleware/rate_limit.py
"""
Rate limiting middleware.

This middleware enforces per-API-key rate limits using a sliding
window algorithm to prevent abuse and ensure fair usage.
"""

from typing import Callable, List, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import settings
from app.core.exceptions import RateLimitExceeded
from app.core.logging import get_logger
from app.core.security import rate_limiter

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting requests per API key.
    
    Uses the global rate limiter from app.core.security to track
    requests per API key. Rate limit headers are added to all
    responses to help clients manage their usage.
    
    Rate limit headers:
    - X-RateLimit-Limit: Maximum requests per window
    - X-RateLimit-Remaining: Requests remaining in window
    - X-RateLimit-Reset: Seconds until window resets
    - Retry-After: Seconds to wait (only on 429)
    
    Attributes:
        excluded_paths: Paths exempt from rate limiting
        enabled: Whether rate limiting is enabled
    """
    
    def __init__(
        self,
        app,
        excluded_paths: Optional[List[str]] = None,
        enabled: Optional[bool] = None,
    ) -> None:
        """
        Initialize the rate limiting middleware.
        
        Args:
            app: The ASGI application
            excluded_paths: Paths exempt from rate limiting
            enabled: Override settings to enable/disable rate limiting
        """
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/api/v1/health",
            "/api/v1/status",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        self.enabled = enabled if enabled is not None else settings.rate_limit_enabled
        
        logger.info(
            "Rate limit middleware initialized",
            enabled=self.enabled,
            limit=settings.rate_limit_requests,
            window_seconds=settings.rate_limit_window_seconds,
        )
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """
        Process the request through rate limiting.
        
        Args:
            request: The incoming request
            call_next: The next middleware/handler
        
        Returns:
            The response with rate limit headers
        """
        # Skip if rate limiting is disabled
        if not self.enabled:
            return await call_next(request)
        
        # Check if path is excluded
        path = request.url.path
        if self._is_excluded(path):
            return await call_next(request)
        
        # Get API key ID from request state (set by auth middleware)
        api_key_id = getattr(request.state, "api_key_id", "anonymous")
        
        try:
            # Check and enforce rate limit
            headers_info = rate_limiter.enforce_rate_limit(api_key_id)
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers to response
            response.headers["X-RateLimit-Limit"] = str(headers_info["X-RateLimit-Limit"])
            response.headers["X-RateLimit-Remaining"] = str(headers_info["X-RateLimit-Remaining"])
            response.headers["X-RateLimit-Reset"] = str(headers_info["X-RateLimit-Reset"])
            
            return response
            
        except RateLimitExceeded as e:
            logger.warning(
                "Rate limit exceeded",
                api_key_id=api_key_id,
                path=path,
                retry_after=e.retry_after,
            )
            
            response = JSONResponse(
                status_code=e.status_code,
                content=e.to_dict(),
            )
            
            # Add retry header
            if e.retry_after:
                response.headers["Retry-After"] = str(e.retry_after)
            
            return response
    
    def _is_excluded(self, path: str) -> bool:
        """Check if path is excluded from rate limiting."""
        for excluded in self.excluded_paths:
            if path.startswith(excluded):
                return True
        return False
