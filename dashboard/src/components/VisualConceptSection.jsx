import React, { useState } from 'react';
import { 
  Eye, 
  Layers, 
  Car, 
  User, 
  Info, 
  Compass, 
  Sparkles,
  Sliders
} from 'lucide-react';

export default function VisualConceptSection() {
  const [conceptMode, setConceptMode] = useState('adaptive'); // 'uniform' or 'adaptive'
  const [hoveredRegion, setHoveredRegion] = useState(null);

  return (
    <section id="concept" className="section-container">
      <div className="section-header">
        <div className="section-title-group">
          <div className="section-tag">
            <Eye size={14} />
            Visual 2.5D Spatial Discretization Model
          </div>
          <h2 className="section-title">
            Conceptual 2.5D Elevation Grid Topology
          </h2>
          <p className="section-desc">
            Interactive visual simulation contrasting homogeneous spatial sampling with 
            safety-centric variable-resolution hierarchical partitioning.
          </p>
        </div>

        {/* Mode Toggle */}
        <div className="concept-mode-toggle">
          <button 
            className={`mode-btn ${conceptMode === 'uniform' ? 'active' : ''}`}
            onClick={() => setConceptMode('uniform')}
          >
            Uniform Mode (0.5m Fixed)
          </button>
          <button 
            className={`mode-btn ${conceptMode === 'adaptive' ? 'active' : ''}`}
            onClick={() => setConceptMode('adaptive')}
          >
            Adaptive Mode (0.25m - 1.0m)
          </button>
        </div>
      </div>

      <div className="glass-card visual-concept-card">
        <div className="concept-layout">
          {/* SVG Canvas Map */}
          <div className="svg-map-wrapper">
            <svg 
              viewBox="0 0 600 400" 
              className="concept-svg"
            >
              {/* Background Dark Field */}
              <rect width="600" height="400" fill="#070a12" />

              {/* Grid Lines Pattern */}
              {conceptMode === 'uniform' ? (
                /* Uniform 0.5m grid: regular 20px squares */
                <g className="uniform-grid-lines" stroke="rgba(59, 130, 246, 0.2)" strokeWidth="1">
                  {Array.from({ length: 30 }).map((_, i) => (
                    <line key={`v-${i}`} x1={i * 20} y1="0" x2={i * 20} y2="400" />
                  ))}
                  {Array.from({ length: 20 }).map((_, i) => (
                    <line key={`h-${i}`} x1="0" y1={i * 20} x2="600" y2={i * 20} />
                  ))}
                </g>
              ) : (
                /* Adaptive grid: concentric & semantic hierarchy */
                <g className="adaptive-grid-lines">
                  {/* Coarse Background (40px squares) */}
                  <g stroke="rgba(148, 163, 184, 0.12)" strokeWidth="1">
                    {Array.from({ length: 15 }).map((_, i) => (
                      <line key={`cv-${i}`} x1={i * 40} y1="0" x2={i * 40} y2="400" />
                    ))}
                    {Array.from({ length: 10 }).map((_, i) => (
                      <line key={`ch-${i}`} x1="0" y1={i * 40} x2="600" y2={i * 40} />
                    ))}
                  </g>

                  {/* Medium Range Region (radius ~180px around ego center [300, 240]) */}
                  <circle 
                    cx="300" 
                    cy="240" 
                    r="150" 
                    fill="rgba(139, 92, 246, 0.04)" 
                    stroke="rgba(139, 92, 246, 0.3)" 
                    strokeDasharray="4 4"
                  />
                  {/* Medium 20px grid inside circle */}
                  <g stroke="rgba(139, 92, 246, 0.25)" strokeWidth="1">
                    {Array.from({ length: 16 }).map((_, i) => (
                      <line key={`mv-${i}`} x1={150 + i * 20} y1="90" x2={150 + i * 20} y2="390" />
                    ))}
                    {Array.from({ length: 16 }).map((_, i) => (
                      <line key={`mh-${i}`} x1="150" y1={90 + i * 20} x2="450" y2={90 + i * 20} />
                    ))}
                  </g>

                  {/* Fine Ego Vicinity (<10m, radius ~60px around [300, 240]) */}
                  <circle 
                    cx="300" 
                    cy="240" 
                    r="60" 
                    fill="rgba(6, 182, 212, 0.08)" 
                    stroke="rgba(6, 182, 212, 0.5)" 
                  />
                  {/* Fine 10px grid */}
                  <g stroke="rgba(6, 182, 212, 0.45)" strokeWidth="1">
                    {Array.from({ length: 13 }).map((_, i) => (
                      <line key={`fv-${i}`} x1={240 + i * 10} y1="180" x2={240 + i * 10} y2="300" />
                    ))}
                    {Array.from({ length: 13 }).map((_, i) => (
                      <line key={`fh-${i}`} x1="240" y1={180 + i * 10} x2="360" y2={180 + i * 10} />
                    ))}
                  </g>

                  {/* Fine Object Cluster: Target Vehicle at [420, 190] */}
                  <rect 
                    x="390" 
                    y="160" 
                    width="60" 
                    height="60" 
                    fill="rgba(16, 185, 129, 0.12)" 
                    stroke="rgba(16, 185, 129, 0.6)" 
                  />
                  <g stroke="rgba(16, 185, 129, 0.5)" strokeWidth="1">
                    {Array.from({ length: 7 }).map((_, i) => (
                      <line key={`vv-${i}`} x1={390 + i * 10} y1="160" x2={390 + i * 10} y2="220" />
                    ))}
                    {Array.from({ length: 7 }).map((_, i) => (
                      <line key={`vh-${i}`} x1="390" y1={160 + i * 10} x2="450" y2={160 + i * 10} />
                    ))}
                  </g>

                  {/* Fine Object Cluster: Pedestrian at [200, 160] */}
                  <rect 
                    x="185" 
                    y="145" 
                    width="30" 
                    height="30" 
                    fill="rgba(245, 158, 11, 0.12)" 
                    stroke="rgba(245, 158, 11, 0.6)" 
                  />
                  <g stroke="rgba(245, 158, 11, 0.5)" strokeWidth="1">
                    {Array.from({ length: 4 }).map((_, i) => (
                      <line key={`pv-${i}`} x1={185 + i * 10} y1="145" x2={185 + i * 10} y2="175" />
                    ))}
                    {Array.from({ length: 4 }).map((_, i) => (
                      <line key={`ph-${i}`} x1="185" y1={145 + i * 10} x2="215" y2={145 + i * 10} />
                    ))}
                  </g>
                </g>
              )}

              {/* Ego Vehicle Centroid */}
              <circle cx="300" cy="240" r="8" fill="#06b6d4" />
              <text x="300" y="265" fill="#22d3ee" fontSize="11" fontFamily="JetBrains Mono" textAnchor="middle" fontWeight="bold">
                Ego Vehicle (Origin)
              </text>

              {/* Target Vehicle at [420, 190] */}
              <rect x="405" y="175" width="30" height="15" rx="3" fill="#10b981" />
              <text x="420" y="150" fill="#34d399" fontSize="10" fontFamily="JetBrains Mono" textAnchor="middle">
                Target Vehicle
              </text>

              {/* Pedestrian at [200, 160] */}
              <circle cx="200" cy="160" r="5" fill="#f59e0b" />
              <text x="200" y="138" fill="#fbbf24" fontSize="10" fontFamily="JetBrains Mono" textAnchor="middle">
                Pedestrian
              </text>

              {/* Wall Obstacle at top right */}
              <rect x="480" y="40" width="80" height="12" rx="2" fill="#8b5cf6" />
              <text x="520" y="32" fill="#a78bfa" fontSize="10" fontFamily="JetBrains Mono" textAnchor="middle">
                Wall Boundary
              </text>

              {/* Range rings legend */}
              <text x="20" y="30" fill="#94a3b8" fontSize="11" fontFamily="JetBrains Mono">
                Mode: {conceptMode === 'uniform' ? 'UNIFORM 0.50m (Homogeneous)' : 'ADAPTIVE MULTI-RESOLUTION'}
              </text>
            </svg>
          </div>

          {/* Explanation sidebar */}
          <div className="concept-sidebar">
            <h3 className="concept-side-title">
              {conceptMode === 'uniform' ? 'Uniform Discretization Behavior' : 'Adaptive Spatial Policy Behavior'}
            </h3>

            {conceptMode === 'uniform' ? (
              <div className="concept-desc-body">
                <p>
                  In fixed <strong>Uniform Grid</strong> mode, each cell has exactly the same 0.50m edge length.
                  Empty asphalt on open highway receives the exact same computational and storage budget 
                  as a complex pedestrian crossing the road.
                </p>
                <div className="concept-stat-box">
                  <div className="cs-row">
                    <span>Sampling Grain:</span>
                    <span className="cs-val text-blue-400">0.50m Everywhere</span>
                  </div>
                  <div className="cs-row">
                    <span>Ego Vicinity Resolution:</span>
                    <span className="cs-val">0.50m</span>
                  </div>
                  <div className="cs-row">
                    <span>Pedestrian Resolution:</span>
                    <span className="cs-val">0.50m</span>
                  </div>
                  <div className="cs-row">
                    <span>Far Field Resolution:</span>
                    <span className="cs-val">0.50m</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="concept-desc-body">
                <p>
                  In <strong>Adaptive Grid</strong> mode, cell density scales according to proximity and semantic importance:
                </p>
                <div className="concept-stat-box">
                  <div className="cs-row">
                    <span>Vehicle & Pedestrian:</span>
                    <span className="cs-val text-cyan-400">0.25m (High Detail)</span>
                  </div>
                  <div className="cs-row">
                    <span>Distance &lt; 10m:</span>
                    <span className="cs-val text-cyan-400">0.25m (Immediate Safety)</span>
                  </div>
                  <div className="cs-row">
                    <span>10m &le; Distance &lt; 25m:</span>
                    <span className="cs-val text-purple-400">0.50m (Medium Range)</span>
                  </div>
                  <div className="cs-row">
                    <span>Distance &ge; 25m:</span>
                    <span className="cs-val text-slate-400">1.00m (Coarse Far Field)</span>
                  </div>
                </div>
              </div>
            )}

            <div className="legend-pills-row">
              <span className="leg-pill" style={{ color: '#06b6d4' }}>● 0.25m Fine</span>
              <span className="leg-pill" style={{ color: '#8b5cf6' }}>● 0.50m Medium</span>
              <span className="leg-pill" style={{ color: '#64748b' }}>● 1.00m Coarse</span>
            </div>

            <div className="callout-box warning" style={{ marginTop: 'auto' }}>
              <Info size={16} className="text-amber-400" style={{ flexShrink: 0 }} />
              <div style={{ fontSize: '0.75rem' }}>
                <strong>Conceptual Model Notice:</strong> This interactive visualizer demonstrates the spatial concept 
                of variable-resolution partitioning. It is a schematic representation, NOT the raw CARLA 2.5D elevation render.
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .concept-mode-toggle {
          display: flex;
          background: rgba(15, 23, 42, 0.7);
          border: 1px solid var(--card-border);
          border-radius: var(--radius-sm);
          padding: 3px;
        }

        .mode-btn {
          background: transparent;
          border: none;
          color: var(--text-secondary);
          font-family: var(--font-sans);
          font-size: 0.8rem;
          font-weight: 500;
          padding: 0.4rem 0.85rem;
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .mode-btn.active {
          background: var(--accent-cyan);
          color: #070a12;
          font-weight: 700;
        }

        .visual-concept-card {
          padding: 1.5rem;
        }

        .concept-layout {
          display: grid;
          grid-template-columns: 1.6fr 1fr;
          gap: 1.5rem;
        }

        .svg-map-wrapper {
          background: #060911;
          border: 1px solid var(--card-border);
          border-radius: var(--radius-sm);
          overflow: hidden;
          box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.8);
        }

        .concept-svg {
          width: 100%;
          height: auto;
          display: block;
        }

        .concept-sidebar {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .concept-side-title {
          font-size: 1.05rem;
          font-weight: 700;
          color: #fff;
        }

        .concept-desc-body p {
          font-size: 0.84rem;
          color: var(--text-secondary);
          line-height: 1.55;
          margin-bottom: 0.85rem;
        }

        .concept-desc-body strong {
          color: #fff;
        }

        .concept-stat-box {
          background: rgba(15, 23, 42, 0.6);
          border: 1px solid var(--card-border);
          border-radius: var(--radius-sm);
          padding: 0.75rem 0.9rem;
          display: flex;
          flex-direction: column;
          gap: 0.35rem;
        }

        .cs-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          font-size: 0.78rem;
        }

        .cs-val {
          font-family: var(--font-mono);
          font-weight: 600;
        }

        .legend-pills-row {
          display: flex;
          gap: 0.85rem;
          font-family: var(--font-mono);
          font-size: 0.75rem;
        }

        @media (max-width: 960px) {
          .concept-layout {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </section>
  );
}
