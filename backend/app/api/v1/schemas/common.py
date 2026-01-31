# backend/app/api/v1/schemas/common.py
"""
Common schemas used across all API endpoints.

These schemas provide consistent response structures and error formats.
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field


# Generic type for response data
T = TypeVar("T")


class ErrorDetail(BaseModel):
    """
    Detailed error information.
    
    Attributes:
        code: Machine-readable error code
        message: Human-readable error message
        details: Additional error context
    """
    
    code: str = Field(
        ...,
        description="Machine-readable error code",
        examples=["VALIDATION_ERROR", "AUTHENTICATION_ERROR"],
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
        examples=["Invalid API key provided"],
    )
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error context",
    )


class ErrorResponse(BaseModel):
    """
    Standard error response format.
    
    All API errors return this structured response.
    """
    
    status: str = Field(
        default="error",
        description="Response status",
    )
    error: ErrorDetail = Field(
        ...,
        description="Error details",
    )


class MetadataResponse(BaseModel):
    """
    Response metadata for tracking and analytics.
    
    Included in successful responses to provide context
    about the operation.
    """
    
    model_used: Optional[str] = Field(
        default=None,
        description="LLM model used for the response",
        examples=["llama3.2", "mistral"],
    )
    provider: Optional[str] = Field(
        default=None,
        description="Provider name",
        examples=["ollama"],
    )
    tokens_used: Optional[int] = Field(
        default=None,
        description="Total tokens consumed",
        ge=0,
    )
    prompt_tokens: Optional[int] = Field(
        default=None,
        description="Tokens in the prompt",
        ge=0,
    )
    completion_tokens: Optional[int] = Field(
        default=None,
        description="Tokens in the completion",
        ge=0,
    )
    latency_ms: Optional[float] = Field(
        default=None,
        description="Processing latency in milliseconds",
        ge=0,
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp (UTC)",
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Unique request identifier for tracing",
    )


class APIResponse(BaseModel, Generic[T]):
    """
    Standard successful response wrapper.
    
    All successful API responses use this format with typed data.
    
    Example:
        {
            "status": "success",
            "data": { ... },
            "metadata": { ... }
        }
    """
    
    status: str = Field(
        default="success",
        description="Response status",
    )
    data: T = Field(
        ...,
        description="Response data payload",
    )
    metadata: Optional[MetadataResponse] = Field(
        default=None,
        description="Response metadata",
    )


class PaginationParams(BaseModel):
    """
    Pagination parameters for list endpoints.
    """
    
    page: int = Field(
        default=1,
        ge=1,
        description="Page number (1-indexed)",
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Items per page",
    )
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated list response.
    """
    
    items: List[T] = Field(
        ...,
        description="List of items",
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of items",
    )
    page: int = Field(
        ...,
        ge=1,
        description="Current page number",
    )
    page_size: int = Field(
        ...,
        ge=1,
        description="Items per page",
    )
    pages: int = Field(
        ...,
        ge=0,
        description="Total number of pages",
    )
