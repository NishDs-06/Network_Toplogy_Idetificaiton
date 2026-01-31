# backend/app/api/v1/schemas/health.py
"""
Health and monitoring schemas.

Schemas for health checks and system metrics.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ServiceStatus(BaseModel):
    """Status of a single service."""
    
    data_ingestion: str = Field(
        default="healthy",
        description="Data ingestion service status",
    )
    similarity_engine: str = Field(
        default="healthy",
        description="Similarity engine status",
    )
    clustering_engine: str = Field(
        default="healthy",
        description="Clustering engine status",
    )
    ml_analytics: str = Field(
        default="healthy",
        description="ML analytics status",
    )
    llm_copilot: str = Field(
        default="healthy",
        description="LLM copilot status",
    )


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(
        ...,
        description="Overall status: healthy, degraded, unhealthy",
        examples=["healthy"],
    )
    timestamp: str = Field(
        ...,
        description="Check timestamp (ISO 8601)",
        examples=["2026-01-31T11:00:00Z"],
    )
    services: ServiceStatus = Field(
        ...,
        description="Status of individual services",
    )
    version: str = Field(
        ...,
        description="API version",
        examples=["1.0.0"],
    )


class MetricsResponse(BaseModel):
    """System metrics response."""
    
    requests_per_minute: int = Field(
        default=0,
        description="Requests per minute",
        examples=[45],
    )
    avg_response_time_ms: float = Field(
        default=0,
        description="Average response time in milliseconds",
        examples=[234],
    )
    active_jobs: int = Field(
        default=0,
        description="Number of active background jobs",
        examples=[3],
    )
    queue_length: int = Field(
        default=0,
        description="Job queue length",
        examples=[7],
    )
    storage_used_gb: float = Field(
        default=0,
        description="Storage used in GB",
        examples=[128.5],
    )
    uptime_hours: float = Field(
        default=0,
        description="System uptime in hours",
        examples=[720],
    )
    uploads_count: int = Field(default=0)
    similarities_count: int = Field(default=0)
    topologies_count: int = Field(default=0)
    anomalies_count: int = Field(default=0)
    propagations_count: int = Field(default=0)
    reports_count: int = Field(default=0)
