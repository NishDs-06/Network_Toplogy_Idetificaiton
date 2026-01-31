# backend/app/api/v1/schemas/topology.py
"""
Topology layer schemas.

Schemas for similarity computation and topology inference.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ComputeSimilarityRequest(BaseModel):
    """Request to compute similarity matrix."""
    
    upload_id: str = Field(
        ...,
        description="ID of the uploaded data to analyze",
        examples=["upl_abc123"],
    )
    method: str = Field(
        default="correlation",
        description="Similarity method: correlation, dtw, mutual_info",
        examples=["correlation"],
    )
    window_size: int = Field(
        default=100,
        description="Window size for analysis",
        examples=[100],
    )
    cell_ids: Optional[List[str]] = Field(
        default=None,
        description="Specific cell IDs to analyze (defaults to all)",
        examples=[["1", "2", "3"]],
    )


class ComputeSimilarityResponse(BaseModel):
    """Response from similarity computation."""
    
    job_id: str = Field(
        ...,
        description="Job ID for tracking",
        examples=["job_sim_001"],
    )
    status: str = Field(
        ...,
        description="Job status: processing, completed, failed",
        examples=["completed"],
    )
    similarity_matrix_id: str = Field(
        ...,
        description="ID of the computed similarity matrix",
        examples=["sim_001"],
    )
    computation_time_sec: Optional[float] = Field(
        default=None,
        description="Computation time in seconds",
        examples=[12.3],
    )
    result_url: str = Field(
        ...,
        description="URL to retrieve the result",
        examples=["/topology/similarity/sim_001"],
    )


class SimilarityMatrix(BaseModel):
    """Similarity matrix result."""
    
    similarity_id: str = Field(
        ...,
        description="Unique identifier for this matrix",
        examples=["sim_001"],
    )
    matrix: List[List[float]] = Field(
        ...,
        description="The similarity matrix (NxN)",
    )
    cell_ids: List[str] = Field(
        ...,
        description="Cell IDs corresponding to matrix indices",
        examples=[["1", "2", "3"]],
    )
    method: str = Field(
        ...,
        description="Method used for computation",
        examples=["correlation"],
    )
    computed_at: str = Field(
        ...,
        description="Computation timestamp (ISO 8601)",
        examples=["2026-01-31T10:30:00Z"],
    )
    download_url: Optional[str] = Field(
        default=None,
        description="URL to download the matrix",
    )


class InferTopologyRequest(BaseModel):
    """Request to infer topology from similarity matrix."""
    
    similarity_id: str = Field(
        ...,
        description="ID of the similarity matrix to use",
        examples=["sim_001"],
    )
    clustering_method: str = Field(
        default="hierarchical",
        description="Clustering method: hierarchical, kmeans, dbscan",
        examples=["hierarchical"],
    )
    num_clusters: Optional[int] = Field(
        default=None,
        description="Number of clusters (auto-detect if not provided)",
        examples=[3],
    )
    distance_threshold: float = Field(
        default=0.5,
        description="Distance threshold for clustering",
        examples=[0.5],
    )


class InferTopologyResponse(BaseModel):
    """Response from topology inference."""
    
    topology_id: str = Field(
        ...,
        description="Unique identifier for the topology result",
        examples=["topo_001"],
    )
    status: str = Field(
        ...,
        description="Inference status",
        examples=["completed"],
    )
    detected_groups: int = Field(
        ...,
        description="Number of detected groups/clusters",
        examples=[3],
    )
    result_url: str = Field(
        ...,
        description="URL to retrieve the full result",
        examples=["/topology/result/topo_001"],
    )


class LinkGroup(BaseModel):
    """A group of cells sharing a common link."""
    
    group_id: str = Field(
        ...,
        description="Unique group identifier",
        examples=["Group_1"],
    )
    group_name: str = Field(
        ...,
        description="Human-readable group name",
        examples=["Link_A"],
    )
    cells: List[str] = Field(
        ...,
        description="Cell IDs in this group",
        examples=[["1", "2", "8", "14"]],
    )
    avg_similarity: float = Field(
        ...,
        description="Average similarity within the group",
        examples=[0.85],
    )
    cell_count: int = Field(
        ...,
        description="Number of cells in the group",
        examples=[4],
    )


class CellAssignment(BaseModel):
    """Assignment of a cell to a group."""
    
    cell_id: str = Field(
        ...,
        description="Cell identifier",
        examples=["1"],
    )
    group_id: str = Field(
        ...,
        description="Assigned group identifier",
        examples=["Group_1"],
    )
    confidence: float = Field(
        ...,
        description="Confidence score for assignment",
        examples=[0.89],
    )


class TopologyResult(BaseModel):
    """Complete topology inference result."""
    
    topology_id: str = Field(
        ...,
        description="Unique identifier for this result",
        examples=["topo_001"],
    )
    created_at: str = Field(
        ...,
        description="Creation timestamp (ISO 8601)",
        examples=["2026-01-31T10:35:00Z"],
    )
    total_cells: int = Field(
        ...,
        description="Total number of cells analyzed",
        examples=[24],
    )
    detected_groups: int = Field(
        ...,
        description="Number of detected groups",
        examples=[3],
    )
    groups: List[LinkGroup] = Field(
        ...,
        description="List of detected link groups",
    )
    cell_assignments: List[CellAssignment] = Field(
        ...,
        description="Per-cell group assignments",
    )
    unassigned_cells: List[str] = Field(
        default_factory=list,
        description="Cells that couldn't be assigned to any group",
        examples=[["5"]],
    )
