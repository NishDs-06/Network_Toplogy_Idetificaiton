import { useCallback, useEffect, useRef, useMemo, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import type { NodeObject, LinkObject } from 'react-force-graph-2d';
import { useNetworkStore } from '../store/networkStore';

interface GraphNode extends NodeObject {
    id: string;
    group: string;
    color: string;
    isAnomaly: boolean;
    anomalyScore?: number;
    x?: number;
    y?: number;
}

interface GraphLink extends LinkObject {
    source: string | GraphNode;
    target: string | GraphNode;
    value: number;
}

export function TopologyGraph() {
    const graphRef = useRef<any>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

    const {
        cells,
        topologyGroups,
        similarityMatrix,
        cellIds,
        hoveredNode,
        selectedNode,
        setHoveredNode,
        setSelectedNode
    } = useNetworkStore();

    // Track container dimensions
    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;

        const updateDimensions = () => {
            const rect = container.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0) {
                setDimensions({ width: rect.width, height: rect.height });
            }
        };

        // Initial measurement with delay for layout
        setTimeout(updateDimensions, 100);

        // Use ResizeObserver for dynamic updates
        const resizeObserver = new ResizeObserver(updateDimensions);
        resizeObserver.observe(container);

        return () => resizeObserver.disconnect();
    }, []);

    // Build graph data
    const graphData = useMemo(() => {
        const nodes: GraphNode[] = cells.map(cell => {
            const group = topologyGroups.find(g => g.id === cell.group);
            return {
                id: cell.id,
                group: cell.group,
                color: group?.color || '#7488a8',
                isAnomaly: cell.isAnomaly,
                anomalyScore: cell.anomalyScore,
            };
        });

        const links: GraphLink[] = [];
        const threshold = 0.5; // Only show links above threshold

        for (let i = 0; i < cellIds.length; i++) {
            for (let j = i + 1; j < cellIds.length; j++) {
                const value = similarityMatrix[i]?.[j];
                if (value && value > threshold) {
                    links.push({
                        source: cellIds[i],
                        target: cellIds[j],
                        value,
                    });
                }
            }
        }

        return { nodes, links };
    }, [cells, topologyGroups, similarityMatrix, cellIds]);

    // Custom node renderer
    const paintNode = useCallback((node: GraphNode, ctx: CanvasRenderingContext2D, globalScale: number) => {
        const isHovered = hoveredNode === node.id;
        const isSelected = selectedNode === node.id;
        const baseSize = node.isAnomaly ? 10 : 7;
        const size = isHovered || isSelected ? baseSize * 1.4 : baseSize;

        // Draw node circle
        ctx.beginPath();
        ctx.arc(node.x!, node.y!, size, 0, 2 * Math.PI);

        // Fill
        ctx.fillStyle = node.color;
        if (!isHovered && !isSelected && hoveredNode) {
            ctx.globalAlpha = 0.3;
        }
        ctx.fill();
        ctx.globalAlpha = 1;

        // Border
        if (node.isAnomaly) {
            ctx.strokeStyle = '#ff3b30';
            ctx.lineWidth = 2;
            ctx.setLineDash([3, 2]);
            ctx.stroke();
            ctx.setLineDash([]);

            // Anomaly glow
            const time = Date.now() / 1000;
            const glowIntensity = 0.4 + 0.4 * Math.sin(time * 2);
            ctx.shadowColor = `rgba(255, 59, 48, ${glowIntensity})`;
            ctx.shadowBlur = 12;
            ctx.beginPath();
            ctx.arc(node.x!, node.y!, size, 0, 2 * Math.PI);
            ctx.stroke();
            ctx.shadowBlur = 0;
        } else if (isHovered || isSelected) {
            ctx.strokeStyle = isSelected ? '#00d9a3' : '#ffd60a';
            ctx.lineWidth = 2;
            ctx.stroke();
        } else {
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
            ctx.lineWidth = 1;
            ctx.stroke();
        }

        // Label
        if (isHovered || isSelected || globalScale > 1.5) {
            ctx.font = `${10 / globalScale}px "IBM Plex Mono", monospace`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'bottom';
            ctx.fillStyle = isSelected ? '#00d9a3' : isHovered ? '#ffd60a' : '#e8e8e8';
            ctx.fillText(node.id.slice(-2), node.x!, node.y! - size - 4);

            if (node.isAnomaly && node.anomalyScore) {
                ctx.fillStyle = '#ff3b30';
                ctx.fillText(`${(node.anomalyScore * 100).toFixed(0)}%`, node.x!, node.y! - size - 16);
            }
        }
    }, [hoveredNode, selectedNode]);

    // Custom link renderer
    const paintLink = useCallback((link: GraphLink, ctx: CanvasRenderingContext2D, globalScale: number) => {
        const source = link.source as GraphNode;
        const target = link.target as GraphNode;

        const isHighlighted =
            hoveredNode === source.id ||
            hoveredNode === target.id ||
            selectedNode === source.id ||
            selectedNode === target.id;

        const opacity = isHighlighted ? 0.8 : (hoveredNode ? 0.1 : 0.3);
        const width = 1 + link.value * 3;

        ctx.beginPath();
        ctx.moveTo(source.x!, source.y!);
        ctx.lineTo(target.x!, target.y!);

        ctx.strokeStyle = source.color;
        ctx.globalAlpha = opacity;
        ctx.lineWidth = width / globalScale;
        ctx.stroke();
        ctx.globalAlpha = 1;
    }, [hoveredNode, selectedNode]);

    // Center on mount
    useEffect(() => {
        if (graphRef.current && dimensions.width > 0) {
            setTimeout(() => {
                graphRef.current?.zoomToFit(400, 50);
            }, 500);
        }
    }, [dimensions]);

    // Handle node interactions
    const handleNodeHover = useCallback((node: GraphNode | null) => {
        setHoveredNode(node?.id || null);
        if (containerRef.current) {
            containerRef.current.style.cursor = node ? 'pointer' : 'grab';
        }
    }, [setHoveredNode]);

    const handleNodeClick = useCallback((node: GraphNode) => {
        setSelectedNode(selectedNode === node.id ? null : node.id);
        if (graphRef.current) {
            graphRef.current.centerAt(node.x, node.y, 500);
            graphRef.current.zoom(2, 500);
        }
    }, [selectedNode, setSelectedNode]);

    const handleBackgroundClick = useCallback(() => {
        setSelectedNode(null);
    }, [setSelectedNode]);

    // Don't render if no data
    if (cells.length === 0) {
        return (
            <div className="viz-container topology flex items-center justify-center">
                <div className="text-center">
                    <div className="font-mono-data text-[var(--text-muted)] mb-2">No topology data available</div>
                    <div className="text-[var(--text-secondary)] text-sm">Upload network data to visualize topology</div>
                </div>
            </div>
        );
    }

    return (
        <div
            ref={containerRef}
            className="viz-container topology"
            style={{ width: '100%', height: '100%', position: 'relative' }}
        >
            <ForceGraph2D
                ref={graphRef}
                graphData={graphData}
                width={dimensions.width}
                height={dimensions.height}
                nodeCanvasObject={paintNode}
                linkCanvasObject={paintLink}
                nodeCanvasObjectMode={() => 'replace'}
                linkCanvasObjectMode={() => 'replace'}
                onNodeHover={handleNodeHover}
                onNodeClick={handleNodeClick}
                onBackgroundClick={handleBackgroundClick}
                backgroundColor="#0a0a0a"
                linkDirectionalParticles={0}
                d3VelocityDecay={0.3}
                d3AlphaDecay={0.02}
                cooldownTicks={100}
                warmupTicks={100}
                enableNodeDrag={true}
                enableZoomPanInteraction={true}
            />

            {/* Legend */}
            <div
                className="absolute bottom-4 left-4 flex flex-col gap-2 p-3"
                style={{ backgroundColor: 'rgba(22, 22, 22, 0.9)', border: '1px solid var(--border-subtle)' }}
            >
                <div className="font-mono-data text-[10px] text-[var(--text-muted)] uppercase tracking-wider mb-1">
                    Topology Groups
                </div>
                {topologyGroups.map(group => (
                    <div key={group.id} className="flex items-center gap-2">
                        <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: group.color }}
                        />
                        <span className="font-mono-data text-[11px] text-[var(--text-secondary)]">
                            {group.name}
                        </span>
                    </div>
                ))}
                <div className="flex items-center gap-2 mt-1 pt-1 border-t border-[var(--border-subtle)]">
                    <div
                        className="w-3 h-3 rounded-full border-2 border-dashed"
                        style={{ borderColor: '#ff3b30' }}
                    />
                    <span className="font-mono-data text-[11px] text-[var(--state-critical)]">
                        Anomaly
                    </span>
                </div>
            </div>
        </div>
    );
}
