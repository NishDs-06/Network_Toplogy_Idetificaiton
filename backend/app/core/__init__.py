# backend/app/core/__init__.py
"""
Core utilities and infrastructure components.

This package contains:
- Exception handling
- Security utilities
- Structured logging
"""

from .exceptions import (
    APIException,
    AuthenticationError,
    RateLimitExceeded,
    ProviderError,
    ModelNotFoundError,
    ValidationError,
)
from .logging import get_logger, setup_logging

__all__ = [
    "APIException",
    "AuthenticationError",
    "RateLimitExceeded",
    "ProviderError",
    "ModelNotFoundError",
    "ValidationError",
    "get_logger",
    "setup_logging",
]
