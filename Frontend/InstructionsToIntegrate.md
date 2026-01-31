# Frontend Integration Instructions

## Network Topology Intelligence Dashboard - Backend Integration Guide

This document provides detailed instructions for integrating the frontend with a backend API. The frontend is built with **React + TypeScript + Vite** and uses **Zustand** for state management.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Data Structures](#data-structures)
3. [Required API Endpoints](#required-api-endpoints)
4. [Integration Points](#integration-points)
5. [State Store Reference](#state-store-reference)
6. [UI Components Overview](#ui-components-overview)
7. [Example API Responses](#example-api-responses)

---

## Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation
```bash
cd Frontend
npm install
npm run dev
```

### Environment Variables (Create `.env` file)
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
```

---

## Data Structures

### 1. CellData
Represents individual network cells in the topology.

```typescript
interface CellData {
    id: string;              // Unique cell identifier (e.g., "cell_01")
    name: string;            // Display name (e.g., "CELL 01")
    group: string;           // Topology group ID this cell belongs to
    isAnomaly: boolean;      // Whether this cell has anomalous behavior
    anomalyScore?: number;   // Optional: 0-1 confidence score (0.89 = 89%)
}
```

### 2. TopologyGroup
Represents groups of cells that share infrastructure.

```typescript
interface TopologyGroup {
    id: string;              // Group identifier (e.g., "link_1")
    name: string;            // Display name (e.g., "Link 1")
    color: string;           // Hex color for visualization (e.g., "#d4a574")
    cells: string[];         // Array of cell IDs in this group
}
```

### 3. Similarity Matrix
A 2D array representing correlation/similarity between cells.

```typescript
type SimilarityMatrix = number[][];  // NxN matrix where N = number of cells
// Values: 0.0 (no correlation) to 1.0 (identical)
// Matrix should be symmetric: matrix[i][j] === matrix[j][i]
// Diagonal should be 1.0: matrix[i][i] === 1.0
```

### 4. PropagationEvent
Represents congestion propagation between topology groups.

```typescript
interface PropagationEvent {
    id: string;                                    // Event ID
    sourceGroup: string;                           // Source topology group ID
    targetGroup: string;                           // Target topology group ID
    timestamp: number;                             // Time offset in minutes
    severity: 'healthy' | 'degraded' | 'critical'; // Severity level
    correlation: number;                           // 0-1 correlation strength
}
```

### 5. Insight
LLM-generated insights for the intelligence panel.

```typescript
interface Insight {
    id: string;                           // Unique insight ID
    type: 'info' | 'warning' | 'critical'; // Severity type
    message: string;                       // Human-readable insight text
    timestamp: Date;                       // When the insight was generated
}
```

---

## Required API Endpoints

### 1. GET /api/similarity-matrix
Returns the cell similarity matrix.

**Response:**
```json
{
    "matrix": [[1.0, 0.78, 0.65, ...], [0.78, 1.0, 0.82, ...], ...],
    "cellIds": ["cell_01", "cell_02", "cell_03", ...],
    "timestamp": "2024-01-31T12:00:00Z"
}
```

### 2. GET /api/cells
Returns cell data with anomaly information.

**Response:**
```json
{
    "cells": [
        {
            "id": "cell_01",
            "name": "CELL 01",
            "group": "link_1",
            "isAnomaly": false,
            "anomalyScore": null
        },
        {
            "id": "cell_06",
            "name": "CELL 06",
            "group": "link_1",
            "isAnomaly": true,
            "anomalyScore": 0.89
        }
    ]
}
```

### 3. GET /api/topology-groups
Returns detected topology clusters.

**Response:**
```json
{
    "groups": [
        {
            "id": "link_1",
            "name": "Link 1",
            "color": "#d4a574",
            "cells": ["cell_01", "cell_02", "cell_03", "cell_04", "cell_05", "cell_06"]
        },
        {
            "id": "link_2",
            "name": "Link 2",
            "color": "#7aa874",
            "cells": ["cell_07", "cell_08", "cell_09", "cell_10", "cell_11", "cell_12"]
        }
    ]
}
```

### 4. GET /api/propagation-events
Returns congestion propagation timeline.

**Response:**
```json
{
    "events": [
        {
            "id": "p1",
            "sourceGroup": "link_1",
            "targetGroup": "link_2",
            "timestamp": 0,
            "severity": "degraded",
            "correlation": 0.65
        }
    ],
    "timeRange": [0, 15]
}
```

### 5. GET /api/insights
Returns LLM-generated insights.

**Response:**
```json
{
    "insights": [
        {
            "id": "i1",
            "type": "critical",
            "message": "Detected anomalous congestion pattern in Cell 06 correlating with Link 1 degradation",
            "timestamp": "2024-01-31T12:00:00Z"
        },
        {
            "id": "i2",
            "type": "warning",
            "message": "Cells 01-06 showing 78% correlation - likely share fronthaul segment",
            "timestamp": "2024-01-31T12:00:00Z"
        }
    ]
}
```

### 6. POST /api/upload-csv
Uploads CSV data for analysis.

**Request:**
```
Content-Type: multipart/form-data
file: <CSV file>
```

**Response:**
```json
{
    "status": "processing",
    "batchId": "BATCH-ML200ZX5",
    "estimatedTime": 30
}
```

### 7. POST /api/chat (for LLM Copilot)
Sends a chat message to the LLM.

**Request:**
```json
{
    "message": "Tell me about anomalies",
    "context": {
        "currentView": "heatmap",
        "selectedCells": ["cell_01", "cell_06"],
        "anomalies": ["cell_06", "cell_18"]
    }
}
```

**Response:**
```json
{
    "response": "Based on my analysis, I've detected 2 anomalies:\n\n• CELL_06: 89% confidence\n• CELL_18: 76% confidence\n\nThe primary anomaly in Cell 06 shows elevated congestion patterns...",
    "suggestedActions": ["Investigate Link 1", "Monitor Cell 06"]
}
```

### 8. WebSocket /ws/live-updates (Optional)
Real-time updates for live monitoring.

**Message Types:**
```json
// New insight
{"type": "insight", "data": {"id": "i3", "type": "warning", "message": "..."}}

// Anomaly update
{"type": "anomaly", "data": {"cellId": "cell_12", "score": 0.72}}

// Matrix update
{"type": "matrix_update", "data": {"matrix": [...], "timestamp": "..."}}
```

---

## Integration Points

### A. Main Store File
**Location:** `src/store/networkStore.ts`

Key functions to integrate:

```typescript
// Load data from API
loadData: (matrix: number[][], cellIds: string[], topology: Record<string, string>) => void

// Add new insight from backend
addInsight: (insight: Omit<Insight, 'id' | 'timestamp'>) => void
```

### B. API Service (Create this file)
**Suggested Location:** `src/services/api.ts`

```typescript
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export async function fetchSimilarityMatrix() {
    const response = await fetch(`${API_BASE}/similarity-matrix`);
    return response.json();
}

export async function fetchCells() {
    const response = await fetch(`${API_BASE}/cells`);
    return response.json();
}

export async function fetchTopologyGroups() {
    const response = await fetch(`${API_BASE}/topology-groups`);
    return response.json();
}

export async function uploadCSV(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE}/upload-csv`, {
        method: 'POST',
        body: formData
    });
    return response.json();
}

export async function sendChatMessage(message: string, context: any) {
    const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, context })
    });
    return response.json();
}
```

### C. Data Loading Hook (Create this file)
**Suggested Location:** `src/hooks/useDataLoader.ts`

```typescript
import { useEffect } from 'react';
import { useNetworkStore } from '../store/networkStore';
import * as api from '../services/api';

export function useDataLoader() {
    const { loadData, addInsight } = useNetworkStore();

    useEffect(() => {
        async function loadInitialData() {
            try {
                const [matrixData, cellsData, groupsData] = await Promise.all([
                    api.fetchSimilarityMatrix(),
                    api.fetchCells(),
                    api.fetchTopologyGroups()
                ]);

                // Build topology mapping
                const topology: Record<string, string> = {};
                cellsData.cells.forEach((cell: any) => {
                    topology[cell.id] = cell.group;
                });

                loadData(matrixData.matrix, matrixData.cellIds, topology);
            } catch (error) {
                console.error('Failed to load data:', error);
            }
        }

        loadInitialData();
    }, [loadData]);
}
```

---

## State Store Reference

### Current State Shape
```typescript
interface NetworkState {
    // Data (from backend)
    similarityMatrix: number[][];      // NxN correlation matrix
    cellIds: string[];                 // Ordered list of cell IDs
    cells: CellData[];                 // Cell metadata with anomaly info
    topologyGroups: TopologyGroup[];   // Detected topology clusters
    propagationEvents: PropagationEvent[]; // Congestion propagation timeline
    insights: Insight[];               // LLM-generated insights

    // UI State (frontend only)
    viewMode: 'heatmap' | 'topology' | 'propagation';
    interactionMode: 'explore' | 'focus' | 'compare' | 'timeline';
    hoveredCell: { row: number; col: number } | null;
    selectedCells: { row: number; col: number }[];
    currentTime: number;               // For timeline scrubber
    timeRange: [number, number];       // Min/max time range
}
```

---

## UI Components Overview

| Component | Description | Data Dependencies |
|-----------|-------------|-------------------|
| `InteractiveHeatmap` | 24x24 cell similarity matrix | `similarityMatrix`, `cellIds`, `cells` |
| `TopologyGraph` | Force-directed network graph | `topologyGroups`, `cells` |
| `PropagationFlow` | Animated congestion flow | `propagationEvents`, `topologyGroups` |
| `BottomPanel` | Insights, recommendations, anomalies | `insights`, `cells` |
| `FloatingChatbot` | LLM chat interface | Needs `/api/chat` endpoint |
| `LeftRail` | Quick metrics sidebar | `cells`, `topologyGroups` |

---

## Example API Responses

### Complete Initial Load Response
For a single API call that returns all data:

```json
{
    "matrix": [
        [1.0, 0.85, 0.72, 0.68, 0.75, 0.82, 0.15, 0.12, ...],
        [0.85, 1.0, 0.78, 0.71, 0.69, 0.73, 0.18, 0.14, ...],
        ...
    ],
    "cellIds": [
        "cell_01", "cell_02", "cell_03", "cell_04", "cell_05", "cell_06",
        "cell_07", "cell_08", "cell_09", "cell_10", "cell_11", "cell_12",
        "cell_13", "cell_14", "cell_15", "cell_16", "cell_17", "cell_18",
        "cell_19", "cell_20", "cell_21", "cell_22", "cell_23", "cell_24"
    ],
    "cells": [
        {"id": "cell_01", "name": "CELL 01", "group": "link_1", "isAnomaly": false},
        {"id": "cell_02", "name": "CELL 02", "group": "link_1", "isAnomaly": false},
        {"id": "cell_03", "name": "CELL 03", "group": "link_1", "isAnomaly": false},
        {"id": "cell_04", "name": "CELL 04", "group": "link_1", "isAnomaly": false},
        {"id": "cell_05", "name": "CELL 05", "group": "link_1", "isAnomaly": false},
        {"id": "cell_06", "name": "CELL 06", "group": "link_1", "isAnomaly": true, "anomalyScore": 0.89},
        {"id": "cell_07", "name": "CELL 07", "group": "link_2", "isAnomaly": false},
        ...
    ],
    "topologyGroups": [
        {"id": "link_1", "name": "Link 1", "color": "#d4a574", "cells": ["cell_01", "cell_02", "cell_03", "cell_04", "cell_05", "cell_06"]},
        {"id": "link_2", "name": "Link 2", "color": "#7aa874", "cells": ["cell_07", "cell_08", "cell_09", "cell_10", "cell_11", "cell_12"]},
        {"id": "link_3", "name": "Link 3", "color": "#7488a8", "cells": ["cell_13", "cell_14", "cell_15", "cell_16", "cell_17", "cell_18"]},
        {"id": "link_4", "name": "Link 4", "color": "#a87488", "cells": ["cell_19", "cell_20", "cell_21", "cell_22", "cell_23", "cell_24"]}
    ],
    "propagationEvents": [
        {"id": "p1", "sourceGroup": "link_1", "targetGroup": "link_2", "timestamp": 0, "severity": "degraded", "correlation": 0.65},
        {"id": "p2", "sourceGroup": "link_2", "targetGroup": "link_3", "timestamp": 5, "severity": "critical", "correlation": 0.82},
        {"id": "p3", "sourceGroup": "link_1", "targetGroup": "link_3", "timestamp": 8, "severity": "degraded", "correlation": 0.45},
        {"id": "p4", "sourceGroup": "link_3", "targetGroup": "link_4", "timestamp": 12, "severity": "healthy", "correlation": 0.33}
    ],
    "insights": [
        {"id": "i1", "type": "critical", "message": "Detected anomalous congestion pattern in Cell 06 correlating with Link 1 degradation", "timestamp": "2024-01-31T12:00:00Z"},
        {"id": "i2", "type": "warning", "message": "Cells 01-06 showing 78% correlation - likely share fronthaul segment", "timestamp": "2024-01-31T12:00:00Z"},
        {"id": "i3", "type": "info", "message": "Topology clustering complete: 4 distinct groups identified with 94% confidence", "timestamp": "2024-01-31T12:00:00Z"}
    ]
}
```

---

## Notes for Backend Developer

1. **Matrix must be symmetric** - `matrix[i][j] === matrix[j][i]`
2. **Cell IDs must match** - `cellIds` order must match matrix row/column order
3. **Anomaly scores** are optional but recommended (0-1 range)
4. **Timestamps** should be ISO 8601 format
5. **Colors** should be valid hex codes for visualization
6. **Severity levels** must be exactly: `'healthy'`, `'degraded'`, or `'critical'`

---

## Contact

For questions about the frontend integration, contact the frontend developer.

**Last Updated:** 2024-01-31

---

## File Structure Reference

```
Frontend/
├── src/
│   ├── components/
│   │   ├── InteractiveHeatmap.tsx   # Main heatmap visualization
│   │   ├── TopologyGraph.tsx        # Network graph
│   │   ├── PropagationFlow.tsx      # Congestion flow visualization
│   │   ├── BottomPanel.tsx          # Insights panel
│   │   ├── FloatingChatbot.tsx      # LLM chat interface
│   │   ├── Header.tsx               # Top navigation
│   │   ├── LeftRail.tsx             # Left sidebar metrics
│   │   └── ...
│   ├── store/
│   │   └── networkStore.ts          # Zustand state management
│   ├── hooks/
│   │   └── useKeyboardShortcuts.ts  # Keyboard navigation
│   ├── services/                    # CREATE THIS FOLDER
│   │   └── api.ts                   # API integration (to be created)
│   ├── App.tsx                      # Main app component
│   └── main.tsx                     # App entry point
├── InstructionsToIntegrate.md       # This file
└── package.json
```
