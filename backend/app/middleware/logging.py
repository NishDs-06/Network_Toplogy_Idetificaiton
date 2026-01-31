# backend/app/middleware/logging.py
"""
Request/response logging middleware.

This middleware logs all incoming requests and outgoing responses
with timing information for monitoring and debugging.
"""

import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for structured request/response logging.
    
    For each request, this middleware:
    1. Generates a unique request ID
    2. Logs the incoming request details
    3. Measures processing time
    4. Logs the response with timing
    
    The request ID is added to the response headers and can be
    used for tracing and debugging across systems.
    
    Logged fields:
    - request_id: Unique identifier for the request
    - method: HTTP method
    - path: Request path
    - status_code: Response status code
    - latency_ms: Processing time in milliseconds
    - api_key_id: Hashed API key identifier
    """
    
    def __init__(self, app, enabled: bool = True) -> None:
        """
        Initialize the logging middleware.
        
        Args:
            app: The ASGI application
            enabled: Whether logging is enabled (default: True)
        """
        super().__init__(app)
        self.enabled = enabled and settings.log_requests
        
        logger.info(
            "Logging middleware initialized",
            enabled=self.enabled,
        )
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """
        Process the request with logging.
        
        Args:
            request: The incoming request
            call_next: The next middleware/handler
        
        Returns:
            The response with request ID header
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]
        
        # Attach to request state
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        
        # Log incoming request
        if self.enabled:
            logger.info(
                "Request received",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                query=str(request.query_params) if request.query_params else None,
                client_ip=self._get_client_ip(request),
            )
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log exception and re-raise
            latency_ms = (time.time() - start_time) * 1000
            logger.error(
                "Request failed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                latency_ms=round(latency_ms, 2),
                error=str(e),
                exc_info=True,
            )
            raise
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        # Log response
        if self.enabled:
            api_key_id = getattr(request.state, "api_key_id", "unknown")
            
            log_func = logger.info if response.status_code < 400 else logger.warning
            
            log_func(
                "Request completed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                latency_ms=round(latency_ms, 2),
                api_key_id=api_key_id,
            )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request.
        
        Checks X-Forwarded-For header for proxied requests.
        
        Args:
            request: The incoming request
        
        Returns:
            Client IP address
        """
        # Check for forwarded header (reverse proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # First IP in the list is the client
            return forwarded.split(",")[0].strip()
        
        # Fall back to direct client
        if request.client:
            return request.client.host
        
        return "unknown"
