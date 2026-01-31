# backend/app/api/v1/routes/copilot.py
"""
LLM Copilot API endpoints.
"""

from fastapi import APIRouter, HTTPException

from app.api.v1.schemas import (
    GenerateInsightsRequest,
    GenerateInsightsResponse,
    CopilotReport,
    QueryRequest,
    QueryResponse,
)
from app.services.copilot_service import copilot_service

router = APIRouter()


@router.post("/generate-insights", response_model=GenerateInsightsResponse)
async def generate_insights(request: GenerateInsightsRequest) -> GenerateInsightsResponse:
    """
    Generate LLM-powered insights from analysis results.
    
    Combines topology, anomaly, and propagation data to produce
    actionable insights and recommendations.
    """
    try:
        result = await copilot_service.generate_insights(
            topology_id=request.topology_id,
            anomaly_id=request.anomaly_id,
            propagation_id=request.propagation_id,
            context=request.context.model_dump() if request.context else None,
        )
        return GenerateInsightsResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insight generation failed: {str(e)}")


@router.get("/report/{report_id}", response_model=CopilotReport)
async def get_report(report_id: str) -> CopilotReport:
    """
    Retrieve generated copilot report.
    """
    result = copilot_service.get_report(report_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Report not found: {report_id}")
    return CopilotReport(**result)


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    """
    Interactive query about network state.
    
    Ask natural language questions about the network topology,
    anomalies, and congestion patterns.
    """
    try:
        result = await copilot_service.query(
            query=request.query,
            context=request.context.model_dump() if request.context else None,
        )
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
