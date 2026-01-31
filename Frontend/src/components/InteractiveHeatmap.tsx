import { useRef, useEffect, useCallback, useState } from 'react';
import * as d3 from 'd3';
import { useNetworkStore } from '../store/networkStore';

export function InteractiveHeatmap() {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [tooltipInfo, setTooltipInfo] = useState<{
        x: number;
        y: number;
        row: number;
        col: number;
        value: number;
    } | null>(null);

    const {
        similarityMatrix,
        cellIds,
        hoveredCell,
        selectedCells,
        setHoveredCell,
        selectCell
    } = useNetworkStore();

    const n = cellIds.length;
    const cellSize = Math.max(24, Math.min(32, 800 / n));
    const gap = 2;
    const labelOffset = 60;
    const totalSize = n * (cellSize + gap) + labelOffset;

    // Color scale from design tokens
    const colorScale = d3.scaleSequential()
        .domain([0, 1])
        .interpolator(d3.interpolateRgb('#1a1a2e', '#00d9a3'));

    const renderHeatmap = useCallback(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Clear
        ctx.fillStyle = '#0a0a0a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw cell labels (columns - top)
        ctx.font = '10px "IBM Plex Mono", monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';

        for (let j = 0; j < n; j++) {
            const x = labelOffset + j * (cellSize + gap) + cellSize / 2;
            const isHovered = hoveredCell?.col === j;
            const isSelected = selectedCells.some(c => c.col === j);

            ctx.fillStyle = isSelected ? '#00d9a3' : isHovered ? '#ffd60a' : '#666666';

            ctx.save();
            ctx.translate(x, labelOffset - 8);
            ctx.rotate(-Math.PI / 4);
            ctx.fillText(cellIds[j].slice(-2), 0, 0);
            ctx.restore();
        }

        // Draw cell labels (rows - left)
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';

        for (let i = 0; i < n; i++) {
            const y = labelOffset + i * (cellSize + gap) + cellSize / 2;
            const isHovered = hoveredCell?.row === i;
            const isSelected = selectedCells.some(c => c.row === i);

            ctx.fillStyle = isSelected ? '#00d9a3' : isHovered ? '#ffd60a' : '#666666';
            ctx.fillText(cellIds[i].slice(-2), labelOffset - 8, y);
        }

        // Draw heatmap cells
        for (let i = 0; i < n; i++) {
            for (let j = 0; j < n; j++) {
                const x = labelOffset + j * (cellSize + gap);
                const y = labelOffset + i * (cellSize + gap);
                const value = similarityMatrix[i][j];

                // Determine if cell should be dimmed
                const isHovered = hoveredCell?.row === i && hoveredCell?.col === j;
                const isInHoveredRowCol = hoveredCell && (hoveredCell.row === i || hoveredCell.col === j);
                const isSelected = selectedCells.some(c => c.row === i && c.col === j);
                const shouldDim = hoveredCell && !isInHoveredRowCol && !isHovered;

                // Base cell color
                ctx.fillStyle = colorScale(value);
                if (shouldDim) {
                    ctx.globalAlpha = 0.3;
                }
                ctx.fillRect(x, y, cellSize, cellSize);
                ctx.globalAlpha = 1;

                // Subtle border
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.06)';
                ctx.lineWidth = 1;
                ctx.strokeRect(x, y, cellSize, cellSize);

                // Hover/Selection highlight
                if (isHovered || isSelected) {
                    ctx.strokeStyle = isSelected ? '#00d9a3' : '#ffd60a';
                    ctx.lineWidth = 2;
                    ctx.strokeRect(x - 1, y - 1, cellSize + 2, cellSize + 2);
                }

                // Diagonal cells (self-correlation)
                if (i === j) {
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
                    ctx.beginPath();
                    ctx.moveTo(x, y);
                    ctx.lineTo(x + cellSize, y + cellSize);
                    ctx.lineTo(x, y + cellSize);
                    ctx.closePath();
                    ctx.fill();
                }
            }
        }

        // Draw row/column highlight lines for hovered cell
        if (hoveredCell) {
            const hx = labelOffset + hoveredCell.col * (cellSize + gap);
            const hy = labelOffset + hoveredCell.row * (cellSize + gap);

            ctx.strokeStyle = 'rgba(255, 214, 10, 0.3)';
            ctx.lineWidth = 1;

            // Horizontal line
            ctx.beginPath();
            ctx.moveTo(labelOffset, hy + cellSize / 2);
            ctx.lineTo(hx, hy + cellSize / 2);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(hx + cellSize, hy + cellSize / 2);
            ctx.lineTo(totalSize, hy + cellSize / 2);
            ctx.stroke();

            // Vertical line
            ctx.beginPath();
            ctx.moveTo(hx + cellSize / 2, labelOffset);
            ctx.lineTo(hx + cellSize / 2, hy);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(hx + cellSize / 2, hy + cellSize);
            ctx.lineTo(hx + cellSize / 2, totalSize);
            ctx.stroke();
        }

        // Draw color scale legend
        const legendX = totalSize + 20;
        const legendY = labelOffset;
        const legendHeight = 200;
        const legendWidth = 16;

        const gradient = ctx.createLinearGradient(legendX, legendY + legendHeight, legendX, legendY);
        gradient.addColorStop(0, '#1a1a2e');
        gradient.addColorStop(1, '#00d9a3');

        ctx.fillStyle = gradient;
        ctx.fillRect(legendX, legendY, legendWidth, legendHeight);

        ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
        ctx.strokeRect(legendX, legendY, legendWidth, legendHeight);

        // Legend labels
        ctx.font = '10px "IBM Plex Mono", monospace';
        ctx.fillStyle = '#a0a0a0';
        ctx.textAlign = 'left';
        ctx.fillText('1.0', legendX + legendWidth + 8, legendY + 4);
        ctx.fillText('0.5', legendX + legendWidth + 8, legendY + legendHeight / 2);
        ctx.fillText('0.0', legendX + legendWidth + 8, legendY + legendHeight);

    }, [similarityMatrix, cellIds, n, cellSize, colorScale, hoveredCell, selectedCells, totalSize, labelOffset]);

    // Handle mouse events
    const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;

        const x = (e.clientX - rect.left) * scaleX - labelOffset;
        const y = (e.clientY - rect.top) * scaleY - labelOffset;

        const col = Math.floor(x / (cellSize + gap));
        const row = Math.floor(y / (cellSize + gap));

        if (col >= 0 && col < n && row >= 0 && row < n && x >= 0 && y >= 0) {
            setHoveredCell({ row, col });
            setTooltipInfo({
                x: e.clientX,
                y: e.clientY,
                row,
                col,
                value: similarityMatrix[row][col],
            });
        } else {
            setHoveredCell(null);
            setTooltipInfo(null);
        }
    }, [n, cellSize, labelOffset, gap, similarityMatrix, setHoveredCell]);

    const handleMouseLeave = useCallback(() => {
        setHoveredCell(null);
        setTooltipInfo(null);
    }, [setHoveredCell]);

    const handleClick = useCallback(() => {
        if (hoveredCell) {
            selectCell(hoveredCell);
        }
    }, [hoveredCell, selectCell]);

    // Render on data or state change
    useEffect(() => {
        renderHeatmap();
    }, [renderHeatmap]);

    return (
        <div
            ref={containerRef}
            className="viz-container heatmap"
            style={{ padding: '24px' }}
        >
            <canvas
                ref={canvasRef}
                width={totalSize + 60}
                height={totalSize}
                onMouseMove={handleMouseMove}
                onMouseLeave={handleMouseLeave}
                onClick={handleClick}
                style={{
                    maxWidth: '100%',
                    maxHeight: '100%',
                    objectFit: 'contain'
                }}
            />

            {/* Tooltip */}
            {tooltipInfo && (
                <div
                    className="tooltip fade-in"
                    style={{
                        left: tooltipInfo.x + 15,
                        top: tooltipInfo.y - 10,
                        transform: 'translateY(-100%)',
                        position: 'fixed',
                    }}
                >
                    <span className="text-[var(--text-primary)]">
                        {cellIds[tooltipInfo.row]}
                    </span>
                    <span className="text-[var(--text-muted)] mx-2">↔</span>
                    <span className="text-[var(--text-primary)]">
                        {cellIds[tooltipInfo.col]}
                    </span>
                    <span className="tooltip-value">
                        {tooltipInfo.value.toFixed(3)}
                    </span>
                </div>
            )}
        </div>
    );
}
