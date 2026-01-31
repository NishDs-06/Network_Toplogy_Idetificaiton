import { create } from 'zustand';

// Types
export interface CellData {
    id: string;
    name: string;
    group: string;
    isAnomaly: boolean;
    anomalyScore?: number;
    confidence?: number;
}

export interface TopologyGroup {
    id: string;
    name: string;
    color: string;
    cells: string[];
}

export interface PropagationEvent {
    id: string;
    sourceGroup: string;
    targetGroup: string;
    timestamp: number;
    severity: 'healthy' | 'degraded' | 'critical';
    correlation: number;
}

export interface Insight {
    id: string;
    type: 'info' | 'warning' | 'critical';
    message: string;
    timestamp: Date;
}

export type ViewMode = 'heatmap' | 'topology' | 'propagation';
export type InteractionMode = 'explore' | 'focus' | 'compare' | 'timeline';
export type HighlightColor = 'red' | 'yellow' | 'green';

export interface HighlightedCell {
    row: number;
    col: number;
    color: HighlightColor;
}

export interface DetailPopup {
    cellId: string;
    row: number;
    col: number;
    x: number;
    y: number;
    title: string;
    content: string;
    type: 'cell' | 'anomaly' | 'correlation';
}

interface NetworkState {
    // Data
    similarityMatrix: number[][];
    cellIds: string[];
    cells: CellData[];
    topologyGroups: TopologyGroup[];
    propagationEvents: PropagationEvent[];
    insights: Insight[];

    // UI State
    viewMode: ViewMode;
    interactionMode: InteractionMode;
    hoveredCell: { row: number; col: number } | null;
    selectedCells: { row: number; col: number }[];
    hoveredNode: string | null;
    selectedNode: string | null;
    isAnalyzing: boolean;
    analysisProgress: number;

    // Highlight State
    highlightedCells: HighlightedCell[];
    highlightMode: 'anomaly' | 'correlation' | null;
    detailPopup: DetailPopup | null;

    // Temporal
    currentTime: number;
    timeRange: [number, number];

    // Actions
    setViewMode: (mode: ViewMode) => void;
    setInteractionMode: (mode: InteractionMode) => void;
    setHoveredCell: (cell: { row: number; col: number } | null) => void;
    selectCell: (cell: { row: number; col: number }) => void;
    clearSelection: () => void;
    setHoveredNode: (nodeId: string | null) => void;
    setSelectedNode: (nodeId: string | null) => void;
    setAnalyzing: (analyzing: boolean, progress?: number) => void;
    setCurrentTime: (time: number) => void;
    loadData: (matrix: number[][], cellIds: string[], topology: Record<string, string>) => void;
    addInsight: (insight: Omit<Insight, 'id' | 'timestamp'>) => void;

    // Highlight Actions
    highlightAnomalyCells: (anomalyCellId: string) => void;
    highlightCorrelationCells: (cellId1: string, cellId2: string) => void;
    setHighlightedCells: (cells: HighlightedCell[]) => void;
    clearHighlights: () => void;
    setDetailPopup: (popup: DetailPopup | null) => void;
    showCellDetail: (row: number, col: number, x: number, y: number) => void;
}

// Generate demo data
const generateDemoData = () => {
    const cellIds = [
        'cell_01', 'cell_02', 'cell_03', 'cell_04', 'cell_05', 'cell_06',
        'cell_07', 'cell_08', 'cell_09', 'cell_10', 'cell_11', 'cell_12',
        'cell_13', 'cell_14', 'cell_15', 'cell_16', 'cell_17', 'cell_18',
        'cell_19', 'cell_20', 'cell_21', 'cell_22', 'cell_23', 'cell_24'
    ];

    // Generate similarity matrix with cluster patterns
    const n = cellIds.length;
    const matrix: number[][] = [];

    // Define clusters
    const clusters = [
        [0, 1, 2, 3, 4, 5],
        [6, 7, 8, 9, 10, 11],
        [12, 13, 14, 15, 16, 17],
        [18, 19, 20, 21, 22, 23]
    ];

    for (let i = 0; i < n; i++) {
        matrix[i] = [];
        for (let j = 0; j < n; j++) {
            if (i === j) {
                matrix[i][j] = 1.0;
            } else {
                // Check if same cluster
                const iCluster = clusters.findIndex(c => c.includes(i));
                const jCluster = clusters.findIndex(c => c.includes(j));

                if (iCluster === jCluster) {
                    // High similarity within cluster
                    matrix[i][j] = 0.7 + Math.random() * 0.25;
                } else {
                    // Lower similarity across clusters
                    matrix[i][j] = Math.random() * 0.3;
                }
            }
        }
    }

    // Make symmetric
    for (let i = 0; i < n; i++) {
        for (let j = i + 1; j < n; j++) {
            const avg = (matrix[i][j] + matrix[j][i]) / 2;
            matrix[i][j] = avg;
            matrix[j][i] = avg;
        }
    }

    const topologyGroups: TopologyGroup[] = [
        { id: 'link_1', name: 'Link 1', color: '#d4a574', cells: cellIds.slice(0, 6) },
        { id: 'link_2', name: 'Link 2', color: '#7aa874', cells: cellIds.slice(6, 12) },
        { id: 'link_3', name: 'Link 3', color: '#7488a8', cells: cellIds.slice(12, 18) },
        { id: 'link_4', name: 'Link 4', color: '#a87488', cells: cellIds.slice(18, 24) },
    ];

    const cells: CellData[] = cellIds.map((id, idx) => ({
        id,
        name: id.replace('_', ' ').toUpperCase(),
        group: topologyGroups[Math.floor(idx / 6)].id,
        isAnomaly: idx === 5 || idx === 17,
        anomalyScore: idx === 5 ? 0.89 : idx === 17 ? 0.76 : undefined,
    }));

    const propagationEvents: PropagationEvent[] = [
        { id: 'p1', sourceGroup: 'link_1', targetGroup: 'link_2', timestamp: 0, severity: 'degraded', correlation: 0.65 },
        { id: 'p2', sourceGroup: 'link_2', targetGroup: 'link_3', timestamp: 5, severity: 'critical', correlation: 0.82 },
        { id: 'p3', sourceGroup: 'link_1', targetGroup: 'link_3', timestamp: 8, severity: 'degraded', correlation: 0.45 },
        { id: 'p4', sourceGroup: 'link_3', targetGroup: 'link_4', timestamp: 12, severity: 'healthy', correlation: 0.33 },
    ];

    const insights: Insight[] = [
        { id: 'i1', type: 'critical', message: 'Detected anomalous congestion pattern in Cell 06 correlating with Link 1 degradation', timestamp: new Date() },
        { id: 'i2', type: 'warning', message: 'Cells 01-06 showing 78% correlation - likely share fronthaul segment', timestamp: new Date() },
        { id: 'i3', type: 'info', message: 'Topology clustering complete: 4 distinct groups identified with 94% confidence', timestamp: new Date() },
    ];

    return { matrix, cellIds, cells, topologyGroups, propagationEvents, insights };
};

const demoData = generateDemoData();

export const useNetworkStore = create<NetworkState>((set, get) => ({
    // Initial demo data
    similarityMatrix: demoData.matrix,
    cellIds: demoData.cellIds,
    cells: demoData.cells,
    topologyGroups: demoData.topologyGroups,
    propagationEvents: demoData.propagationEvents,
    insights: demoData.insights,

    // UI State
    viewMode: 'heatmap',
    interactionMode: 'explore',
    hoveredCell: null,
    selectedCells: [],
    hoveredNode: null,
    selectedNode: null,
    isAnalyzing: false,
    analysisProgress: 0,

    // Highlight State
    highlightedCells: [],
    highlightMode: null,
    detailPopup: null,

    // Temporal
    currentTime: 0,
    timeRange: [0, 15],

    // Actions
    setViewMode: (mode) => set({ viewMode: mode }),

    setInteractionMode: (mode) => set({ interactionMode: mode }),

    setHoveredCell: (cell) => set({ hoveredCell: cell }),

    selectCell: (cell) => set((state) => {
        const exists = state.selectedCells.some(
            c => c.row === cell.row && c.col === cell.col
        );
        if (exists) {
            return {
                selectedCells: state.selectedCells.filter(
                    c => c.row !== cell.row || c.col !== cell.col
                )
            };
        }
        if (state.selectedCells.length >= 2) {
            return { selectedCells: [cell] };
        }
        return { selectedCells: [...state.selectedCells, cell] };
    }),

    clearSelection: () => set({ selectedCells: [], selectedNode: null }),

    setHoveredNode: (nodeId) => set({ hoveredNode: nodeId }),

    setSelectedNode: (nodeId) => set({ selectedNode: nodeId }),

    setAnalyzing: (analyzing, progress = 0) => set({
        isAnalyzing: analyzing,
        analysisProgress: progress
    }),

    setCurrentTime: (time) => set({ currentTime: time }),

    loadData: (matrix, cellIds, topology) => {
        const groups = Object.entries(
            Object.entries(topology).reduce((acc, [cell, group]) => {
                if (!acc[group]) acc[group] = [];
                acc[group].push(cell);
                return acc;
            }, {} as Record<string, string[]>)
        ).map(([id, cells], idx) => ({
            id,
            name: id.replace('_', ' '),
            color: ['#d4a574', '#7aa874', '#7488a8', '#a87488'][idx % 4],
            cells,
        }));

        const cells: CellData[] = cellIds.map(id => ({
            id,
            name: id.replace('_', ' ').toUpperCase(),
            group: topology[id] || 'unknown',
            isAnomaly: false,
        }));

        set({
            similarityMatrix: matrix,
            cellIds,
            cells,
            topologyGroups: groups,
        });
    },

    addInsight: (insight) => set((state) => ({
        insights: [
            { ...insight, id: `i${Date.now()}`, timestamp: new Date() },
            ...state.insights,
        ],
    })),

    // Highlight Actions
    setHighlightedCells: (cells) => set({ highlightedCells: cells }),

    clearHighlights: () => set({
        highlightedCells: [],
        highlightMode: null,
        detailPopup: null
    }),

    setDetailPopup: (popup) => set({ detailPopup: popup }),

    highlightAnomalyCells: (anomalyCellId: string) => {
        const state = get();
        const cellIndex = state.cellIds.findIndex(id => id === anomalyCellId);
        if (cellIndex === -1) return;

        // Find all cells with high correlation to this anomaly (>0.5)
        const highlights: HighlightedCell[] = [];

        // Highlight the anomaly cell itself (diagonal)
        highlights.push({ row: cellIndex, col: cellIndex, color: 'red' });

        // Highlight correlated cells
        for (let i = 0; i < state.cellIds.length; i++) {
            if (i !== cellIndex) {
                const similarity = state.similarityMatrix[cellIndex]?.[i] || 0;
                if (similarity > 0.5) {
                    highlights.push({ row: cellIndex, col: i, color: 'red' });
                    highlights.push({ row: i, col: cellIndex, color: 'red' });
                }
            }
        }

        set({
            highlightedCells: highlights,
            highlightMode: 'anomaly',
            viewMode: 'heatmap' // Switch to heatmap to show highlights
        });
    },

    highlightCorrelationCells: (cellId1: string, cellId2: string) => {
        const state = get();
        const idx1 = state.cellIds.findIndex(id => id === cellId1);
        const idx2 = state.cellIds.findIndex(id => id === cellId2);

        if (idx1 === -1 || idx2 === -1) return;

        const highlights: HighlightedCell[] = [
            { row: idx1, col: idx2, color: 'yellow' },
            { row: idx2, col: idx1, color: 'yellow' },
            { row: idx1, col: idx1, color: 'yellow' },
            { row: idx2, col: idx2, color: 'yellow' },
        ];

        // Also highlight all cells in the same cluster as both cells
        for (let i = 0; i < state.cellIds.length; i++) {
            const sim1 = state.similarityMatrix[idx1]?.[i] || 0;
            const sim2 = state.similarityMatrix[idx2]?.[i] || 0;
            if (sim1 > 0.6 || sim2 > 0.6) {
                highlights.push({ row: idx1, col: i, color: 'yellow' });
                highlights.push({ row: i, col: idx1, color: 'yellow' });
            }
        }

        set({
            highlightedCells: highlights,
            highlightMode: 'correlation',
            viewMode: 'heatmap'
        });
    },

    showCellDetail: (row: number, col: number, x: number, y: number) => {
        const state = get();
        const cell1 = state.cellIds[row];
        const cell2 = state.cellIds[col];
        const value = state.similarityMatrix[row]?.[col] || 0;

        // Check if either cell is an anomaly
        const cell1Data = state.cells.find(c => c.id === cell1);
        const cell2Data = state.cells.find(c => c.id === cell2);
        const hasAnomaly = cell1Data?.isAnomaly || cell2Data?.isAnomaly;

        // Generate LLM-style analysis content
        let content = '';
        if (value > 0.8) {
            content = `Strong correlation (${(value * 100).toFixed(0)}%) indicates these cells likely share the same fronthaul segment. Traffic patterns are highly synchronized, suggesting shared infrastructure or common congestion points.`;
        } else if (value > 0.5) {
            content = `Moderate correlation (${(value * 100).toFixed(0)}%) suggests partial infrastructure overlap. These cells may share upstream components but have some independent paths.`;
        } else {
            content = `Low correlation (${(value * 100).toFixed(0)}%) indicates these cells operate on mostly independent fronthaul segments. Congestion events are unlikely to propagate between them.`;
        }

        if (hasAnomaly) {
            content += `\n\n⚠️ ANOMALY DETECTED: ${cell1Data?.isAnomaly ? cell1 : cell2} shows anomalous behavior with ${((cell1Data?.anomalyScore || cell2Data?.anomalyScore || 0) * 100).toFixed(0)}% confidence.`;
        }

        set({
            detailPopup: {
                cellId: `${cell1}-${cell2}`,
                row,
                col,
                x,
                y,
                title: `${cell1.toUpperCase()} ↔ ${cell2.toUpperCase()}`,
                content,
                type: hasAnomaly ? 'anomaly' : 'cell',
            }
        });
    },
}));

