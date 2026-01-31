# backend/app/api/v1/router.py
"""
API v1 main router.

This module aggregates all v1 endpoint routers into a single router
that can be mounted on the main application.
"""

from fastapi import APIRouter

from app.api.v1.routes import (
    data,
    topology,
    intelligence,
    copilot,
    visualizations,
    batch,
    health,
)

router = APIRouter()

# Data ingestion endpoints
router.include_router(
    data.router,
    prefix="/data",
    tags=["Data Ingestion"],
)

# Topology layer endpoints
router.include_router(
    topology.router,
    prefix="/topology",
    tags=["Topology"],
)

# Intelligence layer endpoints
router.include_router(
    intelligence.router,
    prefix="/intelligence",
    tags=["Intelligence"],
)

# LLM Copilot endpoints
router.include_router(
    copilot.router,
    prefix="/copilot",
    tags=["Copilot"],
)

# Visualization endpoints
router.include_router(
    visualizations.router,
    prefix="/visualizations",
    tags=["Visualizations"],
)

# Batch processing endpoints
router.include_router(
    batch.router,
    prefix="/batch",
    tags=["Batch Processing"],
)

# Health and metrics endpoints (no prefix, directly under /v1)
router.include_router(
    health.router,
    tags=["Monitoring"],
)
