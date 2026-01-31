import { useNetworkStore } from '../store/networkStore';

export function DetailPopup() {
    const { detailPopup, clearHighlights } = useNetworkStore();

    if (!detailPopup) return null;

    return (
        <div
            className="fixed z-[100] pointer-events-auto"
            style={{
                left: Math.min(detailPopup.x + 20, window.innerWidth - 360),
                top: Math.max(detailPopup.y - 20, 60),
            }}
        >
            <div
                className={`w-[340px] bg-[var(--bg-secondary)] border ${detailPopup.type === 'anomaly'
                        ? 'border-[var(--state-critical)]'
                        : 'border-[var(--border-emphasis)]'
                    } shadow-2xl`}
            >
                {/* Header */}
                <div className={`flex items-center justify-between px-4 py-3 ${detailPopup.type === 'anomaly'
                        ? 'bg-[rgba(255,59,48,0.1)]'
                        : 'bg-[var(--bg-tertiary)]'
                    } border-b border-[var(--border-subtle)]`}>
                    <div className="flex items-center gap-2">
                        {detailPopup.type === 'anomaly' && (
                            <span className="w-2 h-2 rounded-full bg-[var(--state-critical)] animate-pulse"></span>
                        )}
                        <h4 className="font-mono-display text-sm text-[var(--text-primary)]">
                            {detailPopup.title}
                        </h4>
                    </div>
                    <button
                        onClick={clearHighlights}
                        className="text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
                    >
                        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                            <path d="M1 1L13 13M1 13L13 1" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                        </svg>
                    </button>
                </div>

                {/* Content */}
                <div className="p-4">
                    <p className="font-mono-data text-xs text-[var(--text-secondary)] leading-relaxed whitespace-pre-line">
                        {detailPopup.content}
                    </p>
                </div>

                {/* Footer with correlation value */}
                <div className="px-4 py-3 border-t border-[var(--border-subtle)] flex items-center justify-between bg-[var(--bg-primary)]">
                    <span className="font-mono-data text-[10px] text-[var(--text-muted)] uppercase">
                        {detailPopup.type === 'anomaly' ? 'Anomaly Analysis' : 'Correlation Analysis'}
                    </span>
                    <span className="font-mono-data text-[10px] text-[var(--text-muted)]">
                        Click elsewhere to close
                    </span>
                </div>
            </div>
        </div>
    );
}
