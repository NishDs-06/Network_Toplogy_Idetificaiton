import { useNetworkStore } from '../store/networkStore';
import { useState, useEffect } from 'react';

function StreamingText({ text, speed = 30 }: { text: string; speed?: number }) {
    const [displayText, setDisplayText] = useState('');
    const [currentIndex, setCurrentIndex] = useState(0);

    useEffect(() => {
        if (currentIndex < text.length) {
            const timer = setTimeout(() => {
                setDisplayText(prev => prev + text[currentIndex]);
                setCurrentIndex(prev => prev + 1);
            }, speed);
            return () => clearTimeout(timer);
        }
    }, [currentIndex, text, speed]);

    useEffect(() => {
        setDisplayText('');
        setCurrentIndex(0);
    }, [text]);

    return (
        <span>
            {displayText}
            {currentIndex < text.length && (
                <span className="animate-pulse text-[var(--accent-active)]">▋</span>
            )}
        </span>
    );
}

export function RightPanel() {
    const { insights, cells, selectedCells, similarityMatrix, cellIds } = useNetworkStore();

    const anomalies = cells.filter(c => c.isAnomaly);

    // Get selected cell info
    const selectedInfo = selectedCells.length > 0 ? {
        row: selectedCells[0].row,
        col: selectedCells[0].col,
        value: similarityMatrix[selectedCells[0].row]?.[selectedCells[0].col],
        cell1: cellIds[selectedCells[0].row],
        cell2: cellIds[selectedCells[0].col],
    } : null;

    return (
        <aside className="right-panel">
            {/* Selected Cell Info */}
            {selectedInfo && (
                <div className="card mb-4">
                    <div className="card-header">
                        <h3 className="card-title">Selection</h3>
                        <button
                            className="text-[11px] text-[var(--text-muted)] hover:text-[var(--accent-hover)]"
                            onClick={() => useNetworkStore.getState().clearSelection()}
                        >
                            CLEAR
                        </button>
                    </div>
                    <div className="font-mono-data text-sm">
                        <span className="text-[var(--text-primary)]">{selectedInfo.cell1}</span>
                        <span className="text-[var(--text-muted)] mx-2">↔</span>
                        <span className="text-[var(--text-primary)]">{selectedInfo.cell2}</span>
                    </div>
                    <div className="mt-2">
                        <span className="text-meta">Correlation:</span>
                        <span className="font-mono-ui text-xl text-[var(--state-healthy)] ml-2">
                            {selectedInfo.value?.toFixed(3)}
                        </span>
                    </div>
                </div>
            )}

            {/* LLM Insights */}
            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Intelligence Insights</h3>
                    <div className="status-indicator">
                        <span className="status-dot healthy"></span>
                        <span className="status-dot healthy"></span>
                        <span className="status-dot inactive"></span>
                    </div>
                </div>
                <div className="flex flex-col gap-3">
                    {insights.map((insight, idx) => (
                        <div
                            key={insight.id}
                            className={`insight-card ${insight.type}`}
                        >
                            <div className="flex items-start gap-2">
                                <span className={`status-dot ${insight.type === 'critical' ? 'critical' :
                                        insight.type === 'warning' ? 'degraded' : 'healthy'
                                    }`}></span>
                                <p className="font-mono-data text-xs text-[var(--text-primary)] leading-relaxed">
                                    {idx === 0 ? <StreamingText text={insight.message} /> : insight.message}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Recommendations */}
            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Recommendations</h3>
                </div>
                <div className="flex flex-col gap-2">
                    <div className="p-3 border border-[var(--border-subtle)] bg-[var(--bg-primary)]">
                        <div className="font-mono-data text-[11px] text-[var(--text-secondary)] mb-1">
                            ACTION SUGGESTED
                        </div>
                        <p className="text-xs text-[var(--text-primary)]">
                            Investigate shared fronthaul segment between Link 1 and Link 2
                        </p>
                    </div>
                    <div className="p-3 border border-[var(--border-subtle)] bg-[var(--bg-primary)]">
                        <div className="font-mono-data text-[11px] text-[var(--text-secondary)] mb-1">
                            MONITOR
                        </div>
                        <p className="text-xs text-[var(--text-primary)]">
                            Cell 06 showing elevated anomaly scores - 89% confidence
                        </p>
                    </div>
                </div>
            </div>

            {/* Anomaly List */}
            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Detected Anomalies</h3>
                    <span className="font-mono-data text-[11px] text-[var(--state-critical)]">
                        {anomalies.length}
                    </span>
                </div>
                <div className="anomaly-list">
                    {anomalies.map(anomaly => (
                        <div key={anomaly.id} className="anomaly-item anomaly-pulse">
                            <span className="status-dot critical"></span>
                            <span className="anomaly-id">{anomaly.id.toUpperCase()}</span>
                            <span className="anomaly-score">
                                {(anomaly.anomalyScore || 0).toFixed(2)}
                            </span>
                        </div>
                    ))}
                    {anomalies.length === 0 && (
                        <div className="text-meta text-center py-4">
                            No anomalies detected
                        </div>
                    )}
                </div>
            </div>
        </aside>
    );
}
