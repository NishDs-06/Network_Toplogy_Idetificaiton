# backend/app/api/v1/schemas/batch.py
"""
Batch processing schemas.

Schemas for running complete analysis pipelines.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BatchConfig(BaseModel):
    """Configuration for batch analysis."""
    
    similarity_method: str = Field(
        default="correlation",
        description="Similarity computation method",
        examples=["correlation"],
    )
    clustering_method: str = Field(
        default="hierarchical",
        description="Clustering method",
        examples=["hierarchical"],
    )
    num_clusters: Optional[str] = Field(
        default="auto",
        description="Number of clusters or 'auto'",
        examples=["auto"],
    )
    anomaly_threshold: float = Field(
        default=0.5,
        description="Anomaly detection threshold",
        examples=[0.5],
    )
    propagation_analysis: bool = Field(
        default=True,
        description="Whether to run propagation analysis",
    )
    generate_report: bool = Field(
        default=True,
        description="Whether to generate LLM report",
    )
    generate_visualizations: bool = Field(
        default=True,
        description="Whether to generate visualizations",
    )


class BatchAnalysisRequest(BaseModel):
    """Request for full analysis pipeline."""
    
    upload_id: str = Field(
        ...,
        description="ID of the uploaded data",
        examples=["upl_001"],
    )
    config: Optional[BatchConfig] = Field(
        default=None,
        description="Pipeline configuration",
    )


class BatchStep(BaseModel):
    """Status of a single batch step."""
    
    step: str = Field(
        ...,
        description="Step name",
        examples=["similarity_computation"],
    )
    status: str = Field(
        ...,
        description="Status: pending, processing, completed, failed",
        examples=["completed"],
    )
    result_id: Optional[str] = Field(
        default=None,
        description="ID of the step result (if completed)",
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message (if failed)",
    )


class BatchResults(BaseModel):
    """Results from completed batch analysis."""
    
    topology_id: Optional[str] = Field(default=None)
    similarity_id: Optional[str] = Field(default=None)
    anomaly_id: Optional[str] = Field(default=None)
    propagation_id: Optional[str] = Field(default=None)
    report_id: Optional[str] = Field(default=None)
    visualizations: List[str] = Field(default_factory=list)


class BatchAnalysisResponse(BaseModel):
    """Response from batch analysis initiation."""
    
    batch_id: str = Field(
        ...,
        description="Unique batch job identifier",
        examples=["batch_001"],
    )
    status: str = Field(
        ...,
        description="Overall status",
        examples=["processing"],
    )
    estimated_completion_time: Optional[str] = Field(
        default=None,
        description="Estimated completion time (ISO 8601)",
        examples=["2026-01-31T11:15:00Z"],
    )
    steps: List[BatchStep] = Field(
        ...,
        description="Status of each pipeline step",
    )
    status_url: str = Field(
        ...,
        description="URL to check batch status",
        examples=["/batch/status/batch_001"],
    )


class BatchStatusResponse(BaseModel):
    """Response for batch status check."""
    
    batch_id: str = Field(
        ...,
        description="Batch job identifier",
        examples=["batch_001"],
    )
    status: str = Field(
        ...,
        description="Overall status: pending, processing, completed, failed",
        examples=["completed"],
    )
    started_at: str = Field(
        ...,
        description="Start timestamp (ISO 8601)",
        examples=["2026-01-31T10:30:00Z"],
    )
    completed_at: Optional[str] = Field(
        default=None,
        description="Completion timestamp (if completed)",
        examples=["2026-01-31T10:52:00Z"],
    )
    duration_sec: Optional[int] = Field(
        default=None,
        description="Total duration in seconds",
        examples=[1320],
    )
    steps: List[BatchStep] = Field(
        ...,
        description="Status of each pipeline step",
    )
    results: Optional[BatchResults] = Field(
        default=None,
        description="Results (if completed)",
    )
