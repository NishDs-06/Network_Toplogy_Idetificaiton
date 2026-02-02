import { useNetworkStore } from '../store/networkStore';
import { useRef, useState, useCallback } from 'react';

export function LeftRail() {
    const {
        topologyGroups,
        cells,
        isAnalyzing,
        setAnalyzing
    } = useNetworkStore();

    const fileInputRef = useRef<HTMLInputElement>(null);
    const [isDragOver, setIsDragOver] = useState(false);

    const handleUploadClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            // Simulate analysis
            setAnalyzing(true, 0);
            let progress = 0;
            const interval = setInterval(() => {
                progress += 10;
                setAnalyzing(true, progress);
                if (progress >= 100) {
                    clearInterval(interval);
                    setAnalyzing(false, 100);
                }
            }, 300);
        }
    }, [setAnalyzing]);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragOver(true);
    };

    const handleDragLeave = () => {
        setIsDragOver(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragOver(false);
        // Handle file drop
    };

    return (
        <aside className="left-rail">
            {/* Upload Section */}
            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Data Input</h3>
                </div>
                <div
                    className={`upload-zone ${isDragOver ? 'dragover' : ''}`}
                    onClick={handleUploadClick}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                >
                    <div className="font-mono-data text-[11px] text-[var(--text-secondary)] mb-2">
                        DROP CSV FILE
                    </div>
                    <div className="text-meta">
                        or click to browse
                    </div>
                </div>
                <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv"
                    className="hidden"
                    onChange={handleFileChange}
                />
            </div>

            {/* Quick Metrics */}
            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Quick Metrics</h3>
                </div>
                <div className="metric">
                    <span className="metric-label">Total Cells</span>
                    <span className="metric-value">{cells.length}</span>
                </div>
                <div className="metric">
                    <span className="metric-label">Groups Detected</span>
                    <span className="metric-value healthy">{topologyGroups.length}</span>
                </div>
                <div className="metric">
                    <span className="metric-label">Anomalies</span>
                    <span className="metric-value critical">
                        {cells.filter(c => c.isAnomaly).length}
                    </span>
                </div>
                <div className="metric">
                    <span className="metric-label">Confidence</span>
                    <span className="metric-value">
                        {cells.length > 0
                            ? Math.round((1 - cells.filter(c => c.isAnomaly).length / cells.length) * 100)
                            : 0}%
                    </span>
                </div>
            </div>

            {/* Topology Groups */}
            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Topology Groups</h3>
                </div>
                <div className="flex flex-col gap-2">
                    {topologyGroups.map(group => (
                        <div
                            key={group.id}
                            className="flex items-center gap-3 p-2 bg-[var(--bg-primary)] border border-[var(--border-subtle)]"
                        >
                            <div
                                className="w-3 h-3"
                                style={{ backgroundColor: group.color }}
                            />
                            <span className="font-mono-data text-xs text-[var(--text-primary)]">
                                {group.name.toUpperCase()}
                            </span>
                            <span className="font-mono-data text-[11px] text-[var(--text-muted)] ml-auto">
                                {group.cells.length} cells
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Analysis Status */}
            {isAnalyzing && (
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Analysis Status</h3>
                        <span className="status-dot healthy"></span>
                    </div>
                    <div className="font-mono-data text-xs text-[var(--text-secondary)]">
                        Processing congestion data...
                    </div>
                </div>
            )}
        </aside>
    );
}
