# backend/app/api/v1/routes/visualizations.py
"""
Visualization API endpoints.
"""

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.api.v1.schemas import (
    HeatmapRequest,
    TopologyGraphRequest,
    PropagationFlowRequest,
    VisualizationResponse,
)
from app.services.visualization_service import visualization_service

router = APIRouter()


@router.post("/heatmap", response_model=VisualizationResponse)
async def generate_heatmap(request: HeatmapRequest) -> VisualizationResponse:
    """
    Generate similarity heatmap visualization.
    
    Creates a color-coded matrix showing cell-to-cell similarity.
    """
    try:
        result = visualization_service.generate_heatmap(
            similarity_id=request.similarity_id,
            format=request.format,
            dpi=request.dpi,
            color_scheme=request.color_scheme,
        )
        return VisualizationResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Heatmap generation failed: {str(e)}")


@router.post("/topology-graph", response_model=VisualizationResponse)
async def generate_topology_graph(request: TopologyGraphRequest) -> VisualizationResponse:
    """
    Generate topology graph visualization.
    
    Creates a network graph showing groups and cell relationships.
    """
    try:
        result = visualization_service.generate_topology_graph(
            topology_id=request.topology_id,
            format=request.format,
            layout=request.layout,
            show_labels=request.show_labels,
            dpi=request.dpi,
        )
        return VisualizationResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Topology graph generation failed: {str(e)}")


@router.post("/propagation-flow", response_model=VisualizationResponse)
async def generate_propagation_flow(request: PropagationFlowRequest) -> VisualizationResponse:
    """
    Generate propagation flow diagram.
    
    Creates a directed graph showing congestion propagation patterns.
    """
    try:
        result = visualization_service.generate_propagation_flow(
            propagation_id=request.propagation_id,
            format=request.format,
            animation=request.animation,
            timeline=request.timeline,
        )
        return VisualizationResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Propagation flow generation failed: {str(e)}")


@router.get("/download/{viz_filename}")
async def download_visualization(viz_filename: str):
    """
    Download generated visualization file.
    """
    # Extract viz_id from filename
    viz_id = viz_filename.rsplit(".", 1)[0] if "." in viz_filename else viz_filename
    
    viz = visualization_service.get_visualization(viz_id)
    if not viz:
        raise HTTPException(status_code=404, detail=f"Visualization not found: {viz_id}")
    
    filepath = viz.get("filepath")
    if not filepath or not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Visualization file not found")
    
    return FileResponse(
        filepath,
        filename=viz_filename,
        media_type=f"image/{viz.get('format', 'png')}",
    )
