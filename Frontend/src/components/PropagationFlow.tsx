import { useMemo } from 'react';
import { useNetworkStore } from '../store/networkStore';
import * as d3 from 'd3';

export function PropagationFlow() {
    const { propagationEvents, topologyGroups, currentTime } = useNetworkStore();

    const width = 900;
    const height = 500;
    const margin = { top: 40, right: 40, bottom: 60, left: 120 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Scales
    const timeScale = useMemo(() => {
        const maxTime = Math.max(...propagationEvents.map(e => e.timestamp), 15);
        return d3.scaleLinear()
            .domain([0, maxTime])
            .range([0, innerWidth]);
    }, [propagationEvents, innerWidth]);

    const groupScale = useMemo(() => {
        return d3.scalePoint<string>()
            .domain(topologyGroups.map(g => g.id))
            .range([0, innerHeight])
            .padding(0.5);
    }, [topologyGroups, innerHeight]);

    // Generate flow paths
    const flows = useMemo(() => {
        return propagationEvents.map(event => {
            const sourceY = groupScale(event.sourceGroup) || 0;
            const targetY = groupScale(event.targetGroup) || 0;
            const startX = timeScale(event.timestamp);
            const endX = timeScale(event.timestamp + 3); // Assume 3ms propagation

            // Bezier control points
            const midX = (startX + endX) / 2;

            const path = `M ${startX} ${sourceY} 
                    C ${midX} ${sourceY}, 
                      ${midX} ${targetY}, 
                      ${endX} ${targetY}`;

            return {
                ...event,
                path,
                startX,
                endX,
                sourceY,
                targetY,
            };
        });
    }, [propagationEvents, timeScale, groupScale]);

    // Get color for severity
    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'critical': return '#ff3b30';
            case 'degraded': return '#ff9500';
            default: return '#666666';
        }
    };

    // Get stroke width from correlation
    const getStrokeWidth = (correlation: number) => {
        return 2 + correlation * 8;
    };

    return (
        <div className="viz-container" style={{ padding: '24px' }}>
            <svg
                width={width}
                height={height}
                className="propagation-svg"
                style={{ maxWidth: '100%', height: 'auto' }}
            >
                <defs>
                    {/* Flow gradients */}
                    {flows.map(flow => (
                        <linearGradient
                            key={`gradient-${flow.id}`}
                            id={`flow-gradient-${flow.id}`}
                            x1="0%"
                            y1="0%"
                            x2="100%"
                            y2="0%"
                        >
                            <stop offset="0%" stopColor={getSeverityColor(flow.severity)} stopOpacity={0.8} />
                            <stop offset="100%" stopColor={getSeverityColor(flow.severity)} stopOpacity={0.3} />
                        </linearGradient>
                    ))}

                    {/* Animated particle */}
                    <circle id="flow-particle" r="3" fill="#ffd60a" />
                </defs>

                <g transform={`translate(${margin.left}, ${margin.top})`}>
                    {/* Background grid */}
                    {/* Time axis gridlines */}
                    {timeScale.ticks(6).map(tick => (
                        <g key={`grid-${tick}`}>
                            <line
                                x1={timeScale(tick)}
                                y1={0}
                                x2={timeScale(tick)}
                                y2={innerHeight}
                                stroke="rgba(255, 255, 255, 0.04)"
                                strokeWidth={1}
                            />
                        </g>
                    ))}

                    {/* Group swimlanes */}
                    {topologyGroups.map(group => {
                        const y = groupScale(group.id) || 0;
                        return (
                            <g key={`lane-${group.id}`}>
                                {/* Lane background */}
                                <rect
                                    x={0}
                                    y={y - 30}
                                    width={innerWidth}
                                    height={60}
                                    fill="rgba(255, 255, 255, 0.02)"
                                    rx={0}
                                />

                                {/* Lane line */}
                                <line
                                    x1={0}
                                    y1={y}
                                    x2={innerWidth}
                                    y2={y}
                                    stroke="rgba(255, 255, 255, 0.1)"
                                    strokeWidth={1}
                                    strokeDasharray="4,4"
                                />

                                {/* Group node */}
                                <circle
                                    cx={0}
                                    cy={y}
                                    r={8}
                                    fill={group.color}
                                    stroke="rgba(255, 255, 255, 0.2)"
                                    strokeWidth={1}
                                />

                                {/* Group label */}
                                <text
                                    x={-16}
                                    y={y}
                                    textAnchor="end"
                                    dominantBaseline="middle"
                                    fill="#a0a0a0"
                                    fontSize={12}
                                    fontFamily="'IBM Plex Mono', monospace"
                                >
                                    {group.name.toUpperCase()}
                                </text>
                            </g>
                        );
                    })}

                    {/* Flow paths */}
                    {flows.map(flow => (
                        <g key={`flow-${flow.id}`}>
                            {/* Flow path */}
                            <path
                                d={flow.path}
                                fill="none"
                                stroke={`url(#flow-gradient-${flow.id})`}
                                strokeWidth={getStrokeWidth(flow.correlation)}
                                strokeLinecap="round"
                                opacity={flow.severity === 'critical' ? 1 : 0.7}
                            >
                                {flow.severity === 'critical' && (
                                    <animate
                                        attributeName="stroke-opacity"
                                        values="0.5;1;0.5"
                                        dur="2s"
                                        repeatCount="indefinite"
                                    />
                                )}
                            </path>

                            {/* Flow label */}
                            <text
                                x={(flow.startX + flow.endX) / 2}
                                y={(flow.sourceY + flow.targetY) / 2 - 12}
                                textAnchor="middle"
                                fill="#a0a0a0"
                                fontSize={10}
                                fontFamily="'IBM Plex Mono', monospace"
                            >
                                {flow.correlation.toFixed(2)}
                            </text>

                            {/* Timestamp marker */}
                            <circle
                                cx={flow.startX}
                                cy={flow.sourceY}
                                r={4}
                                fill={getSeverityColor(flow.severity)}
                            />

                            {/* Animated particle on critical flows */}
                            {flow.severity === 'critical' && (
                                <circle r="4" fill="#ffd60a">
                                    <animateMotion
                                        dur="2s"
                                        repeatCount="indefinite"
                                        path={flow.path}
                                    />
                                </circle>
                            )}
                        </g>
                    ))}

                    {/* Current time indicator */}
                    <g transform={`translate(${timeScale(currentTime)}, 0)`}>
                        <line
                            y1={-10}
                            y2={innerHeight + 10}
                            stroke="#ffd60a"
                            strokeWidth={2}
                            opacity={0.5}
                        />
                        <polygon
                            points="-6,-10 6,-10 0,0"
                            fill="#ffd60a"
                        />
                    </g>

                    {/* Time axis */}
                    <g transform={`translate(0, ${innerHeight + 20})`}>
                        {timeScale.ticks(6).map(tick => (
                            <g key={`tick-${tick}`} transform={`translate(${timeScale(tick)}, 0)`}>
                                <line y2={6} stroke="#666666" />
                                <text
                                    y={20}
                                    textAnchor="middle"
                                    fill="#666666"
                                    fontSize={11}
                                    fontFamily="'IBM Plex Mono', monospace"
                                >
                                    {tick}ms
                                </text>
                            </g>
                        ))}
                        <text
                            x={innerWidth / 2}
                            y={45}
                            textAnchor="middle"
                            fill="#a0a0a0"
                            fontSize={11}
                            fontFamily="'JetBrains Mono', monospace"
                            fontWeight={500}
                            letterSpacing="0.05em"
                        >
                            PROPAGATION DELAY
                        </text>
                    </g>

                    {/* Title */}
                    <text
                        x={innerWidth / 2}
                        y={-20}
                        textAnchor="middle"
                        fill="#e8e8e8"
                        fontSize={14}
                        fontFamily="'JetBrains Mono', monospace"
                        fontWeight={600}
                    >
                        CONGESTION PROPAGATION FLOW
                    </text>
                </g>

                {/* Legend */}
                <g transform={`translate(${width - 140}, ${margin.top})`}>
                    <rect
                        x={-10}
                        y={-10}
                        width={130}
                        height={90}
                        fill="rgba(22, 22, 22, 0.9)"
                        stroke="rgba(255, 255, 255, 0.06)"
                    />
                    <text
                        y={5}
                        fill="#666666"
                        fontSize={10}
                        fontFamily="'IBM Plex Mono', monospace"
                        textTransform="uppercase"
                    >
                        SEVERITY
                    </text>

                    {[
                        { label: 'CRITICAL', color: '#ff3b30' },
                        { label: 'DEGRADED', color: '#ff9500' },
                        { label: 'HEALTHY', color: '#666666' },
                    ].map((item, i) => (
                        <g key={item.label} transform={`translate(0, ${25 + i * 20})`}>
                            <line
                                x2={24}
                                stroke={item.color}
                                strokeWidth={3}
                            />
                            <text
                                x={32}
                                y={4}
                                fill="#a0a0a0"
                                fontSize={10}
                                fontFamily="'IBM Plex Mono', monospace"
                            >
                                {item.label}
                            </text>
                        </g>
                    ))}
                </g>
            </svg>
        </div>
    );
}
