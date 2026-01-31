import { useNetworkStore } from '../store/networkStore';
import { useState, useEffect } from 'react';

function StreamingText({ text, speed = 20 }: { text: string; speed?: number }) {
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

export function BottomPanel() {
    const {
        insights,
        cells,
        highlightAnomalyCells,
        highlightCorrelationCells,
        highlightMode,
        clearHighlights
    } = useNetworkStore();

    const anomalies = cells.filter(c => c.isAnomaly);

    const handleAnomalyClick = (cellId: string) => {
        highlightAnomalyCells(cellId);
    };

    const handleInsightClick = (insight: typeof insights[0]) => {
        if (insight.message.includes('Cell 06')) {
            highlightAnomalyCells('cell_06');
        } else if (insight.message.includes('Cells 01-06')) {
            highlightCorrelationCells('cell_01', 'cell_06');
        } else if (insight.message.includes('4 distinct groups')) {
            highlightCorrelationCells('cell_01', 'cell_07');
        }
    };

    return (
        <div className="bottom-panel-container">
            {/* Clear highlights button - show when highlights active */}
            {highlightMode && (
                <div className="clear-highlights-bar">
                    <button
                        onClick={clearHighlights}
                        className="btn-clear-highlights"
                    >
                        <span className={`highlight-indicator ${highlightMode === 'anomaly' ? 'red' : 'yellow'
                            }`}></span>
                        Clear Highlights
                    </button>
                </div>
            )}

            {/* Intelligence Insights - Full Width */}
            <div className="bottom-section">
                <div className="section-header">
                    <h3 className="section-title">Intelligence Insights</h3>
                    <div className="status-indicator">
                        <span className="status-dot healthy"></span>
                        <span className="status-dot healthy"></span>
                        <span className="status-dot inactive"></span>
                    </div>
                </div>
                <div className="section-content insights-grid">
                    {insights.map((insight, idx) => (
                        <button
                            key={insight.id}
                            onClick={() => handleInsightClick(insight)}
                            className={`insight-card ${insight.type}`}
                        >
                            <span className={`status-dot ${insight.type === 'critical' ? 'critical' :
                                insight.type === 'warning' ? 'degraded' : 'healthy'
                                }`}></span>
                            <p className="insight-text">
                                {idx === 0 ? <StreamingText text={insight.message} /> : insight.message}
                            </p>
                        </button>
                    ))}
                </div>
            </div>

            {/* Recommendations - Full Width */}
            <div className="bottom-section">
                <div className="section-header">
                    <h3 className="section-title">Recommendations</h3>
                </div>
                <div className="section-content recommendations-grid">
                    <div className="rec-card">
                        <div className="rec-badge action">ACTION</div>
                        <div className="rec-body">
                            <p className="rec-title">Investigate shared fronthaul segment</p>
                            <p className="rec-desc">Link 1 and Link 2 show 78% correlation - shared infrastructure likely causing synchronized congestion</p>
                        </div>
                    </div>
                    <div className="rec-card">
                        <div className="rec-badge monitor">MONITOR</div>
                        <div className="rec-body">
                            <p className="rec-title">Cell 06 elevated anomaly</p>
                            <p className="rec-desc">89% confidence - monitor for 15 minute window before escalation</p>
                        </div>
                    </div>
                    <div className="rec-card">
                        <div className="rec-badge info">INFO</div>
                        <div className="rec-body">
                            <p className="rec-title">Topology stable</p>
                            <p className="rec-desc">4 groups identified with 94% confidence. No structural changes detected.</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Detected Anomalies - Full Width */}
            <div className="bottom-section">
                <div className="section-header">
                    <h3 className="section-title">Detected Anomalies</h3>
                    <span className="anomaly-count">{anomalies.length}</span>
                </div>
                <div className="section-content anomalies-row">
                    {anomalies.map(anomaly => (
                        <button
                            key={anomaly.id}
                            onClick={() => handleAnomalyClick(anomaly.id)}
                            className="anomaly-chip"
                        >
                            <span className="status-dot critical"></span>
                            <span className="chip-id">{anomaly.id.toUpperCase()}</span>
                            <span className="chip-score">
                                {((anomaly.anomalyScore || 0) * 100).toFixed(0)}%
                            </span>
                        </button>
                    ))}
                    {anomalies.length === 0 && (
                        <div className="no-anomalies">No anomalies detected</div>
                    )}
                </div>
            </div>
        </div>
    );
}
