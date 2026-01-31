# backend/app/api/v1/routes/frontend.py
"""
Frontend Integration API Endpoints.

These endpoints match exactly what the React frontend expects,
as documented in Frontend/InstructionsToIntegrate.md.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from app.services.frontend_service import frontend_service

router = APIRouter()


# ============================================================
# Response Models
# ============================================================

class SimilarityMatrixResponse(BaseModel):
    matrix: List[List[float]]
    cellIds: List[str]
    timestamp: str


class CellData(BaseModel):
    id: str
    name: str
    group: str
    isAnomaly: bool
    anomalyScore: Optional[float] = None
    confidence: float = 0.0


class CellsResponse(BaseModel):
    cells: List[CellData]


class TopologyGroup(BaseModel):
    id: str
    name: str
    color: str
    cells: List[str]


class TopologyGroupsResponse(BaseModel):
    groups: List[TopologyGroup]


class PropagationEvent(BaseModel):
    id: str
    sourceGroup: str
    targetGroup: str
    timestamp: float
    severity: str
    correlation: float


class PropagationResponse(BaseModel):
    events: List[PropagationEvent]
    timeRange: List[int]


class Insight(BaseModel):
    id: str
    type: str
    message: str
    timestamp: str


class InsightsResponse(BaseModel):
    insights: List[Insight]


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    response: str
    suggestedActions: List[str] = []


# ============================================================
# Endpoints
# ============================================================

@router.get("/similarity-matrix", response_model=SimilarityMatrixResponse)
async def get_similarity_matrix():
    """
    Returns the cell similarity matrix.
    
    Used by: InteractiveHeatmap component
    """
    try:
        data = frontend_service.get_similarity_matrix()
        return SimilarityMatrixResponse(**data)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Similarity matrix not found: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get similarity matrix: {e}"
        )


@router.get("/cells", response_model=CellsResponse)
async def get_cells():
    """
    Returns cell data with anomaly information.
    
    Used by: LeftRail, BottomPanel, TopologyGraph components
    """
    try:
        data = frontend_service.get_cells()
        return CellsResponse(**data)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404, 
            detail=f"Clustering data not found: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cells: {e}"
        )


@router.get("/topology-groups", response_model=TopologyGroupsResponse)
async def get_topology_groups():
    """
    Returns detected topology clusters/groups.
    
    Used by: TopologyGraph, PropagationFlow components
    """
    try:
        data = frontend_service.get_topology_groups()
        return TopologyGroupsResponse(**data)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Topology data not found: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get topology groups: {e}"
        )


@router.get("/propagation-events", response_model=PropagationResponse)
async def get_propagation_events():
    """
    Returns congestion propagation timeline.
    
    Used by: PropagationFlow component
    """
    try:
        data = frontend_service.get_propagation_events()
        return PropagationResponse(**data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get propagation events: {e}"
        )


@router.get("/insights", response_model=InsightsResponse)
async def get_insights():
    """
    Returns LLM-generated insights (uses cache if available).
    
    Used by: BottomPanel component
    """
    try:
        data = frontend_service.get_insights()
        return InsightsResponse(**data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get insights: {e}"
        )


class Recommendation(BaseModel):
    id: str
    type: str
    title: str
    description: str


class RecommendationsResponse(BaseModel):
    recommendations: List[Recommendation]


@router.get("/recommendations", response_model=RecommendationsResponse)
async def get_recommendations():
    """
    Returns LLM-generated recommendations (uses cache if available).
    
    Used by: BottomPanel component
    """
    try:
        data = frontend_service.get_recommendations()
        return RecommendationsResponse(**data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recommendations: {e}"
        )


@router.post("/generate-insights")
async def generate_insights():
    """
    Trigger LLM insight generation (call once on page load).
    Results are cached for 1 hour to reduce GPU load.
    """
    try:
        data = await frontend_service.get_insights_llm()
        return data
    except Exception as e:
        # Return default insights if LLM fails
        return frontend_service.get_insights()


@router.post("/generate-recommendations")
async def generate_recommendations():
    """
    Trigger LLM recommendation generation (call once on page load).
    Results are cached for 1 hour to reduce GPU load.
    """
    try:
        data = await frontend_service.get_recommendations_llm()
        return data
    except Exception as e:
        return frontend_service.get_recommendations()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send message to LLM copilot.
    
    Used by: FloatingChatbot component
    """
    try:
        from app.services.copilot_service import copilot_service
        
        # Build context from current data
        context = request.context or {}
        
        result = await copilot_service.query(
            query=request.message,
            context=context
        )
        
        return ChatResponse(
            response=result.get("answer", "I couldn't process that request."),
            suggestedActions=result.get("related_insights", [])
        )
    except Exception as e:
        # Return graceful fallback
        return ChatResponse(
            response=f"I'm having trouble connecting to my knowledge base. Error: {str(e)}",
            suggestedActions=["Try again", "Check system status"]
        )


@router.get("/state")
async def get_complete_state():
    """
    Returns complete application state in one call.
    Useful for initial page load.
    """
    try:
        return frontend_service.get_complete_state()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get application state: {e}"
        )


@router.post("/refresh-cache")
async def refresh_cache():
    """
    Force refresh of cached data.
    Call this after uploading new data or running analysis.
    """
    frontend_service.clear_cache()
    return {"status": "ok", "message": "Cache cleared"}

