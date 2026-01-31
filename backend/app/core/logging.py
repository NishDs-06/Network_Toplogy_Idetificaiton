# backend/app/core/logging.py
"""
Structured logging configuration using structlog.

This module provides JSON-formatted structured logging suitable for
production environments with log aggregation and analysis.
"""

import logging
import sys
from typing import Any, Dict, Optional

import structlog
from structlog.types import Processor

from app.config import settings


def add_app_context(
    logger: logging.Logger,
    method_name: str,
    event_dict: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Add application context to all log entries.
    
    This processor adds common fields like app_name and environment
    to every log message for easier filtering and correlation.
    """
    event_dict["app"] = settings.app_name
    event_dict["env"] = settings.app_env
    return event_dict


def setup_logging() -> None:
    """
    Configure structured logging for the application.
    
    This function should be called once at application startup.
    It configures both structlog and the standard logging module.
    """
    # Determine log level from settings
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Configure processors based on environment
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        add_app_context,
    ]
    
    if settings.log_format == "json":
        # Production: JSON format for log aggregation
        processors: list[Processor] = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Development: Console-friendly format
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging to route through structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Optional logger name. If not provided, uses the module name.
    
    Returns:
        A structlog BoundLogger instance for structured logging.
    
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing request", request_id="abc123", user="test")
    """
    return structlog.get_logger(name)


class LoggerMixin:
    """
    Mixin class that provides a logger attribute.
    
    Classes that inherit from this mixin will have a `logger` property
    that returns a structlog logger named after the class.
    
    Example:
        >>> class MyService(LoggerMixin):
        ...     def do_something(self):
        ...         self.logger.info("Doing something")
    """
    
    @property
    def logger(self) -> structlog.BoundLogger:
        """Get a logger for this class."""
        return get_logger(self.__class__.__name__)


def log_request_context(
    request_id: str,
    method: str,
    path: str,
    client_ip: Optional[str] = None,
    api_key_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a context dictionary for request logging.
    
    This helper creates a standardized context dictionary for
    logging request-related information.
    
    Args:
        request_id: Unique request identifier
        method: HTTP method
        path: Request path
        client_ip: Client IP address (optional)
        api_key_id: Hashed/masked API key identifier (optional)
    
    Returns:
        Dictionary of context values for logging
    """
    context = {
        "request_id": request_id,
        "http_method": method,
        "http_path": path,
    }
    if client_ip:
        context["client_ip"] = client_ip
    if api_key_id:
        context["api_key_id"] = api_key_id
    return context
