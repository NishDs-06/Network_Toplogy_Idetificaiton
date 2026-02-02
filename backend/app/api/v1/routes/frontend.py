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


class RecommendationExpandRequest(BaseModel):
    rec_id: str
    title: str
    type: str


class RecommendationExpandResponse(BaseModel):
    rec_id: str
    title: str
    type: str
    detailed_description: str
    steps: List[str]
    impact: str
    priority: str


# Cache for expanded recommendations
_rec_detail_cache: Dict[str, Dict] = {}


@router.post("/recommendation-expand", response_model=RecommendationExpandResponse)
async def expand_recommendation(request: RecommendationExpandRequest):
    """
    Get detailed LLM-generated content for a recommendation.
    Cached for 1 hour per recommendation.
    """
    cache_key = f"rec_{request.rec_id}"
    
    # Check cache
    if cache_key in _rec_detail_cache:
        return RecommendationExpandResponse(**_rec_detail_cache[cache_key])
    
    try:
        from app.providers.ollama import OllamaProvider
        from app.providers.base import ChatMessage
        import pandas as pd
        from pathlib import Path
        
        # Load network context
        PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent
        anomaly_path = PROJECT_ROOT / "ML" / "outputs" / "cell_anomalies.csv"
        
        context = ""
        if anomaly_path.exists():
            df = pd.read_csv(anomaly_path)
            cell_stats = df.groupby("cell_id").agg({"anomaly": "mean"}).reset_index()
            top_anomalies = cell_stats.nlargest(3, "anomaly")
            context = f"Top anomalies: {', '.join([f'Cell {int(r.cell_id)} ({r.anomaly*100:.0f}%)' for _, r in top_anomalies.iterrows()])}"
        
        provider = OllamaProvider()
        
        messages = [
            ChatMessage(
                role="system",
                content="""You are a network operations advisor. For the given recommendation, provide:
1. A detailed description (2-3 sentences)
2. 3-4 actionable steps to implement
3. Expected impact
4. Priority level (HIGH/MEDIUM/LOW)

Format your response EXACTLY as:
DESCRIPTION: [your description]
STEPS:
- Step 1
- Step 2
- Step 3
IMPACT: [expected impact]
PRIORITY: [HIGH/MEDIUM/LOW]"""
            ),
            ChatMessage(
                role="user",
                content=f"Recommendation: {request.title} (Type: {request.type})\nNetwork context: {context}"
            ),
        ]
        
        result = await provider.chat(messages)
        llm_text = result.content
        
        # Parse response
        description = ""
        steps = []
        impact = "Improved network stability"
        priority = "MEDIUM"
        
        lines = llm_text.split('\n')
        current_section = ""
        for line in lines:
            line = line.strip()
            if line.startswith("DESCRIPTION:"):
                current_section = "desc"
                description = line.replace("DESCRIPTION:", "").strip()
            elif line.startswith("STEPS:"):
                current_section = "steps"
            elif line.startswith("IMPACT:"):
                current_section = "impact"
                impact = line.replace("IMPACT:", "").strip()
            elif line.startswith("PRIORITY:"):
                priority = line.replace("PRIORITY:", "").strip()
            elif current_section == "desc" and line:
                description += " " + line
            elif current_section == "steps" and line.startswith("-"):
                steps.append(line[1:].strip())
            elif current_section == "impact" and line:
                impact += " " + line
        
        # Fallback if parsing fails
        if not description:
            description = f"Detailed analysis for: {request.title}"
        if not steps:
            steps = ["Review affected cells", "Check network logs", "Apply remediation"]
        
        detail = {
            "rec_id": request.rec_id,
            "title": request.title,
            "type": request.type,
            "detailed_description": description[:300],
            "steps": steps[:5],
            "impact": impact[:150],
            "priority": priority
        }
        
        _rec_detail_cache[cache_key] = detail
        return RecommendationExpandResponse(**detail)
        
    except Exception as e:
        # Fallback response
        return RecommendationExpandResponse(
            rec_id=request.rec_id,
            title=request.title,
            type=request.type,
            detailed_description=f"This recommendation suggests action based on current network analysis.",
            steps=["Review the identified cells", "Check network performance metrics", "Apply suggested changes"],
            impact="Improved network health and reduced anomalies",
            priority="MEDIUM"
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
    Send message to LLM copilot with rich network context.
    
    Used by: FloatingChatbot component
    """
    try:
        from app.services.copilot_service import copilot_service
        import pandas as pd
        from pathlib import Path
        
        # Build rich context from actual data
        PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent
        
        # Load anomaly data
        anomaly_path = PROJECT_ROOT / "ML" / "outputs" / "cell_anomalies.csv"
        anomaly_context = ""
        if anomaly_path.exists():
            df = pd.read_csv(anomaly_path)
            cell_stats = df.groupby("cell_id").agg({
                "anomaly": "mean",
                "confidence": "mean"
            }).reset_index()
            
            # Identify anomalous cells (>25% rate)
            anomalous = cell_stats[cell_stats["anomaly"] > 0.25]
            healthy = cell_stats[cell_stats["anomaly"] <= 0.25]
            
            anomaly_context = f"""
ANOMALY DETECTION RESULTS:
- Total cells monitored: {len(cell_stats)}
- Anomalous cells (>25% throughput drop rate): {len(anomalous)}
- Healthy cells: {len(healthy)}
- Threshold: 30% throughput drop from rolling median baseline

ANOMALOUS CELLS DETAIL:
"""
            for _, row in anomalous.iterrows():
                anomaly_context += f"- Cell {int(row['cell_id'])}: {row['anomaly']*100:.1f}% of time slots show anomaly, avg confidence {row['confidence']*100:.1f}%\n"
            
            if len(anomalous) == 0:
                anomaly_context += "- No cells currently exceed the 25% anomaly rate threshold\n"
            
            anomaly_context += f"""
TOP 5 CELLS BY ANOMALY RATE:
"""
            for _, row in cell_stats.nlargest(5, "anomaly").iterrows():
                status = "⚠️ FLAGGED" if row["anomaly"] > 0.25 else "✓ healthy"
                anomaly_context += f"- Cell {int(row['cell_id'])}: {row['anomaly']*100:.1f}% rate ({status})\n"
        
        # Load topology groups
        groups_path = PROJECT_ROOT / "Clustering" / "outputs" / "relative_fronthaul_groups.csv"
        topology_context = ""
        if groups_path.exists():
            groups_df = pd.read_csv(groups_path)
            n_groups = groups_df["relative_group"].nunique()
            topology_context = f"""
TOPOLOGY CLUSTERING:
- {n_groups} distinct fronthaul link groups identified
- Cells in same group share similar congestion patterns (likely shared infrastructure)

GROUPS:
"""
            for grp in sorted(groups_df["relative_group"].unique()):
                cells = groups_df[groups_df["relative_group"] == grp]["cell_id"].tolist()
                topology_context += f"- Link {grp}: Cells {cells}\n"
        
        # ML Pipeline context
        ml_context = """
ML PIPELINE EXPLANATION:
1. Raw data: Throughput measurements per cell per time slot
2. Baseline: Rolling 100-slot median per cell
3. Anomaly: When throughput drops >30% below baseline
4. Confidence: How severe the drop is (0% = at threshold, 100% = 2x threshold)
5. Cell flagged: If >25% of its slots are anomalous
6. Topology: Cells clustered by congestion similarity (Pearson correlation on z-scores)
"""
        
        full_context = f"""You are a Network Intelligence Copilot analyzing a telecom fronthaul network.

{anomaly_context}
{topology_context}
{ml_context}

Answer questions about:
- Which cells have anomalies and why
- Topology groupings and what they mean
- Recommendations for network issues
- Technical details about the ML detection

Be specific and reference actual cell numbers and data from the context above."""

        result = await copilot_service.query(
            query=request.message,
            context={"system_context": full_context}
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

