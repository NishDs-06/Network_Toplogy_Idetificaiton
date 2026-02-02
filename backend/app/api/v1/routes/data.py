# backend/app/api/v1/routes/data.py
"""
Data ingestion API endpoints.
"""

from fastapi import APIRouter, HTTPException

from app.api.v1.schemas import (
    DataUploadRequest,
    DataUploadResponse,
)
from app.services.data_service import data_service

router = APIRouter()


@router.post("/upload", response_model=DataUploadResponse)
async def upload_data(request: DataUploadRequest) -> DataUploadResponse:
    """
    Upload telemetry data for analysis.
    
    Accepts loss_events or throughput data in CSV format.
    Data can be provided inline or via file URL.
    """
    try:
        result = data_service.upload_data(
            data_type=request.data_type,
            data=request.data,
            file_url=request.file_url,
            metadata=request.metadata.model_dump() if request.metadata else None,
        )
        return DataUploadResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
