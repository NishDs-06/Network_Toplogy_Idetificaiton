# backend/app/api/v1/schemas/__init__.py
"""
API v1 schemas package.

Export all schemas for convenient importing.
"""

from .common import (
    ErrorDetail,
    ErrorResponse,
    MetadataResponse,
    APIResponse,
    PaginationParams,
    PaginatedResponse,
)

from .data import (
    DataMetadata,
    DataUploadRequest,
    DataUploadResponse,
    LossEventRecord,
    ThroughputRecord,
)

from .topology import (
    ComputeSimilarityRequest,
    ComputeSimilarityResponse,
    SimilarityMatrix,
    InferTopologyRequest,
    InferTopologyResponse,
    LinkGroup,
    CellAssignment,
    TopologyResult,
)

from .intelligence import (
    DetectAnomaliesRequest,
    DetectAnomaliesResponse,
    AnomalyScore,
    AnomalyStatistics,
    AnomalyResult,
    AnalyzePropagationRequest,
    AnalyzePropagationResponse,
    PropagationEvent,
    PropagationPath,
    NetworkNode,
    NetworkEdge,
    NetworkGraph,
    PropagationResult,
)

from .copilot import (
    InsightContext,
    GenerateInsightsRequest,
    GenerateInsightsResponse,
    NetworkInsight,
    ActionRecommendation,
    TopologySummary,
    ReportMetadata,
    CopilotReport,
    QueryContext,
    QueryRequest,
    SupportingData,
    QueryResponse,
)

from .visualization import (
    HeatmapRequest,
    TopologyGraphRequest,
    PropagationFlowRequest,
    VisualizationResponse,
)

from .batch import (
    BatchConfig,
    BatchAnalysisRequest,
    BatchStep,
    BatchResults,
    BatchAnalysisResponse,
    BatchStatusResponse,
)

from .health import (
    ServiceStatus,
    HealthResponse,
    MetricsResponse,
)

__all__ = [
    # Common
    "ErrorDetail",
    "ErrorResponse",
    "MetadataResponse",
    "APIResponse",
    "PaginationParams",
    "PaginatedResponse",
    # Data
    "DataMetadata",
    "DataUploadRequest",
    "DataUploadResponse",
    "LossEventRecord",
    "ThroughputRecord",
    # Topology
    "ComputeSimilarityRequest",
    "ComputeSimilarityResponse",
    "SimilarityMatrix",
    "InferTopologyRequest",
    "InferTopologyResponse",
    "LinkGroup",
    "CellAssignment",
    "TopologyResult",
    # Intelligence
    "DetectAnomaliesRequest",
    "DetectAnomaliesResponse",
    "AnomalyScore",
    "AnomalyStatistics",
    "AnomalyResult",
    "AnalyzePropagationRequest",
    "AnalyzePropagationResponse",
    "PropagationEvent",
    "PropagationPath",
    "NetworkNode",
    "NetworkEdge",
    "NetworkGraph",
    "PropagationResult",
    # Copilot
    "InsightContext",
    "GenerateInsightsRequest",
    "GenerateInsightsResponse",
    "NetworkInsight",
    "ActionRecommendation",
    "TopologySummary",
    "ReportMetadata",
    "CopilotReport",
    "QueryContext",
    "QueryRequest",
    "SupportingData",
    "QueryResponse",
    # Visualization
    "HeatmapRequest",
    "TopologyGraphRequest",
    "PropagationFlowRequest",
    "VisualizationResponse",
    # Batch
    "BatchConfig",
    "BatchAnalysisRequest",
    "BatchStep",
    "BatchResults",
    "BatchAnalysisResponse",
    "BatchStatusResponse",
    # Health
    "ServiceStatus",
    "HealthResponse",
    "MetricsResponse",
]
