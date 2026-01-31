# backend/app/api/v1/schemas/visualization.py
"""
Visualization schemas.

Schemas for generating various visualization types.
"""

from typing import Optional

from pydantic import BaseModel, Field


class HeatmapRequest(BaseModel):
    """Request for generating a similarity heatmap."""
    
    similarity_id: str = Field(
        ...,
        description="ID of the similarity matrix",
        examples=["sim_001"],
    )
    format: str = Field(
        default="png",
        description="Output format: png, svg, pdf",
        examples=["png"],
    )
    dpi: int = Field(
        default=300,
        description="Resolution in DPI",
        examples=[300],
    )
    color_scheme: str = Field(
        default="viridis",
        description="Color scheme: viridis, plasma, inferno, magma, coolwarm",
        examples=["viridis"],
    )


class TopologyGraphRequest(BaseModel):
    """Request for generating a topology graph."""
    
    topology_id: str = Field(
        ...,
        description="ID of the topology result",
        examples=["topo_001"],
    )
    format: str = Field(
        default="png",
        description="Output format: png, svg, pdf",
        examples=["png"],
    )
    layout: str = Field(
        default="spring",
        description="Graph layout: spring, circular, kamada_kawai",
        examples=["spring"],
    )
    show_labels: bool = Field(
        default=True,
        description="Whether to show node labels",
    )
    dpi: int = Field(
        default=300,
        description="Resolution in DPI",
        examples=[300],
    )


class PropagationFlowRequest(BaseModel):
    """Request for generating a propagation flow diagram."""
    
    propagation_id: str = Field(
        ...,
        description="ID of the propagation analysis",
        examples=["prop_001"],
    )
    format: str = Field(
        default="svg",
        description="Output format: png, svg",
        examples=["svg"],
    )
    animation: bool = Field(
        default=True,
        description="Whether to include animation (SVG only)",
    )
    timeline: bool = Field(
        default=True,
        description="Whether to show timeline",
    )


class VisualizationResponse(BaseModel):
    """Response from visualization generation."""
    
    visualization_id: str = Field(
        ...,
        description="Unique visualization identifier",
        examples=["viz_heat_001"],
    )
    type: str = Field(
        ...,
        description="Visualization type: heatmap, topology_graph, propagation_flow",
        examples=["heatmap"],
    )
    download_url: str = Field(
        ...,
        description="URL to download the visualization",
        examples=["/visualizations/download/viz_heat_001.png"],
    )
    thumbnail_url: Optional[str] = Field(
        default=None,
        description="URL to thumbnail (if available)",
        examples=["/visualizations/thumbnail/viz_heat_001.png"],
    )
    animation_url: Optional[str] = Field(
        default=None,
        description="URL to animation (for flow diagrams)",
    )
