import { useNetworkStore } from '../store/networkStore';
import { useState, useEffect } from 'react';

interface Recommendation {
    id: string;
    type: string;
    title: string;
    description: string;
}

interface RecommendationDetail {
    rec_id: string;
    title: string;
    type: string;
    detailed_description: string;
    steps: string[];
    impact: string;
    priority: string;
}

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

// Enhanced Modal with LLM details
function RecommendationModal({
    rec,
    onClose
}: {
    rec: Recommendation | null;
    onClose: () => void
}) {
    const [detail, setDetail] = useState<RecommendationDetail | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (rec) {
            setLoading(true);
            fetch('http://localhost:8000/v1/api/recommendation-expand', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rec_id: rec.id, title: rec.title, type: rec.type })
            })
                .then(res => res.json())
                .then(data => {
                    setDetail(data);
                    setLoading(false);
                })
                .catch(() => {
                    setDetail({
                        rec_id: rec.id,
                        title: rec.title,
                        type: rec.type,
                        detailed_description: rec.description,
                        steps: ["Review affected cells", "Check network logs", "Apply changes"],
                        impact: "Improved network health",
                        priority: "MEDIUM"
                    });
                    setLoading(false);
                });
        }
    }, [rec]);

    if (!rec) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <div className={`rec-badge ${rec.type}`}>
                        {rec.type.toUpperCase()}
                    </div>
                    <span className={`priority-badge ${detail?.priority?.toLowerCase() || 'medium'}`}>
                        {detail?.priority || 'LOADING'}
                    </span>
                    <button className="modal-close" onClick={onClose}>×</button>
                </div>

                <h3 className="modal-title">{rec.title}</h3>

                {loading ? (
                    <div className="modal-loading">
                        <span className="loading-spinner"></span>
                        Generating detailed analysis...
                    </div>
                ) : (
                    <>
                        <p className="modal-desc">{detail?.detailed_description || rec.description}</p>

                        {detail?.steps && detail.steps.length > 0 && (
                            <div className="modal-steps">
                                <h4 className="steps-title">Action Steps</h4>
                                <ol className="steps-list">
                                    {detail.steps.map((step, i) => (
                                        <li key={i} className="step-item">
                                            <span className="step-num">{i + 1}</span>
                                            {step}
                                        </li>
                                    ))}
                                </ol>
                            </div>
                        )}

                        {detail?.impact && (
                            <div className="modal-impact">
                                <h4 className="impact-title">Expected Impact</h4>
                                <p className="impact-text">{detail.impact}</p>
                            </div>
                        )}
                    </>
                )}

                <div className="modal-actions">
                    <button className="btn-secondary" onClick={onClose}>Dismiss</button>
                    <button className="btn-primary">Apply Changes</button>
                </div>
            </div>
        </div>
    );
}

export function BottomPanel() {
    const {
        insights,
        cells,
        highlightAnomalyCells,
        highlightMode,
        clearHighlights
    } = useNetworkStore();

    const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
    const [selectedRec, setSelectedRec] = useState<Recommendation | null>(null);
    const [loading, setLoading] = useState(true);

    // Fetch recommendations on mount
    useEffect(() => {
        const fetchRecommendations = async () => {
            try {
                const res = await fetch('http://localhost:8000/v1/api/recommendations');
                if (res.ok) {
                    const data = await res.json();
                    setRecommendations(data.recommendations || []);
                }
            } catch (e) {
                console.error('Failed to fetch recommendations:', e);
            } finally {
                setLoading(false);
            }
        };
        fetchRecommendations();
    }, []);

    const anomalies = cells.filter(c => c.isAnomaly);

    const handleAnomalyClick = (cellId: string) => {
        highlightAnomalyCells(cellId);
    };

    const handleInsightClick = (insight: typeof insights[0]) => {
        if (insight.message.includes('Cell')) {
            const match = insight.message.match(/Cell\s*(\d+)/i);
            if (match) {
                highlightAnomalyCells(`cell_${match[1].padStart(2, '0')}`);
            }
        }
    };

    return (
        <div className="bottom-panel-container">
            {/* Modal for recommendation details */}
            <RecommendationModal rec={selectedRec} onClose={() => setSelectedRec(null)} />

            {/* Clear highlights button */}
            {highlightMode && (
                <div className="clear-highlights-bar">
                    <button onClick={clearHighlights} className="btn-clear-highlights">
                        <span className={`highlight-indicator ${highlightMode === 'anomaly' ? 'red' : 'yellow'}`}></span>
                        Clear Highlights
                    </button>
                </div>
            )}

            {/* Intelligence Insights */}
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
                                insight.type === 'warning' ? 'degraded' : 'healthy'}`}></span>
                            <p className="insight-text">
                                {idx === 0 ? <StreamingText text={insight.message} /> : insight.message}
                            </p>
                        </button>
                    ))}
                </div>
            </div>

            {/* Recommendations - with hover and click popup */}
            <div className="bottom-section">
                <div className="section-header">
                    <h3 className="section-title">Recommendations</h3>
                    <span className="rec-count">{recommendations.length}</span>
                </div>
                <div className="section-content recommendations-grid">
                    {loading ? (
                        <div className="rec-loading">Loading recommendations...</div>
                    ) : recommendations.length > 0 ? (
                        recommendations.map((rec) => (
                            <div
                                key={rec.id}
                                className="rec-card hoverable"
                                onClick={() => setSelectedRec(rec)}
                            >
                                <div className={`rec-badge ${rec.type}`}>
                                    {rec.type.toUpperCase()}
                                </div>
                                <div className="rec-body">
                                    <p className="rec-title">{rec.title}</p>
                                    <p className="rec-desc">{rec.description}</p>
                                </div>
                                <span className="rec-expand">→</span>
                            </div>
                        ))
                    ) : (
                        <div className="rec-card">
                            <div className="rec-badge info">INFO</div>
                            <div className="rec-body">
                                <p className="rec-title">No recommendations</p>
                                <p className="rec-desc">System is operating normally</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Detected Anomalies */}
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
                            <span className="chip-id">{anomaly.name || anomaly.id.toUpperCase()}</span>
                            <span className="chip-score" title="Confidence Score">
                                {((anomaly.confidence ?? anomaly.anomalyScore ?? 0) * 100).toFixed(0)}% conf
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
