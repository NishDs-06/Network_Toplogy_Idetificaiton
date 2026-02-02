# backend/app/api/v1/schemas/intelligence.py
"""
Intelligence layer schemas.

Schemas for anomaly detection and propagation analysis.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DetectAnomaliesRequest(BaseModel):
    """Request for anomaly detection."""
    
    topology_id: str = Field(
        ...,
        description="ID of the topology result to analyze",
        examples=["topo_001"],
    )
    similarity_id: str = Field(
        ...,
        description="ID of the similarity matrix",
        examples=["sim_001"],
    )
    threshold: float = Field(
        default=0.5,
        description="Confidence score threshold (lower = anomaly)",
        examples=[0.5],
    )
    method: str = Field(
        default="isolation_forest",
        description="Detection method: isolation_forest, zscore, local_outlier_factor",
        examples=["isolation_forest"],
    )


class DetectAnomaliesResponse(BaseModel):
    """Response from anomaly detection."""
    
    analysis_id: str = Field(
        ...,
        description="Unique analysis identifier",
        examples=["anom_001"],
    )
    status: str = Field(
        ...,
        description="Analysis status",
        examples=["completed"],
    )
    anomalies_detected: int = Field(
        ...,
        description="Number of anomalies detected",
        examples=[2],
    )
    result_url: str = Field(
        ...,
        description="URL to retrieve full results",
        examples=["/intelligence/anomalies/anom_001"],
    )


class AnomalyScore(BaseModel):
    """Anomaly score for a single cell."""
    
    cell_id: str = Field(
        ...,
        description="Cell identifier",
        examples=["5"],
    )
    group_id: str = Field(
        ...,
        description="Assigned group identifier",
        examples=["Group_2"],
    )
    confidence_score: float = Field(
        ...,
        description="Confidence score (0-1, lower = more anomalous)",
        examples=[0.32],
    )
    is_anomaly: bool = Field(
        ...,
        description="Whether this cell is classified as anomalous",
        examples=[True],
    )
    anomaly_type: Optional[str] = Field(
        default=None,
        description="Type of anomaly: low_correlation, temporal_mismatch",
        examples=["low_correlation"],
    )
    severity: str = Field(
        default="medium",
        description="Severity: low, medium, high",
        examples=["high"],
    )
    deviation_percentage: Optional[float] = Field(
        default=None,
        description="Deviation from expected behavior",
        examples=[68.5],
    )
    explanation: Optional[str] = Field(
        default=None,
        description="Human-readable explanation",
        examples=["Cell shows significantly lower correlation with group peers"],
    )


class AnomalyStatistics(BaseModel):
    """Statistics for anomaly analysis."""
    
    avg_confidence: float = Field(
        ...,
        description="Average confidence score",
        examples=[0.76],
    )
    min_confidence: float = Field(
        ...,
        description="Minimum confidence score",
        examples=[0.32],
    )
    max_confidence: float = Field(
        ...,
        description="Maximum confidence score",
        examples=[0.95],
    )


class AnomalyResult(BaseModel):
    """Complete anomaly detection result."""
    
    analysis_id: str = Field(
        ...,
        description="Unique analysis identifier",
        examples=["anom_001"],
    )
    analyzed_at: str = Field(
        ...,
        description="Analysis timestamp (ISO 8601)",
        examples=["2026-01-31T10:40:00Z"],
    )
    topology_id: str = Field(
        ...,
        description="Source topology ID",
        examples=["topo_001"],
    )
    total_cells_analyzed: int = Field(
        ...,
        description="Total cells analyzed",
        examples=[24],
    )
    anomalies_detected: int = Field(
        ...,
        description="Number of anomalies detected",
        examples=[2],
    )
    anomalies: List[AnomalyScore] = Field(
        ...,
        description="List of detected anomalies",
    )
    normal_cells: List[AnomalyScore] = Field(
        default_factory=list,
        description="List of normal cells with their scores",
    )
    statistics: AnomalyStatistics = Field(
        ...,
        description="Statistical summary",
    )


class AnalyzePropagationRequest(BaseModel):
    """Request for propagation analysis."""
    
    topology_id: str = Field(
        ...,
        description="ID of the topology result",
        examples=["topo_001"],
    )
    upload_id: str = Field(
        ...,
        description="ID of the uploaded data",
        examples=["upl_001"],
    )
    time_window_sec: int = Field(
        default=60,
        description="Time window for analysis in seconds",
        examples=[60],
    )
    cross_correlation_lag: int = Field(
        default=50,
        description="Maximum lag for cross-correlation",
        examples=[50],
    )
    min_correlation: float = Field(
        default=0.6,
        description="Minimum correlation threshold",
        examples=[0.6],
    )


class AnalyzePropagationResponse(BaseModel):
    """Response from propagation analysis."""
    
    propagation_id: str = Field(
        ...,
        description="Unique propagation analysis ID",
        examples=["prop_001"],
    )
    status: str = Field(
        ...,
        description="Analysis status",
        examples=["completed"],
    )
    propagation_events_detected: int = Field(
        ...,
        description="Number of propagation events detected",
        examples=[3],
    )
    result_url: str = Field(
        ...,
        description="URL to retrieve full results",
        examples=["/intelligence/propagation/prop_001"],
    )


class PropagationEvent(BaseModel):
    """A single propagation event between groups."""
    
    event_id: str = Field(
        ...,
        description="Unique event identifier",
        examples=["evt_001"],
    )
    source_group: str = Field(
        ...,
        description="Source group ID",
        examples=["Group_1"],
    )
    target_group: str = Field(
        ...,
        description="Target group ID",
        examples=["Group_2"],
    )
    delay_ms: float = Field(
        ...,
        description="Propagation delay in milliseconds",
        examples=[8.5],
    )
    correlation: float = Field(
        ...,
        description="Correlation strength",
        examples=[0.73],
    )
    direction: str = Field(
        ...,
        description="Direction: upstream, downstream, bidirectional",
        examples=["downstream"],
    )
    confidence: float = Field(
        ...,
        description="Confidence in this detection",
        examples=[0.81],
    )
    timestamp: str = Field(
        ...,
        description="Event timestamp (ISO 8601)",
        examples=["2026-01-31T10:15:23Z"],
    )


class PropagationPath(BaseModel):
    """A propagation path through multiple groups."""
    
    path_id: str = Field(
        ...,
        description="Unique path identifier",
        examples=["path_001"],
    )
    sequence: List[str] = Field(
        ...,
        description="Ordered list of groups in the path",
        examples=[["Group_1", "Group_2", "Group_3"]],
    )
    total_delay_ms: float = Field(
        ...,
        description="Total delay across the path",
        examples=[15.3],
    )
    strength: float = Field(
        ...,
        description="Overall path strength",
        examples=[0.71],
    )
    type: str = Field(
        ...,
        description="Path type: cascading_congestion, feedback_loop",
        examples=["cascading_congestion"],
    )


class NetworkNode(BaseModel):
    """Node in the network graph."""
    
    id: str = Field(
        ...,
        description="Node identifier",
        examples=["Group_1"],
    )
    type: str = Field(
        ...,
        description="Node type: source, intermediate, target",
        examples=["source"],
    )
    congestion_level: float = Field(
        ...,
        description="Congestion level (0-1)",
        examples=[0.85],
    )


class NetworkEdge(BaseModel):
    """Edge in the network graph."""
    
    source: str = Field(
        ...,
        description="Source node ID",
        examples=["Group_1"],
    )
    target: str = Field(
        ...,
        description="Target node ID",
        examples=["Group_2"],
    )
    delay_ms: float = Field(
        ...,
        description="Propagation delay",
        examples=[8.5],
    )
    strength: float = Field(
        ...,
        description="Edge strength/correlation",
        examples=[0.73],
    )


class NetworkGraph(BaseModel):
    """Network propagation graph."""
    
    nodes: List[NetworkNode] = Field(
        ...,
        description="Graph nodes",
    )
    edges: List[NetworkEdge] = Field(
        ...,
        description="Graph edges",
    )


class PropagationResult(BaseModel):
    """Complete propagation analysis result."""
    
    propagation_id: str = Field(
        ...,
        description="Unique analysis identifier",
        examples=["prop_001"],
    )
    analyzed_at: str = Field(
        ...,
        description="Analysis timestamp (ISO 8601)",
        examples=["2026-01-31T10:45:00Z"],
    )
    topology_id: str = Field(
        ...,
        description="Source topology ID",
        examples=["topo_001"],
    )
    time_window_analyzed_sec: int = Field(
        ...,
        description="Time window analyzed in seconds",
        examples=[3600],
    )
    events: List[PropagationEvent] = Field(
        ...,
        description="Detected propagation events",
    )
    propagation_paths: List[PropagationPath] = Field(
        ...,
        description="Identified propagation paths",
    )
    network_graph: NetworkGraph = Field(
        ...,
        description="Network graph representation",
    )
