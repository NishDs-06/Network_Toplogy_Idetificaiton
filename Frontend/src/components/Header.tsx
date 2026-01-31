import { useNetworkStore } from '../store/networkStore';

export function Header() {
    const { viewMode, isAnalyzing, analysisProgress, cells } = useNetworkStore();

    const healthyCells = cells.filter(c => !c.isAnomaly).length;
    const anomalyCells = cells.filter(c => c.isAnomaly).length;
    const totalCells = cells.length;

    return (
        <header className="header">
            {/* Logo */}
            <div className="flex items-center gap-4">
                <div className="font-mono-display text-lg tracking-tight">
                    <span className="text-[var(--text-primary)]">FRONTHAUL</span>
                    <span className="text-[var(--state-healthy)] ml-2">NET</span>
                </div>
                <div className="h-6 w-px bg-[var(--border-emphasis)]"></div>
                <span className="font-mono-data text-[11px] text-[var(--text-secondary)] uppercase tracking-wider">
                    Topology Intelligence
                </span>
            </div>

            {/* Status Indicators */}
            <div className="flex items-center gap-8">
                {/* Analysis Status */}
                {isAnalyzing && (
                    <div className="flex items-center gap-3">
                        <div className="w-24 h-1 bg-[var(--bg-tertiary)] overflow-hidden">
                            <div
                                className="h-full bg-[var(--state-healthy)] transition-all duration-300"
                                style={{ width: `${analysisProgress}%` }}
                            />
                        </div>
                        <span className="font-mono-data text-[11px] text-[var(--text-secondary)]">
                            ANALYZING...
                        </span>
                    </div>
                )}

                {/* Network Health */}
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2">
                        <span className="font-mono-data text-[11px] text-[var(--text-secondary)]">CELLS</span>
                        <span className="font-mono-ui text-sm text-[var(--text-primary)]">{totalCells}</span>
                    </div>

                    <div className="flex items-center gap-2">
                        <span className="status-dot healthy"></span>
                        <span className="font-mono-data text-[11px] text-[var(--state-healthy)]">{healthyCells}</span>
                    </div>

                    {anomalyCells > 0 && (
                        <div className="flex items-center gap-2">
                            <span className="status-dot critical"></span>
                            <span className="font-mono-data text-[11px] text-[var(--state-critical)]">{anomalyCells}</span>
                        </div>
                    )}
                </div>

                {/* View Indicator */}
                <div className="flex items-center gap-2">
                    <span className="font-mono-data text-[11px] text-[var(--text-muted)]">VIEW</span>
                    <span className="font-mono-ui text-xs text-[var(--accent-active)] uppercase">
                        {viewMode}
                    </span>
                </div>

                {/* Keyboard Hints */}
                <div className="flex items-center gap-2">
                    <span className="kbd">H</span>
                    <span className="kbd">T</span>
                    <span className="kbd">P</span>
                </div>
            </div>
        </header>
    );
}
