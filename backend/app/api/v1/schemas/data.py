# backend/app/api/v1/schemas/data.py
"""
Data ingestion schemas.

Schemas for data upload requests and responses.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DataMetadata(BaseModel):
    """Metadata for uploaded data."""
    
    start_time: Optional[str] = Field(
        default=None,
        description="Start time of the data range (ISO 8601)",
        examples=["2026-01-31T00:00:00Z"],
    )
    end_time: Optional[str] = Field(
        default=None,
        description="End time of the data range (ISO 8601)",
        examples=["2026-01-31T23:59:59Z"],
    )
    cell_count: Optional[int] = Field(
        default=None,
        description="Number of cells in the data",
        examples=[24],
    )


class DataUploadRequest(BaseModel):
    """Request for uploading telemetry data."""
    
    data_type: str = Field(
        ...,
        description="Type of data: loss_events or throughput",
        examples=["loss_events"],
    )
    format: str = Field(
        default="csv",
        description="Data format",
        examples=["csv"],
    )
    file_url: Optional[str] = Field(
        default=None,
        description="URL to the data file (for remote files)",
        examples=["s3://bucket/loss_data.csv"],
    )
    data: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Inline data records (alternative to file_url)",
    )
    metadata: Optional[DataMetadata] = Field(
        default=None,
        description="Optional metadata about the data",
    )


class DataUploadResponse(BaseModel):
    """Response after data upload."""
    
    upload_id: str = Field(
        ...,
        description="Unique identifier for this upload",
        examples=["upl_abc123"],
    )
    status: str = Field(
        ...,
        description="Upload status: processing, completed, failed",
        examples=["processing"],
    )
    records_count: int = Field(
        ...,
        description="Number of records processed",
        examples=[150000],
    )
    estimated_processing_time_sec: Optional[int] = Field(
        default=None,
        description="Estimated processing time in seconds",
        examples=[45],
    )


class LossEventRecord(BaseModel):
    """Single loss event record."""
    
    slot_id: int = Field(
        ...,
        description="Time slot identifier",
        examples=[1],
    )
    cell_id: int = Field(
        ...,
        description="Cell identifier",
        examples=[1],
    )
    loss_event: int = Field(
        ...,
        description="Loss event flag: 0 = no loss, 1 = loss",
        examples=[0, 1],
    )


class ThroughputRecord(BaseModel):
    """Single throughput record."""
    
    slot_id: int = Field(
        ...,
        description="Time slot identifier",
        examples=[1],
    )
    cell_id: int = Field(
        ...,
        description="Cell identifier",
        examples=[1],
    )
    throughput_slot: float = Field(
        ...,
        description="Throughput value for this slot",
        examples=[30.656],
    )
