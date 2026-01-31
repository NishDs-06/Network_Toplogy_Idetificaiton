// Frontend/src/services/api.ts
/**
 * API Service for Backend Integration
 * 
 * This service connects the frontend to the backend API.
 * All endpoints match the backend's /v1/api/* routes.
 */

// API base URL - uses environment variable or localhost default
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/v1/api';

// ============================================================
// Types matching backend responses
// ============================================================

export interface SimilarityMatrixResponse {
    matrix: number[][];
    cellIds: string[];
    timestamp: string;
}

export interface CellData {
    id: string;
    name: string;
    group: string;
    isAnomaly: boolean;
    anomalyScore: number | null;
    confidence: number;
}

export interface CellsResponse {
    cells: CellData[];
}

export interface TopologyGroup {
    id: string;
    name: string;
    color: string;
    cells: string[];
}

export interface TopologyGroupsResponse {
    groups: TopologyGroup[];
}

export interface PropagationEvent {
    id: string;
    sourceGroup: string;
    targetGroup: string;
    timestamp: number;
    severity: 'healthy' | 'degraded' | 'critical';
    correlation: number;
}

export interface PropagationResponse {
    events: PropagationEvent[];
    timeRange: [number, number];
}

export interface Insight {
    id: string;
    type: 'info' | 'warning' | 'critical';
    message: string;
    timestamp: string;
}

export interface InsightsResponse {
    insights: Insight[];
}

export interface Recommendation {
    id: string;
    type: 'action' | 'monitor' | 'info';
    title: string;
    description: string;
}

export interface RecommendationsResponse {
    recommendations: Recommendation[];
}

export interface ChatResponse {
    response: string;
    suggestedActions: string[];
}

export interface CompleteStateResponse {
    matrix: number[][];
    cellIds: string[];
    cells: CellData[];
    topologyGroups: TopologyGroup[];
    propagationEvents: PropagationEvent[];
    insights: Insight[];
}

// ============================================================
// API Functions
// ============================================================

/**
 * Fetch similarity matrix
 */
export async function fetchSimilarityMatrix(): Promise<SimilarityMatrixResponse> {
    const response = await fetch(`${API_BASE}/similarity-matrix`);
    if (!response.ok) {
        throw new Error(`Failed to fetch similarity matrix: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Fetch cell data with anomaly information
 */
export async function fetchCells(): Promise<CellsResponse> {
    const response = await fetch(`${API_BASE}/cells`);
    if (!response.ok) {
        throw new Error(`Failed to fetch cells: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Fetch topology groups (clusters)
 */
export async function fetchTopologyGroups(): Promise<TopologyGroupsResponse> {
    const response = await fetch(`${API_BASE}/topology-groups`);
    if (!response.ok) {
        throw new Error(`Failed to fetch topology groups: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Fetch propagation events for timeline
 */
export async function fetchPropagationEvents(): Promise<PropagationResponse> {
    const response = await fetch(`${API_BASE}/propagation-events`);
    if (!response.ok) {
        throw new Error(`Failed to fetch propagation events: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Fetch LLM-generated insights
 */
export async function fetchInsights(): Promise<InsightsResponse> {
    const response = await fetch(`${API_BASE}/insights`);
    if (!response.ok) {
        throw new Error(`Failed to fetch insights: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Send chat message to LLM copilot
 */
export async function sendChatMessage(
    message: string,
    context?: Record<string, unknown>
): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, context }),
    });
    if (!response.ok) {
        throw new Error(`Chat request failed: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Fetch complete application state in one call
 * This is more efficient for initial page load
 */
export async function fetchCompleteState(): Promise<CompleteStateResponse> {
    const response = await fetch(`${API_BASE}/state`);
    if (!response.ok) {
        throw new Error(`Failed to fetch application state: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Force refresh of cached data on the server
 */
export async function refreshCache(): Promise<void> {
    const response = await fetch(`${API_BASE}/refresh-cache`, { method: 'POST' });
    if (!response.ok) {
        throw new Error(`Failed to refresh cache: ${response.statusText}`);
    }
}

/**
 * Upload CSV file for analysis
 */
export async function uploadCSV(file: File): Promise<{ status: string; batchId: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE.replace('/api', '')}/data/upload`, {
        method: 'POST',
        body: formData,
    });
    if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
    }
    return response.json();
}

export async function fetchRecommendations(): Promise<Recommendation[]> {
    const response = await fetch(`${API_BASE}/recommendations`);
    if (!response.ok) throw new Error('Failed to fetch recommendations');
    const data = await response.json();
    return data.recommendations || [];
}

// =============================================================
// LLM Generation (call once on page load, results cached 1 hour)
// =============================================================

export async function triggerLLMInsights(): Promise<InsightsResponse> {
    try {
        const response = await fetch(`${API_BASE}/generate-insights`, {
            method: 'POST',
        });
        if (!response.ok) {
            console.warn('LLM insights failed, using defaults');
            return fetchInsights();
        }
        return response.json();
    } catch {
        return fetchInsights();
    }
}

export async function triggerLLMRecommendations(): Promise<RecommendationsResponse> {
    try {
        const response = await fetch(`${API_BASE}/generate-recommendations`, {
            method: 'POST',
        });
        if (!response.ok) {
            console.warn('LLM recommendations failed, using defaults');
            return { recommendations: await fetchRecommendations() };
        }
        return response.json();
    } catch {
        return { recommendations: await fetchRecommendations() };
    }
}

// ============================================================
// Health Check
// ============================================================

/**
 * Check if backend is available
 */
export async function checkHealth(): Promise<boolean> {
    try {
        const response = await fetch(`${API_BASE.replace('/api', '')}/health`);
        return response.ok;
    } catch {
        return false;
    }
}
