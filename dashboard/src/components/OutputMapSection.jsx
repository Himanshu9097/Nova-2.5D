import React, { useState } from 'react';
import { 
  Map, 
  Layers, 
  Eye, 
  Sliders, 
  Info, 
  Maximize2,
  Sparkles,
  Grid
} from 'lucide-react';
import { useBenchmark } from '../context/BenchmarkContext';

export default function OutputMapSection() {
  const { activeDataset, isDemo } = useBenchmark();
  const [mapMode, setMapMode] = useState('adaptive'); // 'uniform' or 'adaptive'
  const [colorMode, setColorMode] = useState('elevation'); // 'elevation' or 'semantic'
  const [hoveredCell, setHoveredCell] = useState(null);

  const outputMapData = activeDataset?.output_map || {};
  const cellsSample = mapMode === 'uniform' 
    ? (outputMapData.uniform_cells_sample || [])
    : (outputMapData.adaptive_cells_sample || []);

  const totalUniformCells = outputMapData.total_uniform_cells || activeDataset?.uniform?.cells_mean || 3322;
  const totalAdaptiveCells = outputMapData.total_adaptive_cells || activeDataset?.adaptive?.cells_mean || 3560;

  // Semantic color mapping
  const semanticColors = {
    0: '#3b82f6', // Road
    1: '#10b981', // Vehicle
    2: '#f59e0b', // Pedestrian
    3: '#8b5cf6', // Wall
    4: '#ef4444'  // Noise
  };

  // Compute bounding box of sampled cells for scaling
  const minX = cellsSample.length ? Math.min(...cellsSample.map(c => c.cell_x)) : -30;
  const maxX = cellsSample.length ? Math.max(...cellsSample.map(c => c.cell_x)) : 30;
  const minY = cellsSample.length ? Math.min(...cellsSample.map(c => c.cell_y)) : -15;
  const maxY = cellsSample.length ? Math.max(...cellsSample.map(c => c.cell_y)) : 15;

  const rangeX = Math.max(1, maxX - minX);
  const rangeY = Math.max(1, maxY - minY);

  // Elevation min/max for color scale
  const minZ = cellsSample.length ? Math.min(...cellsSample.map(c => c.max_height)) : 0;
  const maxZ = cellsSample.length ? Math.max(...cellsSample.map(c => c.max_height)) : 3;
  const rangeZ = Math.max(0.1, maxZ - minZ);

  const getElevationColor = (z) => {
    const norm = Math.max(0, Math.min(1, (z - minZ) / rangeZ));
    // Color gradient from dark blue (low elevation) -> cyan -> emerald -> yellow (high elevation)
    if (norm < 0.33) {
      return `rgb(${Math.round(6 + norm * 3 * 30)}, ${Math.round(182 * norm * 3)}, 212)`;
    } else if (norm < 0.66) {
      const sub = (norm - 0.33) * 3;
      return `rgb(${Math.round(6 + sub * 10)}, ${Math.round(182 - sub * 30)}, ${Math.round(212 - sub * 100)})`;
    } else {
      const sub = (norm - 0.66) * 3;
      return `rgb(${Math.round(16 + sub * 220)}, ${Math.round(185 - sub * 30)}, 129)`;
    }
  };

  return (
    <section id="output-map" className="section-container">
      <div className="section-header">
        <div className="section-title-group">
          <div className="section-tag">
            <Map size={14} />
            Spatial Grid Visualization
          </div>
          <h2 className="section-title">
            2.5D Elevation Map Output
          </h2>
          <p className="section-desc">
            Visual inspection of generated 2.5D raster cells, maximum height elevations (Z_max), 
            and hierarchical resolution partitioning produced by the benchmark engine.
          </p>
        </div>

        <div className="map-toolbar">
          {/* Map Mode Toggle */}
          <div className="toggle-group">
            <button 
              className={`toggle-btn ${mapMode === 'uniform' ? 'active' : ''}`}
              onClick={() => setMapMode('uniform')}
            >
              Uniform Grid ({totalUniformCells.toLocaleString()} cells)
            </button>
            <button 
              className={`toggle-btn ${mapMode === 'adaptive' ? 'active' : ''}`}
              onClick={() => setMapMode('adaptive')}
            >
              Adaptive Grid ({totalAdaptiveCells.toLocaleString()} cells)
            </button>
          </div>

          {/* Color Mode Toggle */}
          <div className="toggle-group">
            <button 
              className={`toggle-btn ${colorMode === 'elevation' ? 'active' : ''}`}
              onClick={() => setColorMode('elevation')}
            >
              Elevation (Z)
            </button>
            <button 
              className={`toggle-btn ${colorMode === 'semantic' ? 'active' : ''}`}
              onClick={() => setColorMode('semantic')}
            >
              Semantic Class
            </button>
          </div>
        </div>
      </div>

      <div className="glass-card output-map-card">
        <div className="map-display-layout">
          {/* Top-Down Map Canvas/SVG Viewport */}
          <div className="map-viewport">
            <svg viewBox="0 0 700 380" className="map-svg">
              <rect width="700" height="380" fill="#060911" />

              {/* Grid axes / background guidelines */}
              <g stroke="rgba(255, 255, 255, 0.05)" strokeWidth="1">
                <line x1="350" y1="0" x2="350" y2="380" strokeDasharray="3 3" />
                <line x1="0" y1="190" x2="700" y2="190" strokeDasharray="3 3" />
              </g>

              {/* Render Cells */}
              {cellsSample.map((cell, idx) => {
                // Map coordinates to SVG 700x380
                const px = 50 + ((cell.cell_x - minX) / rangeX) * 600;
                const py = 330 - ((cell.cell_y - minY) / rangeY) * 280;

                const cellWidth = mapMode === 'adaptive' 
                  ? (cell.resolution === 0.25 ? 5 : cell.resolution === 0.5 ? 9 : 15)
                  : 8;

                const fillCol = colorMode === 'elevation'
                  ? getElevationColor(cell.max_height)
                  : (semanticColors[cell.semantic_class] || '#94a3b8');

                return (
                  <rect
                    key={idx}
                    x={px - cellWidth / 2}
                    y={py - cellWidth / 2}
                    width={cellWidth}
                    height={cellWidth}
                    fill={fillCol}
                    opacity={hoveredCell === cell ? 1 : 0.85}
                    stroke={hoveredCell === cell ? '#fff' : 'rgba(0,0,0,0.5)'}
                    strokeWidth={hoveredCell === cell ? 1.5 : 0.5}
                    rx={1}
                    onMouseEnter={() => setHoveredCell(cell)}
                    onMouseLeave={() => setHoveredCell(null)}
                    style={{ cursor: 'pointer', transition: 'all 0.1s ease' }}
                  />
                );
              })}

              {/* Vehicle / Origin Marker */}
              <circle cx="350" cy="190" r="5" fill="#06b6d4" />
              <text x="350" y="210" fill="#22d3ee" fontSize="10" fontFamily="JetBrains Mono" textAnchor="middle">
                Ego Sensor (0,0)
              </text>

              {/* Dataset Name & Cell Count overlay */}
              <text x="18" y="26" fill="#94a3b8" fontSize="11" fontFamily="JetBrains Mono">
                Dataset: {activeDataset?.dataset?.name || 'Active Scene'} • {cellsSample.length} Sampled Cells
              </text>
            </svg>
          </div>

          {/* Interactive Inspection & Legend Panel */}
          <div className="map-sidebar">
            <h3 className="sidebar-title">Cell Inspection Telemetry</h3>

            {hoveredCell ? (
              <div className="inspect-card">
                <div className="inspect-row">
                  <span>Grid Index (X, Y):</span>
                  <span className="inspect-val mono">({hoveredCell.cell_x}, {hoveredCell.cell_y})</span>
                </div>
                <div className="inspect-row">
                  <span>Resolution:</span>
                  <span className="inspect-val mono text-cyan-400">{hoveredCell.resolution}m</span>
                </div>
                <div className="inspect-row">
                  <span>Max Elevation (Z):</span>
                  <span className="inspect-val mono text-emerald-400">{hoveredCell.max_height.toFixed(2)} m</span>
                </div>
                <div className="inspect-row">
                  <span>Point Density:</span>
                  <span className="inspect-val mono">{hoveredCell.point_count} pts</span>
                </div>
                {hoveredCell.semantic_class !== null && (
                  <div className="inspect-row">
                    <span>Semantic Class:</span>
                    <span className="inspect-val mono" style={{ color: semanticColors[hoveredCell.semantic_class] }}>
                      Class {hoveredCell.semantic_class}
                    </span>
                  </div>
                )}
              </div>
            ) : (
              <div className="inspect-placeholder">
                <Eye size={20} className="text-slate-500" />
                <span>Hover over any grid cell in the viewport to inspect elevation and coordinate payload</span>
              </div>
            )}

            {/* Legend */}
            <div className="legend-box">
              <span className="legend-title">Active Color Legend ({colorMode.toUpperCase()})</span>
              {colorMode === 'elevation' ? (
                <div className="elevation-gradient-bar">
                  <div className="grad-strip"></div>
                  <div className="grad-labels">
                    <span>Min ({minZ.toFixed(1)}m)</span>
                    <span>Mid</span>
                    <span>Max ({maxZ.toFixed(1)}m)</span>
                  </div>
                </div>
              ) : (
                <div className="semantic-legend-list">
                  <div className="sem-item"><span className="sem-dot" style={{ background: '#3b82f6' }}></span> Road (0)</div>
                  <div className="sem-item"><span className="sem-dot" style={{ background: '#10b981' }}></span> Vehicle (1)</div>
                  <div className="sem-item"><span className="sem-dot" style={{ background: '#f59e0b' }}></span> Pedestrian (2)</div>
                  <div className="sem-item"><span className="sem-dot" style={{ background: '#8b5cf6' }}></span> Wall/Building (3)</div>
                  <div className="sem-item"><span className="sem-dot" style={{ background: '#ef4444' }}></span> Noise (4)</div>
                </div>
              )}
            </div>

            <div className="callout-box info" style={{ marginTop: 'auto', padding: '0.65rem 0.85rem' }}>
              <Info size={15} className="text-cyan-400" style={{ flexShrink: 0 }} />
              <div style={{ fontSize: '0.72rem' }}>
                {isDemo 
                  ? "Showing downsampled cell structure for the default baseline scene."
                  : `Showing generated 2.5D elevation cells for ${activeDataset?.dataset?.name}.`}
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .map-toolbar {
          display: flex;
          align-items: center;
          gap: 1rem;
          flex-wrap: wrap;
        }

        .toggle-group {
          display: flex;
          background: rgba(15, 23, 42, 0.7);
          border: 1px solid var(--card-border);
          border-radius: var(--radius-sm);
          padding: 2px;
        }

        .output-map-card {
          padding: 1.5rem;
        }

        .map-display-layout {
          display: grid;
          grid-template-columns: 1.8fr 1fr;
          gap: 1.5rem;
        }

        .map-viewport {
          background: #060911;
          border: 1px solid var(--card-border);
          border-radius: var(--radius-sm);
          overflow: hidden;
          box-shadow: inset 0 0 24px rgba(0,0,0,0.8);
        }

        .map-svg {
          width: 100%;
          height: auto;
          display: block;
        }

        .map-sidebar {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .sidebar-title {
          font-size: 0.95rem;
          font-weight: 700;
          color: #fff;
        }

        .inspect-card {
          background: rgba(15, 23, 42, 0.7);
          border: 1px solid var(--accent-cyan);
          border-radius: var(--radius-sm);
          padding: 0.85rem 1rem;
          display: flex;
          flex-direction: column;
          gap: 0.4rem;
        }

        .inspect-placeholder {
          background: rgba(15, 23, 42, 0.4);
          border: 1px dashed var(--card-border);
          border-radius: var(--radius-sm);
          padding: 1.25rem 1rem;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.5rem;
          text-align: center;
          font-size: 0.76rem;
          color: var(--text-muted);
        }

        .inspect-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          font-size: 0.78rem;
          color: var(--text-secondary);
        }

        .inspect-val {
          font-weight: 600;
          color: #fff;
        }

        .legend-box {
          background: rgba(15, 23, 42, 0.5);
          border: 1px solid var(--card-border);
          border-radius: var(--radius-sm);
          padding: 0.75rem 0.9rem;
        }

        .legend-title {
          font-size: 0.72rem;
          font-weight: 700;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.05em;
          display: block;
          margin-bottom: 0.45rem;
        }

        .grad-strip {
          height: 10px;
          border-radius: 4px;
          background: linear-gradient(90deg, rgb(6, 182, 212) 0%, rgb(16, 185, 129) 50%, rgb(236, 155, 129) 100%);
          margin-bottom: 0.25rem;
        }

        .grad-labels {
          display: flex;
          justify-content: space-between;
          font-family: var(--font-mono);
          font-size: 0.68rem;
          color: var(--text-muted);
        }

        .semantic-legend-list {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .sem-item {
          display: flex;
          align-items: center;
          gap: 0.35rem;
          font-size: 0.74rem;
          color: #cbd5e1;
        }

        .sem-dot {
          width: 7px;
          height: 7px;
          border-radius: 50%;
        }

        @media (max-width: 960px) {
          .map-display-layout {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </section>
  );
}
