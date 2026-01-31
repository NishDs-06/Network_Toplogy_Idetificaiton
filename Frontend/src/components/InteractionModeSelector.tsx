import { useNetworkStore, type InteractionMode } from '../store/networkStore';

const modes: { id: InteractionMode; label: string; shortcut: string; description: string }[] = [
    { id: 'explore', label: 'EXPLORE', shortcut: '', description: 'Pan & zoom freely' },
    { id: 'focus', label: 'FOCUS', shortcut: 'F', description: 'Fullscreen viz' },
    { id: 'compare', label: 'COMPARE', shortcut: 'C', description: 'Side-by-side' },
    { id: 'timeline', label: 'TIMELINE', shortcut: '', description: 'Temporal view' },
];

export function InteractionModeSelector() {
    const { interactionMode, setInteractionMode } = useNetworkStore();

    return (
        <div className="flex items-center gap-1 p-1 bg-[var(--bg-tertiary)] border border-[var(--border-subtle)]">
            {modes.map(mode => (
                <button
                    key={mode.id}
                    onClick={() => setInteractionMode(mode.id)}
                    className={`
                        relative px-3 py-1.5 font-mono-data text-[10px] uppercase tracking-wider
                        transition-all duration-150 group
                        ${interactionMode === mode.id
                            ? 'bg-[var(--accent-active)] text-[var(--bg-primary)]'
                            : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-primary)]'
                        }
                    `}
                    title={mode.description}
                >
                    <span>{mode.label}</span>
                    {mode.shortcut && (
                        <span className={`
                            ml-1.5 text-[8px] px-1 border
                            ${interactionMode === mode.id
                                ? 'border-[var(--bg-secondary)] opacity-60'
                                : 'border-[var(--border-emphasis)]'
                            }
                        `}>
                            {mode.shortcut}
                        </span>
                    )}

                    {/* Tooltip */}
                    <div className="
                        absolute bottom-full left-1/2 -translate-x-1/2 mb-2
                        px-2 py-1 bg-black/95 text-[var(--text-primary)]
                        text-[10px] whitespace-nowrap
                        opacity-0 group-hover:opacity-100 transition-opacity duration-150
                        pointer-events-none z-50
                        border border-[var(--border-emphasis)]
                    ">
                        {mode.description}
                        <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-black" />
                    </div>
                </button>
            ))}
        </div>
    );
}
