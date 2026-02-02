# backend/app/api/v1/routes/intelligence.py
"""
Intelligence layer API endpoints.
"""

from fastapi import APIRouter, HTTPException

from app.api.v1.schemas import (
    DetectAnomaliesRequest,
    DetectAnomaliesResponse,
    AnomalyResult,
    AnalyzePropagationRequest,
    AnalyzePropagationResponse,
    PropagationResult,
)
from app.services.anomaly_service import anomaly_service
from app.services.propagation_service import propagation_service

router = APIRouter()


@router.post("/detect-anomalies", response_model=DetectAnomaliesResponse)
async def detect_anomalies(request: DetectAnomaliesRequest) -> DetectAnomaliesResponse:
    """
    Detect anomalous cells based on group membership.
    
    Cells with low correlation to their assigned group are flagged.
    """
    try:
        result = anomaly_service.detect_anomalies(
            topology_id=request.topology_id,
            similarity_id=request.similarity_id,
            threshold=request.threshold,
            method=request.method,
        )
        return DetectAnomaliesResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")


@router.get("/anomalies/{analysis_id}", response_model=AnomalyResult)
async def get_anomalies(analysis_id: str) -> AnomalyResult:
    """
    Retrieve anomaly detection results.
    """
    result = anomaly_service.get_anomaly(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Anomaly analysis not found: {analysis_id}")
    return AnomalyResult(**result)


@router.post("/analyze-propagation", response_model=AnalyzePropagationResponse)
async def analyze_propagation(request: AnalyzePropagationRequest) -> AnalyzePropagationResponse:
    """
    Analyze congestion propagation patterns.
    
    Uses cross-correlation to detect temporal relationships between groups.
    """
    try:
        result = propagation_service.analyze_propagation(
            topology_id=request.topology_id,
            upload_id=request.upload_id,
            time_window_sec=request.time_window_sec,
            cross_correlation_lag=request.cross_correlation_lag,
            min_correlation=request.min_correlation,
        )
        return AnalyzePropagationResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Propagation analysis failed: {str(e)}")


@router.get("/propagation/{propagation_id}", response_model=PropagationResult)
async def get_propagation(propagation_id: str) -> PropagationResult:
    """
    Retrieve propagation analysis results.
    """
    result = propagation_service.get_propagation(propagation_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Propagation analysis not found: {propagation_id}")
    return PropagationResult(**result)
