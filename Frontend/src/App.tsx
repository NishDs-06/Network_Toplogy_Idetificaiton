import './index.css';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
import { useNetworkStore } from './store/networkStore';
import { Header } from './components/Header';
import { LeftRail } from './components/LeftRail';
import { RightPanel } from './components/RightPanel';
import { Footer } from './components/Footer';
import { ViewTabs } from './components/ViewTabs';
import { InteractiveHeatmap } from './components/InteractiveHeatmap';
import { PropagationFlow } from './components/PropagationFlow';
import { InteractionModeSelector } from './components/InteractionModeSelector';
import { TemporalScrubber } from './components/TemporalScrubber';
import { Suspense, lazy, useState } from 'react';

// Lazy load TopologyGraph to avoid blocking render
const TopologyGraph = lazy(() => import('./components/TopologyGraph').then(m => ({ default: m.TopologyGraph })));

function App() {
  // Enable keyboard shortcuts
  useKeyboardShortcuts();

  const { viewMode, setViewMode, interactionMode, setInteractionMode } = useNetworkStore();

  // For compare mode - track which two views to show
  const [compareViews, setCompareViews] = useState<['heatmap' | 'topology' | 'propagation', 'heatmap' | 'topology' | 'propagation']>(['heatmap', 'topology']);

  // Render a visualization based on view type
  const renderVisualization = (view: 'heatmap' | 'topology' | 'propagation', fullSize = true) => {
    const sizeClass = fullSize ? 'w-full h-full' : 'w-full h-full';

    switch (view) {
      case 'heatmap':
        return <div className={sizeClass}><InteractiveHeatmap /></div>;
      case 'topology':
        return (
          <div className={sizeClass}>
            <Suspense fallback={
              <div className="flex items-center justify-center h-full text-[var(--text-secondary)] font-mono-data">
                <div className="flex flex-col items-center gap-2">
                  <div className="w-8 h-8 border-2 border-[var(--accent-active)] border-t-transparent rounded-full animate-spin"></div>
                  <span>Loading topology...</span>
                </div>
              </div>
            }>
              <TopologyGraph />
            </Suspense>
          </div>
        );
      case 'propagation':
        return <div className={sizeClass}><PropagationFlow /></div>;
    }
  };

  // Focus mode - fullscreen overlay
  if (interactionMode === 'focus') {
    return (
      <div className="fixed inset-0 z-50 bg-[var(--bg-primary)] flex flex-col">
        {/* Focus mode header */}
        <div className="flex items-center justify-between p-4 bg-[var(--bg-secondary)] border-b border-[var(--border-subtle)]">
          <div className="flex items-center gap-4">
            <span className="font-mono-display text-lg text-[var(--accent-active)]">FOCUS MODE</span>
            <span className="font-mono-data text-sm text-[var(--text-secondary)] uppercase">{viewMode}</span>
          </div>
          <button
            onClick={() => setInteractionMode('explore')}
            className="btn flex items-center gap-2"
          >
            <span>EXIT</span>
            <span className="kbd">ESC</span>
          </button>
        </div>

        {/* Full visualization */}
        <div className="flex-1 overflow-hidden">
          {renderVisualization(viewMode)}
        </div>
      </div>
    );
  }

  // Compare mode - side by side
  if (interactionMode === 'compare') {
    return (
      <div className="fixed inset-0 z-50 bg-[var(--bg-primary)] flex flex-col">
        {/* Compare mode header */}
        <div className="flex items-center justify-between p-4 bg-[var(--bg-secondary)] border-b border-[var(--border-subtle)]">
          <div className="flex items-center gap-4">
            <span className="font-mono-display text-lg text-[var(--accent-active)]">COMPARE MODE</span>
            <div className="flex items-center gap-2">
              <select
                value={compareViews[0]}
                onChange={(e) => setCompareViews([e.target.value as any, compareViews[1]])}
                className="bg-[var(--bg-tertiary)] border border-[var(--border-emphasis)] text-[var(--text-primary)] font-mono-data text-xs p-2"
              >
                <option value="heatmap">HEATMAP</option>
                <option value="topology">TOPOLOGY</option>
                <option value="propagation">PROPAGATION</option>
              </select>
              <span className="text-[var(--text-muted)]">vs</span>
              <select
                value={compareViews[1]}
                onChange={(e) => setCompareViews([compareViews[0], e.target.value as any])}
                className="bg-[var(--bg-tertiary)] border border-[var(--border-emphasis)] text-[var(--text-primary)] font-mono-data text-xs p-2"
              >
                <option value="heatmap">HEATMAP</option>
                <option value="topology">TOPOLOGY</option>
                <option value="propagation">PROPAGATION</option>
              </select>
            </div>
          </div>
          <button
            onClick={() => setInteractionMode('explore')}
            className="btn flex items-center gap-2"
          >
            <span>EXIT</span>
            <span className="kbd">ESC</span>
          </button>
        </div>

        {/* Side by side views */}
        <div className="flex-1 flex overflow-hidden">
          <div className="flex-1 border-r border-[var(--border-subtle)] overflow-hidden">
            <div className="h-8 bg-[var(--bg-secondary)] flex items-center px-4 border-b border-[var(--border-subtle)]">
              <span className="font-mono-data text-[11px] text-[var(--text-secondary)] uppercase">{compareViews[0]}</span>
            </div>
            <div className="h-[calc(100%-2rem)]">
              {renderVisualization(compareViews[0])}
            </div>
          </div>
          <div className="flex-1 overflow-hidden">
            <div className="h-8 bg-[var(--bg-secondary)] flex items-center px-4 border-b border-[var(--border-subtle)]">
              <span className="font-mono-data text-[11px] text-[var(--text-secondary)] uppercase">{compareViews[1]}</span>
            </div>
            <div className="h-[calc(100%-2rem)]">
              {renderVisualization(compareViews[1])}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Timeline mode - propagation with scrubber
  if (interactionMode === 'timeline') {
    return (
      <div className="fixed inset-0 z-50 bg-[var(--bg-primary)] flex flex-col">
        {/* Timeline mode header */}
        <div className="flex items-center justify-between p-4 bg-[var(--bg-secondary)] border-b border-[var(--border-subtle)]">
          <div className="flex items-center gap-4">
            <span className="font-mono-display text-lg text-[var(--accent-active)]">TIMELINE MODE</span>
            <span className="font-mono-data text-sm text-[var(--text-secondary)]">Congestion Propagation Analysis</span>
          </div>
          <button
            onClick={() => setInteractionMode('explore')}
            className="btn flex items-center gap-2"
          >
            <span>EXIT</span>
            <span className="kbd">ESC</span>
          </button>
        </div>

        {/* Propagation flow */}
        <div className="flex-1 overflow-hidden">
          {renderVisualization('propagation')}
        </div>

        {/* Temporal scrubber */}
        <TemporalScrubber />
      </div>
    );
  }

  // Normal explore mode
  return (
    <div className="command-center">
      {/* Header */}
      <Header />

      {/* Left Rail */}
      <LeftRail />

      {/* Main Canvas */}
      <main className="main-canvas">
        {/* View Controls Bar */}
        <div className="flex items-center justify-between border-b border-[var(--border-subtle)]">
          <ViewTabs activeView={viewMode} onViewChange={setViewMode} />
          <div className="pr-4">
            <InteractionModeSelector />
          </div>
        </div>

        {/* Visualization Container */}
        <div className="flex-1 overflow-hidden relative">
          {renderVisualization(viewMode)}
        </div>

        {/* Temporal Scrubber - shown in propagation view */}
        {viewMode === 'propagation' && <TemporalScrubber />}
      </main>

      {/* Right Panel */}
      <RightPanel />

      {/* Footer */}
      <Footer />
    </div>
  );
}

export default App;
