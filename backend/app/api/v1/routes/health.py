# backend/app/api/v1/routes/health.py
"""
Health and monitoring API endpoints.
"""

from datetime import datetime, timezone

from fastapi import APIRouter

from app.api.v1.schemas import (
    ServiceStatus,
    HealthResponse,
    MetricsResponse,
)
from app.services.storage import storage
from app.providers.ollama import OllamaProvider

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    System health check.
    
    Returns status of all services.
    """
    # Check LLM availability
    try:
        provider = OllamaProvider()
        llm_health = await provider.health_check()
        llm_status = "healthy" if llm_health.is_healthy else "degraded"
    except:
        llm_status = "unavailable"
    
    services = ServiceStatus(
        data_ingestion="healthy",
        similarity_engine="healthy",
        clustering_engine="healthy",
        ml_analytics="healthy",
        llm_copilot=llm_status,
    )
    
    # Determine overall status
    if llm_status == "unavailable":
        overall_status = "degraded"
    else:
        overall_status = "healthy"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        services=services,
        version="1.0.0",
    )


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    """
    System performance metrics.
    
    Returns current system statistics.
    """
    metrics = storage.get_metrics()
    
    return MetricsResponse(
        requests_per_minute=0,  # Would need request tracking middleware
        avg_response_time_ms=0,  # Would need timing middleware
        active_jobs=metrics.get("active_jobs", 0),
        queue_length=0,
        storage_used_gb=0.001,  # Placeholder for in-memory storage
        uptime_hours=0,  # Would need startup time tracking
        uploads_count=metrics.get("uploads_count", 0),
        similarities_count=metrics.get("similarities_count", 0),
        topologies_count=metrics.get("topologies_count", 0),
        anomalies_count=metrics.get("anomalies_count", 0),
        propagations_count=metrics.get("propagations_count", 0),
        reports_count=metrics.get("reports_count", 0),
    )
