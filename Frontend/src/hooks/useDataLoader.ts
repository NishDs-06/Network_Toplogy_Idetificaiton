// Frontend/src/hooks/useDataLoader.ts
/**
 * Data Loader Hook
 * 
 * Fetches real data from the backend API and loads it into the Zustand store.
 * Call this hook in App.tsx to automatically load data on startup.
 */

import { useEffect, useState, useCallback } from 'react';
import { useNetworkStore } from '../store/networkStore';
import * as api from '../services/api';

interface LoaderState {
    isLoading: boolean;
    error: string | null;
    isConnected: boolean;
    lastUpdated: Date | null;
}

export function useDataLoader() {
    const [state, setState] = useState<LoaderState>({
        isLoading: true,
        error: null,
        isConnected: false,
        lastUpdated: null,
    });

    const loadData = useCallback(async () => {
        setState((prev: LoaderState) => ({ ...prev, isLoading: true, error: null }));

        try {
            // Check if backend is available
            const isHealthy = await api.checkHealth();
            if (!isHealthy) {
                setState((prev: LoaderState) => ({
                    ...prev,
                    isLoading: false,
                    isConnected: false,
                    error: 'Backend not available. Using demo data.',
                }));
                return;
            }

            setState((prev: LoaderState) => ({ ...prev, isConnected: true }));

            // Fetch all data in parallel
            const [matrixData, cellsData, groupsData, eventsData, insightsData] = await Promise.all([
                api.fetchSimilarityMatrix(),
                api.fetchCells(),
                api.fetchTopologyGroups(),
                api.fetchPropagationEvents(),
                api.fetchInsights(),
            ]);

            // Update the store with real data
            useNetworkStore.setState({
                similarityMatrix: matrixData.matrix,
                cellIds: matrixData.cellIds,
                cells: cellsData.cells.map(cell => ({
                    ...cell,
                    isAnomaly: cell.isAnomaly ?? false,
                    anomalyScore: cell.anomalyScore ?? undefined,
                })),
                topologyGroups: groupsData.groups,
                propagationEvents: eventsData.events.map(event => ({
                    ...event,
                    severity: event.severity as 'healthy' | 'degraded' | 'critical',
                })),
                insights: insightsData.insights.map(insight => ({
                    ...insight,
                    type: insight.type as 'info' | 'warning' | 'critical',
                    timestamp: new Date(insight.timestamp),
                })),
                timeRange: eventsData.timeRange as [number, number],
            });

            setState({
                isLoading: false,
                error: null,
                isConnected: true,
                lastUpdated: new Date(),
            });

            console.log('✅ Loaded real data from backend');
            console.log(`   - ${matrixData.cellIds.length} cells`);
            console.log(`   - ${groupsData.groups.length} topology groups`);
            console.log(`   - ${eventsData.events.length} propagation events`);

        } catch (error) {
            console.error('Failed to load data from backend:', error);
            setState({
                isLoading: false,
                error: error instanceof Error ? error.message : 'Failed to load data',
                isConnected: false,
                lastUpdated: null,
            });
        }
    }, []);

    // Load data on mount
    useEffect(() => {
        loadData();
    }, [loadData]);

    // Expose reload function
    return {
        ...state,
        reload: loadData,
    };
}
