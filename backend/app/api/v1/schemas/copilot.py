# backend/app/api/v1/schemas/copilot.py
"""
LLM Copilot layer schemas.

Schemas for insight generation and interactive queries.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class InsightContext(BaseModel):
    """Context for insight generation."""
    
    time_range: Optional[str] = Field(
        default=None,
        description="Time range for analysis",
        examples=["2026-01-31T00:00:00Z to 2026-01-31T23:59:59Z"],
    )
    network_region: Optional[str] = Field(
        default=None,
        description="Network region identifier",
        examples=["East_Region"],
    )


class GenerateInsightsRequest(BaseModel):
    """Request for generating LLM insights."""
    
    topology_id: str = Field(
        ...,
        description="ID of the topology result",
        examples=["topo_001"],
    )
    anomaly_id: Optional[str] = Field(
        default=None,
        description="ID of the anomaly analysis",
        examples=["anom_001"],
    )
    propagation_id: Optional[str] = Field(
        default=None,
        description="ID of the propagation analysis",
        examples=["prop_001"],
    )
    context: Optional[InsightContext] = Field(
        default=None,
        description="Additional context for insights",
    )


class GenerateInsightsResponse(BaseModel):
    """Response from insight generation."""
    
    report_id: str = Field(
        ...,
        description="Unique report identifier",
        examples=["rpt_001"],
    )
    status: str = Field(
        ...,
        description="Generation status",
        examples=["completed"],
    )
    generation_time_sec: float = Field(
        ...,
        description="Time taken to generate in seconds",
        examples=[3.2],
    )
    result_url: str = Field(
        ...,
        description="URL to retrieve the report",
        examples=["/copilot/report/rpt_001"],
    )


class NetworkInsight(BaseModel):
    """A single network insight."""
    
    insight_id: str = Field(
        ...,
        description="Unique insight identifier",
        examples=["ins_001"],
    )
    type: str = Field(
        ...,
        description="Insight type: congestion_alert, anomaly_detected, propagation_detected",
        examples=["congestion_alert"],
    )
    severity: str = Field(
        ...,
        description="Severity: low, medium, high",
        examples=["high"],
    )
    title: str = Field(
        ...,
        description="Human-readable title",
        examples=["Persistent Congestion Detected on Link_A"],
    )
    description: str = Field(
        ...,
        description="Detailed description",
        examples=["Link_A shows sustained congestion during peak hours"],
    )
    affected_entities: List[str] = Field(
        ...,
        description="List of affected entities",
        examples=[["Group_1"]],
    )
    timestamp: str = Field(
        ...,
        description="Insight timestamp (ISO 8601)",
        examples=["2026-01-31T10:45:00Z"],
    )


class ActionRecommendation(BaseModel):
    """A recommended action for addressing issues."""
    
    recommendation_id: str = Field(
        ...,
        description="Unique recommendation identifier",
        examples=["rec_001"],
    )
    insight_id: str = Field(
        ...,
        description="Related insight ID",
        examples=["ins_001"],
    )
    action_type: str = Field(
        ...,
        description="Action type: capacity_upgrade, traffic_shaping, hardware_check, reroute",
        examples=["capacity_upgrade"],
    )
    priority: str = Field(
        ...,
        description="Priority: low, medium, high",
        examples=["high"],
    )
    title: str = Field(
        ...,
        description="Action title",
        examples=["Increase Link_A Capacity"],
    )
    description: str = Field(
        ...,
        description="Detailed action description",
    )
    expected_impact: str = Field(
        ...,
        description="Expected impact of the action",
        examples=["Reduce packet loss by 45-60%"],
    )
    estimated_effort: str = Field(
        ...,
        description="Effort level: low, medium, high",
        examples=["medium"],
    )
    implementation_steps: List[str] = Field(
        default_factory=list,
        description="Step-by-step implementation guide",
    )


class TopologySummary(BaseModel):
    """Summary of topology analysis."""
    
    total_cells: int = Field(
        ...,
        description="Total cells analyzed",
        examples=[24],
    )
    detected_groups: int = Field(
        ...,
        description="Number of detected groups",
        examples=[3],
    )
    unassigned_cells: int = Field(
        default=0,
        description="Number of unassigned cells",
        examples=[1],
    )
    avg_group_confidence: Optional[float] = Field(
        default=None,
        description="Average confidence across groups",
        examples=[0.85],
    )


class ReportMetadata(BaseModel):
    """Metadata for the analysis report."""
    
    analysis_duration_sec: Optional[float] = Field(
        default=None,
        description="Total analysis duration in seconds",
        examples=[45],
    )
    data_points_analyzed: Optional[int] = Field(
        default=None,
        description="Number of data points analyzed",
        examples=[150000],
    )
    confidence_level: str = Field(
        default="medium",
        description="Overall confidence: low, medium, high",
        examples=["high"],
    )


class CopilotReport(BaseModel):
    """Complete copilot report."""
    
    report_id: str = Field(
        ...,
        description="Unique report identifier",
        examples=["rpt_001"],
    )
    generated_at: str = Field(
        ...,
        description="Generation timestamp (ISO 8601)",
        examples=["2026-01-31T10:50:00Z"],
    )
    summary: str = Field(
        ...,
        description="Executive summary of the analysis",
    )
    topology_summary: TopologySummary = Field(
        ...,
        description="Summary of topology analysis",
    )
    health_status: str = Field(
        ...,
        description="Overall health: healthy, degraded, critical",
        examples=["degraded"],
    )
    insights: List[NetworkInsight] = Field(
        ...,
        description="List of generated insights",
    )
    recommendations: List[ActionRecommendation] = Field(
        ...,
        description="List of action recommendations",
    )
    metadata: Optional[ReportMetadata] = Field(
        default=None,
        description="Report metadata",
    )


class QueryContext(BaseModel):
    """Context for interactive queries."""
    
    report_id: Optional[str] = Field(
        default=None,
        description="Report ID for context",
        examples=["rpt_001"],
    )
    topology_id: Optional[str] = Field(
        default=None,
        description="Topology ID for context",
        examples=["topo_001"],
    )


class QueryRequest(BaseModel):
    """Request for interactive query."""
    
    query: str = Field(
        ...,
        description="Natural language question",
        examples=["Which link is most congested?"],
    )
    context: Optional[QueryContext] = Field(
        default=None,
        description="Context for the query",
    )


class SupportingData(BaseModel):
    """Supporting data for query response."""
    
    group_id: Optional[str] = Field(default=None)
    congestion_level: Optional[float] = Field(default=None)
    affected_cells: Optional[List[str]] = Field(default=None)
    packet_loss_increase_pct: Optional[float] = Field(default=None)


class QueryResponse(BaseModel):
    """Response to interactive query."""
    
    query_id: str = Field(
        ...,
        description="Unique query identifier",
        examples=["qry_001"],
    )
    question: str = Field(
        ...,
        description="The original question",
    )
    answer: str = Field(
        ...,
        description="Natural language answer",
    )
    supporting_data: Optional[SupportingData] = Field(
        default=None,
        description="Supporting data for the answer",
    )
    related_insights: List[str] = Field(
        default_factory=list,
        description="Related insight IDs",
        examples=[["ins_001", "ins_003"]],
    )
