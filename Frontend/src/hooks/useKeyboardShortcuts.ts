import { useEffect, useCallback } from 'react';
import { useNetworkStore } from '../store/networkStore';

export function useKeyboardShortcuts() {
    const { setViewMode, clearSelection, interactionMode, setInteractionMode } = useNetworkStore();

    const handleKeyDown = useCallback((event: KeyboardEvent) => {
        // Ignore if user is typing in an input
        if (
            event.target instanceof HTMLInputElement ||
            event.target instanceof HTMLTextAreaElement
        ) {
            return;
        }

        switch (event.key.toLowerCase()) {
            case 'h':
                setViewMode('heatmap');
                break;
            case 't':
                setViewMode('topology');
                break;
            case 'p':
                setViewMode('propagation');
                break;
            case 'escape':
                if (interactionMode === 'focus') {
                    setInteractionMode('explore');
                }
                clearSelection();
                break;
            case 'f':
                setInteractionMode(interactionMode === 'focus' ? 'explore' : 'focus');
                break;
            case 'c':
                setInteractionMode(interactionMode === 'compare' ? 'explore' : 'compare');
                break;
        }
    }, [setViewMode, clearSelection, interactionMode, setInteractionMode]);

    useEffect(() => {
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [handleKeyDown]);
}
