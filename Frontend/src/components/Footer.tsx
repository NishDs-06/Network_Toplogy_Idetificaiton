import { useNetworkStore } from '../store/networkStore';

export function Footer() {
    const { cellIds, topologyGroups } = useNetworkStore();

    const timestamp = new Date().toISOString().replace('T', ' ').slice(0, 19);
    const batchId = `BATCH-${Date.now().toString(36).toUpperCase()}`;

    const addWatermark = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
        const watermarkText = `FRONTHAUL NET • ${timestamp} • ${batchId}`;

        ctx.save();
        ctx.font = '11px "IBM Plex Mono", monospace';
        ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
        ctx.textAlign = 'right';
        ctx.textBaseline = 'bottom';
        ctx.fillText(watermarkText, width - 16, height - 12);

        // Add logo watermark in top-left
        ctx.font = 'bold 12px "JetBrains Mono", monospace';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'top';
        ctx.fillStyle = 'rgba(0, 217, 163, 0.5)';
        ctx.fillText('FRONTHAUL', 16, 12);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
        ctx.fillText('NET', 100, 12);
        ctx.restore();
    };

    const handleExportPNG = () => {
        // Find the active canvas element
        const sourceCanvas = document.querySelector('canvas') as HTMLCanvasElement;
        if (!sourceCanvas) {
            alert('No visualization to export. Please ensure a canvas view is active.');
            return;
        }

        // Create a new canvas with watermark
        const exportCanvas = document.createElement('canvas');
        const padding = 40;
        exportCanvas.width = sourceCanvas.width + padding * 2;
        exportCanvas.height = sourceCanvas.height + padding * 2;

        const ctx = exportCanvas.getContext('2d')!;

        // Fill background
        ctx.fillStyle = '#0a0a0a';
        ctx.fillRect(0, 0, exportCanvas.width, exportCanvas.height);

        // Draw original canvas
        ctx.drawImage(sourceCanvas, padding, padding);

        // Add watermark
        addWatermark(ctx, exportCanvas.width, exportCanvas.height);

        // Download
        const link = document.createElement('a');
        link.download = `network-topology-${timestamp.replace(/[: ]/g, '-')}.png`;
        link.href = exportCanvas.toDataURL('image/png');
        link.click();
    };

    const handleExportSVG = () => {
        // Export SVG visualization
        const svg = document.querySelector('.propagation-svg') as SVGElement;
        if (svg) {
            // Clone SVG and add watermark
            const svgClone = svg.cloneNode(true) as SVGElement;

            // Create watermark group
            const watermarkGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            watermarkGroup.setAttribute('class', 'watermark');

            // Bottom-right watermark
            const watermarkText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            watermarkText.setAttribute('x', String(parseInt(svg.getAttribute('width') || '900') - 20));
            watermarkText.setAttribute('y', String(parseInt(svg.getAttribute('height') || '500') - 10));
            watermarkText.setAttribute('text-anchor', 'end');
            watermarkText.setAttribute('fill', 'rgba(255, 255, 255, 0.4)');
            watermarkText.setAttribute('font-family', "'IBM Plex Mono', monospace");
            watermarkText.setAttribute('font-size', '11');
            watermarkText.textContent = `FRONTHAUL NET • ${timestamp} • ${batchId}`;
            watermarkGroup.appendChild(watermarkText);

            // Top-left logo
            const logoText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            logoText.setAttribute('x', '20');
            logoText.setAttribute('y', '20');
            logoText.setAttribute('fill', 'rgba(0, 217, 163, 0.5)');
            logoText.setAttribute('font-family', "'JetBrains Mono', monospace");
            logoText.setAttribute('font-size', '12');
            logoText.setAttribute('font-weight', 'bold');
            logoText.textContent = 'FRONTHAUL NET';
            watermarkGroup.appendChild(logoText);

            svgClone.appendChild(watermarkGroup);

            const svgData = new XMLSerializer().serializeToString(svgClone);
            const blob = new Blob([svgData], { type: 'image/svg+xml' });
            const link = document.createElement('a');
            link.download = `network-topology-${timestamp.replace(/[: ]/g, '-')}.svg`;
            link.href = URL.createObjectURL(blob);
            link.click();
        } else {
            alert('SVG export is available only in Propagation view.');
        }
    };

    return (
        <footer className="footer">
            {/* Left: Timestamp & Batch */}
            <div className="flex items-center gap-6">
                <div className="flex items-center gap-2">
                    <span className="font-mono-data text-[11px] text-[var(--text-muted)]">TIMESTAMP</span>
                    <span className="font-mono-data text-xs text-[var(--text-secondary)]">{timestamp}</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className="font-mono-data text-[11px] text-[var(--text-muted)]">BATCH</span>
                    <span className="font-mono-data text-xs text-[var(--text-secondary)]">{batchId}</span>
                </div>
            </div>

            {/* Center: Data Summary */}
            <div className="flex items-center gap-4">
                <span className="font-mono-data text-[11px] text-[var(--text-muted)]">
                    {cellIds.length} CELLS • {topologyGroups.length} GROUPS
                </span>
            </div>

            {/* Right: Export Controls */}
            <div className="flex items-center gap-2">
                <button className="btn" onClick={handleExportPNG}>
                    EXPORT PNG
                </button>
                <button className="btn" onClick={handleExportSVG}>
                    EXPORT SVG
                </button>
            </div>
        </footer>
    );
}
