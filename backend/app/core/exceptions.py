# backend/app/core/exceptions.py
"""
Custom exception classes for the API backend.

This module defines a hierarchy of exceptions that map to specific
HTTP status codes and provide structured error responses.
"""

from typing import Any, Dict, Optional


class APIException(Exception):
    """
    Base exception for all API errors.
    
    All custom exceptions should inherit from this class to ensure
    consistent error handling and response formatting.
    
    Attributes:
        message: Human-readable error message
        status_code: HTTP status code for the response
        error_code: Machine-readable error code for client handling
        details: Additional error details (optional)
    """
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to a dictionary for JSON response."""
        response = {
            "status": "error",
            "error": {
                "code": self.error_code,
                "message": self.message,
            }
        }
        if self.details:
            response["error"]["details"] = self.details
        return response


class AuthenticationError(APIException):
    """
    Raised when API key authentication fails.
    
    HTTP Status: 401 Unauthorized
    """
    
    def __init__(
        self,
        message: str = "Invalid or missing API key",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details,
        )


class RateLimitExceeded(APIException):
    """
    Raised when rate limit is exceeded for an API key.
    
    HTTP Status: 429 Too Many Requests
    """
    
    def __init__(
        self,
        message: str = "Rate limit exceeded. Please try again later.",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        extra_details = details or {}
        if retry_after:
            extra_details["retry_after_seconds"] = retry_after
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details=extra_details,
        )
        self.retry_after = retry_after


class ProviderError(APIException):
    """
    Raised when LLM provider encounters an error.
    
    HTTP Status: 502 Bad Gateway (provider unavailable) or 500 (provider error)
    """
    
    def __init__(
        self,
        message: str = "LLM provider error",
        provider: str = "unknown",
        is_unavailable: bool = False,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        extra_details = {"provider": provider}
        if details:
            extra_details.update(details)
        super().__init__(
            message=message,
            status_code=502 if is_unavailable else 500,
            error_code="PROVIDER_UNAVAILABLE" if is_unavailable else "PROVIDER_ERROR",
            details=extra_details,
        )


class ModelNotFoundError(APIException):
    """
    Raised when requested model is not found or unavailable.
    
    HTTP Status: 404 Not Found
    """
    
    def __init__(
        self,
        model: str,
        provider: str = "unknown",
        available_models: Optional[list] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        extra_details = {
            "requested_model": model,
            "provider": provider,
        }
        if available_models:
            extra_details["available_models"] = available_models
        if details:
            extra_details.update(details)
        super().__init__(
            message=f"Model '{model}' not found",
            status_code=404,
            error_code="MODEL_NOT_FOUND",
            details=extra_details,
        )


class ValidationError(APIException):
    """
    Raised when request validation fails.
    
    HTTP Status: 422 Unprocessable Entity
    """
    
    def __init__(
        self,
        message: str = "Validation error",
        errors: Optional[list] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        extra_details = details or {}
        if errors:
            extra_details["validation_errors"] = errors
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=extra_details,
        )


class ServiceUnavailableError(APIException):
    """
    Raised when a required service is unavailable.
    
    HTTP Status: 503 Service Unavailable
    """
    
    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        service: str = "unknown",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        extra_details = {"service": service}
        if retry_after:
            extra_details["retry_after_seconds"] = retry_after
        if details:
            extra_details.update(details)
        super().__init__(
            message=message,
            status_code=503,
            error_code="SERVICE_UNAVAILABLE",
            details=extra_details,
        )
        self.retry_after = retry_after


class TimeoutError(APIException):
    """
    Raised when a request times out.
    
    HTTP Status: 504 Gateway Timeout
    """
    
    def __init__(
        self,
        message: str = "Request timed out",
        timeout_seconds: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        extra_details = details or {}
        if timeout_seconds:
            extra_details["timeout_seconds"] = timeout_seconds
        super().__init__(
            message=message,
            status_code=504,
            error_code="TIMEOUT_ERROR",
            details=extra_details,
        )
