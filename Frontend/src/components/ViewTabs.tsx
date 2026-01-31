import type { ViewMode } from '../store/networkStore';

interface ViewTabsProps {
    activeView: ViewMode;
    onViewChange: (view: ViewMode) => void;
}

export function ViewTabs({ activeView, onViewChange }: ViewTabsProps) {
    const tabs: { id: ViewMode; label: string; shortcut: string }[] = [
        { id: 'heatmap', label: 'HEATMAP', shortcut: 'H' },
        { id: 'topology', label: 'TOPOLOGY', shortcut: 'T' },
        { id: 'propagation', label: 'PROPAGATION', shortcut: 'P' },
    ];

    return (
        <div className="view-tabs">
            {tabs.map(tab => (
                <button
                    key={tab.id}
                    className={`view-tab ${activeView === tab.id ? 'active' : ''}`}
                    onClick={() => onViewChange(tab.id)}
                >
                    <span>{tab.label}</span>
                    <span className="kbd ml-2 text-[9px]">{tab.shortcut}</span>
                </button>
            ))}
        </div>
    );
}
