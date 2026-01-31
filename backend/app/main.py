# backend/app/main.py
"""
Fronthaul Network Intelligence System - FastAPI Application.

This module provides the main FastAPI application with all middleware,
exception handlers, and router configuration.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.exceptions import APIException
from app.api.v1 import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events handler.
    
    Handles startup and shutdown operations.
    """
    # Startup
    print(f"🚀 Starting {settings.app_name} v1.0.0")
    print(f"📡 Environment: {settings.app_env}")
    print(f"🔗 API docs available at: http://{settings.host}:{settings.port}/docs")
    yield
    # Shutdown
    print(f"👋 Shutting down {settings.app_name}")


# Create FastAPI application
app = FastAPI(
    title="Fronthaul Network Intelligence API",
    description="""
## Network Topology Intelligence System

A three-layer intelligence architecture for fronthaul network analysis:

### Topology Layer (Backend)
- Data ingestion and processing
- Similarity matrix computation
- Hierarchical clustering and topology inference

### Intelligence Layer (ML)
- Anomaly detection
- Congestion propagation analysis
- Confidence scoring

### LLM Copilot Layer (Integration)
- Natural language insights
- Interactive Q&A
- Actionable recommendations
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_methods_list,
    allow_headers=settings.cors_headers_list,
)


# Exception Handlers
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle custom API exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": request.headers.get("X-Request-ID", ""),
            }
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(exc)} if settings.debug else {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
    )


# Include API v1 router
app.include_router(v1_router, prefix="/v1")


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """Root endpoint with API information."""
    return {
        "name": "Fronthaul Network Intelligence API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "api_version": "v1",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
    )
