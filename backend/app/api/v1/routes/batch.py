# backend/app/api/v1/routes/batch.py
"""
Batch processing API endpoints.
"""

from fastapi import APIRouter, HTTPException

from app.api.v1.schemas import (
    BatchAnalysisRequest,
    BatchAnalysisResponse,
    BatchStatusResponse,
)
from app.services.batch_service import batch_service

router = APIRouter()


@router.post("/full-analysis", response_model=BatchAnalysisResponse)
async def full_analysis(request: BatchAnalysisRequest) -> BatchAnalysisResponse:
    """
    Run complete analysis pipeline.
    
    Executes all analysis steps:
    1. Data validation
    2. Similarity computation
    3. Topology inference
    4. Anomaly detection
    5. Propagation analysis
    6. Insight generation
    7. Visualization generation
    
    Returns immediately with a batch ID for status tracking.
    """
    try:
        result = await batch_service.run_full_analysis(
            upload_id=request.upload_id,
            config=request.config.model_dump() if request.config else None,
        )
        return BatchAnalysisResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@router.get("/status/{batch_id}", response_model=BatchStatusResponse)
async def get_batch_status(batch_id: str) -> BatchStatusResponse:
    """
    Check status of a batch analysis job.
    
    Returns current step statuses and results when complete.
    """
    result = batch_service.get_batch_status(batch_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Batch job not found: {batch_id}")
    return BatchStatusResponse(**result)
