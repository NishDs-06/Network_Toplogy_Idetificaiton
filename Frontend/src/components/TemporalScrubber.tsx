import React, { useCallback, useRef, useState, useEffect } from 'react';
import { useNetworkStore } from '../store/networkStore';

export function TemporalScrubber() {
    const { currentTime, timeRange, setCurrentTime, propagationEvents } = useNetworkStore();
    const [isDragging, setIsDragging] = useState(false);
    const [isPlaying, setIsPlaying] = useState(false);
    const trackRef = useRef<HTMLDivElement>(null);
    const playIntervalRef = useRef<number | null>(null);

    const [min, max] = timeRange;
    const progress = ((currentTime - min) / (max - min)) * 100;

    const handleMove = useCallback((clientX: number) => {
        if (!trackRef.current) return;
        const rect = trackRef.current.getBoundingClientRect();
        const percent = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
        const newTime = min + percent * (max - min);
        setCurrentTime(Math.round(newTime * 10) / 10);
    }, [min, max, setCurrentTime]);

    const handleMouseDown = (e: React.MouseEvent) => {
        setIsDragging(true);
        handleMove(e.clientX);
    };

    const handleMouseMove = useCallback((e: MouseEvent) => {
        if (isDragging) handleMove(e.clientX);
    }, [isDragging, handleMove]);

    const handleMouseUp = useCallback(() => {
        setIsDragging(false);
    }, []);

    // Add/remove global listeners
    useEffect(() => {
        if (isDragging) {
            window.addEventListener('mousemove', handleMouseMove);
            window.addEventListener('mouseup', handleMouseUp);
        }
        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
        };
    }, [isDragging, handleMouseMove, handleMouseUp]);

    // Play/pause
    const togglePlay = () => {
        if (isPlaying) {
            if (playIntervalRef.current) {
                clearInterval(playIntervalRef.current);
                playIntervalRef.current = null;
            }
            setIsPlaying(false);
        } else {
            setIsPlaying(true);
            playIntervalRef.current = window.setInterval(() => {
                const state = useNetworkStore.getState();
                const next = state.currentTime + 0.5;
                if (next >= max) {
                    if (playIntervalRef.current) clearInterval(playIntervalRef.current);
                    setIsPlaying(false);
                    state.setCurrentTime(min);
                } else {
                    state.setCurrentTime(next);
                }
            }, 200);
        }
    };

    // Get events at current time
    const activeEvents = propagationEvents.filter(
        e => e.timestamp <= currentTime && e.timestamp + 3 >= currentTime
    );

    return (
        <div className="temporal-scrubber p-4 bg-[var(--bg-secondary)] border-t border-[var(--border-subtle)]">
            <div className="flex items-center gap-4">
                {/* Play/Pause Button */}
                <button
                    onClick={togglePlay}
                    className="w-8 h-8 flex items-center justify-center border border-[var(--border-emphasis)] hover:bg-[var(--accent-hover)] hover:border-[var(--accent-hover)] hover:text-[var(--bg-primary)] transition-all"
                >
                    {isPlaying ? (
                        <svg width="10" height="12" viewBox="0 0 10 12" fill="currentColor">
                            <rect x="0" y="0" width="3" height="12" />
                            <rect x="7" y="0" width="3" height="12" />
                        </svg>
                    ) : (
                        <svg width="12" height="14" viewBox="0 0 12 14" fill="currentColor">
                            <polygon points="0,0 12,7 0,14" />
                        </svg>
                    )}
                </button>

                {/* Time Display */}
                <div className="font-mono-ui text-sm text-[var(--accent-active)] min-w-[60px]">
                    {currentTime.toFixed(1)}ms
                </div>

                {/* Track */}
                <div
                    ref={trackRef}
                    className="flex-1 h-2 bg-[var(--bg-tertiary)] cursor-pointer relative"
                    onMouseDown={handleMouseDown}
                >
                    {/* Event markers */}
                    {propagationEvents.map(event => (
                        <div
                            key={event.id}
                            className="absolute top-0 h-full w-1"
                            style={{
                                left: `${((event.timestamp - min) / (max - min)) * 100}%`,
                                backgroundColor: event.severity === 'critical' ? 'var(--state-critical)' :
                                    event.severity === 'degraded' ? 'var(--state-degraded)' : 'var(--text-muted)',
                                opacity: activeEvents.includes(event) ? 1 : 0.3,
                            }}
                        />
                    ))}

                    {/* Progress fill */}
                    <div
                        className="absolute left-0 top-0 h-full bg-[var(--accent-active)] pointer-events-none"
                        style={{ width: `${progress}%` }}
                    />

                    {/* Handle */}
                    <div
                        className={`
                            absolute top-1/2 -translate-y-1/2 w-4 h-4
                            border-2 border-[var(--accent-active)] bg-[var(--bg-primary)]
                            pointer-events-none transition-transform
                            ${isDragging ? 'scale-125' : ''}
                        `}
                        style={{ left: `calc(${progress}% - 8px)` }}
                    />
                </div>

                {/* End time */}
                <div className="font-mono-data text-[11px] text-[var(--text-muted)]">
                    {max}ms
                </div>
            </div>

            {/* Active events indicator */}
            {activeEvents.length > 0 && (
                <div className="mt-2 flex gap-2">
                    {activeEvents.map(event => (
                        <span
                            key={event.id}
                            className="font-mono-data text-[10px] px-2 py-0.5"
                            style={{
                                backgroundColor: event.severity === 'critical' ? 'rgba(255, 59, 48, 0.2)' :
                                    event.severity === 'degraded' ? 'rgba(255, 149, 0, 0.2)' : 'transparent',
                                color: event.severity === 'critical' ? 'var(--state-critical)' :
                                    event.severity === 'degraded' ? 'var(--state-degraded)' : 'var(--text-secondary)',
                                border: '1px solid currentColor',
                            }}
                        >
                            {event.sourceGroup.toUpperCase()} → {event.targetGroup.toUpperCase()}
                        </span>
                    ))}
                </div>
            )}
        </div>
    );
}
