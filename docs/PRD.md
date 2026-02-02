# 📋 Product Requirements Document (PRD)

## Network Topology Identification System - v1.0

**Document Version:** 1.0  
**Last Updated:** February 2026  
**Status:** Released  

---

## 1. Executive Summary

### 1.1 Product Vision

The Network Topology Identification System is an AI-powered platform that automatically identifies shared infrastructure (fronthaul links) in 5G mobile networks by analyzing cell congestion patterns. It helps network operators detect anomalies, understand topology relationships, and make data-driven decisions.

### 1.2 Problem Statement

In modern 5G networks with thousands of cells, operators struggle to:
- Identify which cells share common fronthaul infrastructure
- Detect and diagnose congestion propagation patterns
- Correlate performance degradation across related cells
- Make real-time decisions based on network health

### 1.3 Solution

An end-to-end ML pipeline + interactive dashboard that:
1. **Ingests** raw throughput data from network cells
2. **Analyzes** congestion patterns using correlation metrics
3. **Clusters** cells into topology groups (shared infrastructure)
4. **Detects** anomalies using rolling baseline comparison
5. **Visualizes** results in an interactive React dashboard
6. **Provides** LLM-powered insights and recommendations

---

## 2. Product Overview

### 2.1 Target Users

| User Type | Use Case |
|-----------|----------|
| **NOC Engineers** | Real-time monitoring, anomaly investigation |
| **Network Planners** | Topology verification, capacity planning |
| **Data Scientists** | ML model tuning, threshold optimization |
| **Operations Managers** | High-level health dashboards, reporting |

### 2.2 Key Features (v1.0)

| Feature | Priority | Status |
|---------|----------|--------|
| Cell similarity matrix calculation | P0 | ✅ Complete |
| Hierarchical topology clustering | P0 | ✅ Complete |
| Anomaly detection (throughput drops) | P0 | ✅ Complete |
| Interactive topology graph | P0 | ✅ Complete |
| Correlation heatmap | P0 | ✅ Complete |
| Propagation flow visualization | P1 | ✅ Complete |
| LLM-powered chat copilot | P1 | ✅ Complete |
| AI-generated recommendations | P1 | ✅ Complete |
| Recommendation detail expansion | P2 | ✅ Complete |

---

## 3. Technical Specifications

### 3.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Raw .dat     │  │ Processed    │  │ ML Outputs       │   │
│  │ files        │→ │ CSV files    │→ │ (anomalies,      │   │
│  │              │  │              │  │  clusters)       │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   ML PIPELINE                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │Preprocessing │  │ Anomaly      │  │ Clustering       │   │
│  │• Parse .dat  │→ │ Detection    │→ │ • Similarity     │   │
│  │• Aggregate   │  │ • Rolling    │  │ • Hierarchical   │   │
│  │• Normalize   │  │   baseline   │  │ • Group assign   │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ REST API     │  │ LLM Service  │  │ Caching Layer    │   │
│  │ • /cells     │  │ • Ollama     │  │ • 5 min TTL      │   │
│  │ • /groups    │  │ • Chat       │  │ • 1 hr LLM cache │   │
│  │ • /chat      │  │ • Insights   │  │                  │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND (React + Vite)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Topology     │  │ Heatmap      │  │ Chat Interface   │   │
│  │ Graph (D3)   │  │ (D3)         │  │ (LLM Copilot)    │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Bottom Panel │  │ Left Rail    │  │ Propagation Flow │   │
│  │ (Insights)   │  │ (Metrics)    │  │ (SVG animation)  │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Frontend | React | 19.x |
| Frontend Build | Vite | 6.x |
| State Management | Zustand | 5.x |
| Visualization | D3.js | 7.x |
| Backend | FastAPI | 0.109+ |
| Language | Python | 3.12+ |
| ML Libraries | pandas, scipy, scikit-learn | Latest |
| LLM Provider | Ollama | Latest |
| Default Model | llama3.1:8b | - |

### 3.3 Data Flow

```
1. RAW DATA INPUT
   └── Preprocessing/raw_data/throughput-cell-*.dat
       Format: <timestamp> <throughput_value>

2. PREPROCESSING
   └── Preprocessing/outputs/multicell_throughputdata.csv
       Columns: cell_id, slot_id, throughput_slot

3. ANOMALY DETECTION
   └── ML/outputs/cell_anomalies.csv
       Columns: cell_id, slot_id, throughput_slot, baseline, drop_ratio, anomaly, confidence

4. CLUSTERING
   └── Clustering/outputs/relative_fronthaul_groups.csv
       Columns: cell_id, relative_group, group_color

5. SIMILARITY MATRIX
   └── Clustering/outputs/similarity_matrix.csv
       Format: cell_id × cell_id correlation matrix
```

---

## 4. ML Pipeline Details

### 4.1 Anomaly Detection Algorithm

```python
# Algorithm: Rolling Baseline Comparison

1. For each cell:
   a. Sort data by slot_id
   b. Calculate rolling median (window=100 slots)
   c. Compute drop_ratio = (baseline - actual) / baseline
   d. Flag anomaly if drop_ratio > 30%
   e. Confidence = min(1.0, (drop_ratio - 0.30) / 0.30)

2. Aggregate per cell:
   a. anomaly_rate = mean(anomaly flags)
   b. If anomaly_rate > 25%, flag cell as anomalous
```

### 4.2 Topology Clustering Algorithm

```python
# Algorithm: Hierarchical Clustering on Congestion Correlation

1. Build congestion event matrix:
   - For each cell, mark slots where throughput < 10th percentile
   
2. Calculate Z-score normalized correlation:
   - Pearson correlation on congestion patterns
   - Cells with similar congestion = likely shared infrastructure
   
3. Apply hierarchical clustering:
   - Linkage: average
   - Distance threshold: optimized for distinct groups
   
4. Assign group colors for visualization
```

### 4.3 Configurable Thresholds

| Parameter | Default | Location | Description |
|-----------|---------|----------|-------------|
| `WINDOW` | 100 | ML/step2_detect_anomalies.py | Rolling window size |
| `DROP_RATIO` | 0.30 | ML/step2_detect_anomalies.py | Throughput drop threshold |
| `ANOMALY_THRESHOLD` | 0.25 | visualization/plot_topology_graph.py | Cell-level flag threshold |

---

## 5. API Reference

### 5.1 Core Endpoints

| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/v1/api/cells` | GET | - | `{cells: [{id, name, group, isAnomaly, confidence}]}` |
| `/v1/api/topology-groups` | GET | - | `{groups: [{id, name, color, cells}]}` |
| `/v1/api/similarity-matrix` | GET | - | `{matrix: [[float]], cellIds: [string]}` |
| `/v1/api/insights` | GET | - | `{insights: [{id, type, message}]}` |
| `/v1/api/recommendations` | GET | - | `{recommendations: [{id, type, title, description}]}` |

### 5.2 LLM Endpoints

| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/v1/api/chat` | POST | `{message: string}` | `{response: string}` |
| `/v1/api/recommendation-expand` | POST | `{rec_id, title, type}` | `{detailed_description, steps[], impact, priority}` |
| `/v1/api/generate-insights` | POST | - | `{insights: [...]}` (triggers LLM) |

---

## 6. Frontend Components

### 6.1 Component Hierarchy

```
App
├── Header
├── ViewTabs (Topology | Heatmap | Propagation)
├── MainVisualization
│   ├── TopologyGraph (force-directed D3 graph)
│   ├── InteractiveHeatmap (correlation matrix)
│   └── PropagationFlow (animated SVG)
├── LeftRail
│   ├── DataInput (file upload)
│   ├── QuickMetrics (cells, groups, anomalies)
│   └── TopologyGroups (group list)
├── BottomPanel
│   ├── IntelligenceInsights (LLM-generated)
│   ├── Recommendations (clickable cards)
│   └── DetectedAnomalies (cell chips)
├── FloatingChatbot (LLM chat interface)
└── Footer
```

### 6.2 State Management (Zustand)

```typescript
interface NetworkStore {
  // Data
  cells: CellData[]
  topologyGroups: TopologyGroup[]
  insights: Insight[]
  similarityMatrix: number[][]
  
  // UI State
  currentView: 'topology' | 'heatmap' | 'propagation'
  highlightMode: 'anomaly' | 'correlation' | null
  selectedCell: string | null
  
  // Actions
  fetchData: () => Promise<void>
  highlightAnomalyCells: (cellId: string) => void
  clearHighlights: () => void
}
```

---

## 7. Deployment

### 7.1 Development

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd Frontend
npm run dev

# Terminal 3: Ollama
ollama serve
```

### 7.2 Production (Future)

| Component | Deployment Option |
|-----------|-------------------|
| Frontend | Vercel, Netlify, or static hosting |
| Backend | Docker container on Kubernetes |
| Ollama | GPU server with NVIDIA drivers |
| Database | PostgreSQL for persistence (future) |

---

## 8. Future Roadmap

### v1.1 (Planned)
- [ ] Real-time data streaming (WebSocket)
- [ ] Historical trend analysis
- [ ] Alert notifications (email/Slack)

### v1.2 (Planned)
- [ ] Multi-tenant support
- [ ] Custom threshold per cell type
- [ ] Export reports (PDF/Excel)

### v2.0 (Vision)
- [ ] Predictive anomaly detection
- [ ] Auto-remediation actions
- [ ] Integration with OSS/BSS systems

---

## 9. Glossary

| Term | Definition |
|------|------------|
| **Fronthaul** | Network segment between radio unit (RU) and distributed unit (DU) |
| **Cell** | A single radio transmitter/receiver unit |
| **Topology Group** | Cells sharing common fronthaul infrastructure |
| **Anomaly** | Significant throughput drop from baseline |
| **Congestion** | Network performance degradation due to overload |
| **Propagation** | Spread of congestion from one group to another |

---

*Document maintained by the Network Intelligence Team*
