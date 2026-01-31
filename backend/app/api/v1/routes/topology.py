# backend/app/api/v1/routes/topology.py
"""
Topology layer API endpoints.
"""

from fastapi import APIRouter, HTTPException

from app.api.v1.schemas import (
    ComputeSimilarityRequest,
    ComputeSimilarityResponse,
    SimilarityMatrix,
    InferTopologyRequest,
    InferTopologyResponse,
    TopologyResult,
)
from app.services.similarity_service import similarity_service
from app.services.topology_service import topology_service

router = APIRouter()


@router.post("/compute-similarity", response_model=ComputeSimilarityResponse)
async def compute_similarity(request: ComputeSimilarityRequest) -> ComputeSimilarityResponse:
    """
    Compute similarity matrix from uploaded data.
    
    Supports correlation, DTW, and mutual information methods.
    """
    try:
        result = similarity_service.compute_similarity(
            upload_id=request.upload_id,
            method=request.method,
            window_size=request.window_size,
            cell_ids=request.cell_ids,
        )
        return ComputeSimilarityResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similarity computation failed: {str(e)}")


@router.get("/similarity/{similarity_id}", response_model=SimilarityMatrix)
async def get_similarity(similarity_id: str) -> SimilarityMatrix:
    """
    Retrieve computed similarity matrix.
    """
    result = similarity_service.get_similarity(similarity_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Similarity matrix not found: {similarity_id}")
    return SimilarityMatrix(**result)


@router.post("/infer", response_model=InferTopologyResponse)
async def infer_topology(request: InferTopologyRequest) -> InferTopologyResponse:
    """
    Infer network topology from similarity matrix.
    
    Supports hierarchical, k-means, and DBSCAN clustering.
    """
    try:
        result = topology_service.infer_topology(
            similarity_id=request.similarity_id,
            clustering_method=request.clustering_method,
            num_clusters=request.num_clusters,
            distance_threshold=request.distance_threshold,
        )
        return InferTopologyResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Topology inference failed: {str(e)}")


@router.get("/result/{topology_id}", response_model=TopologyResult)
async def get_topology(topology_id: str) -> TopologyResult:
    """
    Retrieve topology inference result.
    """
    result = topology_service.get_topology(topology_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Topology not found: {topology_id}")
    return TopologyResult(**result)
