import React, { useState } from 'react';
import { 
  Grid, 
  Layers, 
  Code, 
  CheckCircle2, 
  AlertTriangle, 
  Compass, 
  Cpu, 
  ArrowRight,
  Maximize2
} from 'lucide-react';
import { GRID_ALGORITHMS } from '../data/benchmarkData';

export default function GridMethodsSection() {
  const [activeTab, setActiveTab] = useState('both'); // 'both', 'uniform', 'adaptive'

  const u = GRID_ALGORITHMS.uniform;
  const a = GRID_ALGORITHMS.adaptive;

  return (
    <section id="grid-methods" className="section-container">
      <div className="section-header">
        <div className="section-title-group">
          <div className="section-tag">
            <Grid size={14} />
            Spatial Discretization Policies
          </div>
          <h2 className="section-title">
            Grid Representation Architectures
          </h2>
          <p className="section-desc">
            Contrasting the mathematical formulation, cell structure, indexing logic, and 
            empirical cell counts of the fixed Uniform Grid against the prototype Adaptive Grid policy.
          </p>
        </div>
      </div>

      <div className="grid-2">
        {/* UNIFORM GRID PANEL */}
        <div className="glass-card grid-method-card uniform-theme">
          <div className="method-badge-bar">
            <span className="badge badge-blue">FIXED RESOLUTION BASELINE</span>
            <span className="mono-tag">Res = {u.resolutionMeters}m</span>
          </div>

          <div className="method-title-row">
            <h3 className="method-name">{u.name}</h3>
            <div className="cell-stat">
              <span className="cell-stat-val">{u.occupiedCells.toLocaleString()}</span>
              <span className="cell-stat-lbl">Occupied Cells</span>
            </div>
          </div>

          <p className="method-summary">{u.policySummary}</p>

          {/* Code snippet / formula */}
          <div className="code-block">
            <div className="code-header">
              <Code size={13} className="text-blue-400" />
              <span>Indexing Formula</span>
            </div>
            <pre className="code-content">
{`cell_x = int(np.floor(x / 0.5))
cell_y = int(np.floor(y / 0.5))
cell_id = (cell_x, cell_y)`}
            </pre>
          </div>

          {/* Cell Payload */}
          <div className="payload-box">
            <span className="payload-title">Cell Structure Data Payload:</span>
            <ul className="payload-list">
              <li><code>points</code>: List of raw 5D LiDAR point tuples</li>
              <li><code>max_height</code>: Dynamic maximum Z elevation (float)</li>
              <li><code>semantic_classes</code>: List of integer semantic classifications</li>
            </ul>
          </div>

          {/* Visual Schematic Box */}
          <div className="schematic-box">
            <div className="schematic-label">Fixed Resolution Schematic (Uniform 0.5m)</div>
            <div className="uniform-grid-graphic">
              {Array.from({ length: 36 }).map((_, i) => (
                <div key={i} className="uniform-cell">
                  {i % 4 === 0 && <span className="cell-dot"></span>}
                </div>
              ))}
            </div>
            <div className="schematic-caption">Homogeneous 0.50m × 0.50m cell size spanning all spatial ranges</div>
          </div>

          <div className="tradeoff-grid">
            <div className="tradeoff-col pro">
              <span className="tradeoff-title">Advantages</span>
              <p>{u.pros}</p>
            </div>
            <div className="tradeoff-col con">
              <span className="tradeoff-title">Drawbacks</span>
              <p>{u.cons}</p>
            </div>
          </div>
        </div>

        {/* ADAPTIVE GRID PANEL */}
        <div className="glass-card grid-method-card adaptive-theme">
          <div className="method-badge-bar">
            <span className="badge badge-purple">PROTOTYPE ADAPTIVE HEURISTIC</span>
            <span className="badge badge-amber">Infrastructure Baseline</span>
          </div>

          <div className="method-title-row">
            <h3 className="method-name">{a.name}</h3>
            <div className="cell-stat">
              <span className="cell-stat-val text-purple-400">{a.occupiedCells.toLocaleString()}</span>
              <span className="cell-stat-lbl">Occupied Cells</span>
            </div>
          </div>

          <p className="method-summary">{a.policySummary}</p>

          {/* Policy Rules Table */}
          <div className="rules-table-wrap">
            <div className="rules-table-title">Prototype Multi-Resolution Policy Rules</div>
            <div className="rules-list">
              {a.policyRules.map((rule, idx) => (
                <div key={idx} className="rule-row">
                  <span className="rule-cond">{rule.condition}</span>
                  <ArrowRight size={13} className="text-purple-400" />
                  <span className={`rule-res res-${rule.level.toLowerCase()}`}>
                    {rule.resolution}m ({rule.level})
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Code snippet / formula */}
          <div className="code-block">
            <div className="code-header">
              <Code size={13} className="text-purple-400" />
              <span>Indexing Formula (3-Tuple Key)</span>
            </div>
            <pre className="code-content">
{`resolution = get_resolution(x, y, semantic_class)
cell_x = int(np.floor(x / resolution))
cell_y = int(np.floor(y / resolution))
cell_id = (cell_x, cell_y, resolution)`}
            </pre>
          </div>

          {/* Visual Schematic Box */}
          <div className="schematic-box">
            <div className="schematic-label">Variable Resolution Schematic (0.25m / 0.5m / 1.0m)</div>
            <div className="adaptive-grid-graphic">
              <div className="coarse-quadrant">
                <span>1.0m (Far Field)</span>
              </div>
              <div className="medium-quadrant">
                <div className="med-subcell">0.5m</div>
                <div className="med-subcell">0.5m</div>
                <div className="fine-cluster">
                  <div className="fine-subcell">0.25m</div>
                  <div className="fine-subcell">0.25m</div>
                  <div className="fine-subcell">0.25m</div>
                  <div className="fine-subcell">0.25m</div>
                </div>
                <div className="med-subcell">0.5m</div>
              </div>
            </div>
            <div className="schematic-caption">Fine 0.25m near vehicles/pedestrians; coarse 1.0m in background</div>
          </div>

          {/* Prototype disclaimer callout */}
          <div className="callout-box warning" style={{ margin: '1rem 0' }}>
            <AlertTriangle size={17} className="text-amber-400" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div style={{ fontSize: '0.8rem' }}>
              <strong>Important Prototype Notice:</strong> {a.prototypeDisclaimer}
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .grid-method-card {
          padding: 1.6rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .grid-method-card.uniform-theme {
          border-top: 3px solid var(--accent-blue);
        }

        .grid-method-card.adaptive-theme {
          border-top: 3px solid var(--accent-purple);
        }

        .method-badge-bar {
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .mono-tag {
          font-family: var(--font-mono);
          font-size: 0.75rem;
          color: var(--accent-blue);
          background: rgba(59, 130, 246, 0.1);
          border: 1px solid rgba(59, 130, 246, 0.25);
          padding: 0.15rem 0.5rem;
          border-radius: 4px;
        }

        .method-title-row {
          display: flex;
          align-items: flex-end;
          justify-content: space-between;
        }

        .method-name {
          font-size: 1.25rem;
          font-weight: 800;
          color: #fff;
        }

        .cell-stat {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
        }

        .cell-stat-val {
          font-family: var(--font-mono);
          font-size: 1.4rem;
          font-weight: 700;
          color: #fff;
          line-height: 1;
        }

        .cell-stat-lbl {
          font-size: 0.7rem;
          color: var(--text-muted);
          text-transform: uppercase;
        }

        .method-summary {
          font-size: 0.84rem;
          color: var(--text-secondary);
          line-height: 1.5;
        }

        .code-block {
          background: #090e1a;
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: var(--radius-sm);
          overflow: hidden;
        }

        .code-header {
          display: flex;
          align-items: center;
          gap: 0.4rem;
          background: rgba(255, 255, 255, 0.03);
          border-bottom: 1px solid rgba(255, 255, 255, 0.06);
          padding: 0.4rem 0.75rem;
          font-family: var(--font-mono);
          font-size: 0.72rem;
          color: var(--text-secondary);
        }

        .code-content {
          padding: 0.65rem 0.75rem;
          font-family: var(--font-mono);
          font-size: 0.75rem;
          color: #38bdf8;
          line-height: 1.45;
          margin: 0;
          white-space: pre-wrap;
        }

        .payload-box {
          background: rgba(15, 23, 42, 0.5);
          border: 1px solid var(--card-border);
          border-radius: var(--radius-sm);
          padding: 0.75rem 0.9rem;
        }

        .payload-title {
          font-size: 0.78rem;
          font-weight: 600;
          color: #cbd5e1;
          display: block;
          margin-bottom: 0.4rem;
        }

        .payload-list {
          list-style: none;
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
          font-size: 0.76rem;
          color: var(--text-secondary);
        }

        .payload-list code {
          font-family: var(--font-mono);
          color: var(--accent-cyan);
        }

        .schematic-box {
          background: #080c16;
          border: 1px solid var(--card-border);
          border-radius: var(--radius-sm);
          padding: 0.85rem;
          display: flex;
          flex-direction: column;
          align-items: center;
        }

        .schematic-label {
          font-size: 0.75rem;
          font-weight: 600;
          color: var(--text-secondary);
          margin-bottom: 0.6rem;
          align-self: flex-start;
        }

        .uniform-grid-graphic {
          display: grid;
          grid-template-columns: repeat(6, 26px);
          grid-template-rows: repeat(6, 22px);
          gap: 2px;
          margin: 0.5rem 0;
        }

        .uniform-cell {
          background: rgba(59, 130, 246, 0.15);
          border: 1px solid rgba(59, 130, 246, 0.35);
          border-radius: 2px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .cell-dot {
          width: 5px;
          height: 5px;
          background: var(--accent-cyan);
          border-radius: 50%;
        }

        .adaptive-grid-graphic {
          display: grid;
          grid-template-columns: 1fr 1fr;
          width: 170px;
          height: 140px;
          gap: 3px;
          margin: 0.5rem 0;
        }

        .coarse-quadrant {
          background: rgba(139, 92, 246, 0.1);
          border: 1px dashed rgba(139, 92, 246, 0.35);
          display: flex;
          align-items: center;
          justify-content: center;
          font-family: var(--font-mono);
          font-size: 0.65rem;
          color: #a78bfa;
          text-align: center;
          padding: 4px;
        }

        .medium-quadrant {
          display: grid;
          grid-template-columns: 1fr 1fr;
          grid-template-rows: 1fr 1fr;
          gap: 2px;
        }

        .med-subcell {
          background: rgba(139, 92, 246, 0.2);
          border: 1px solid rgba(139, 92, 246, 0.4);
          display: flex;
          align-items: center;
          justify-content: center;
          font-family: var(--font-mono);
          font-size: 0.62rem;
          color: #c4b5fd;
        }

        .fine-cluster {
          display: grid;
          grid-template-columns: 1fr 1fr;
          grid-template-rows: 1fr 1fr;
          gap: 1px;
          background: rgba(6, 182, 212, 0.2);
          border: 1px solid var(--accent-cyan);
        }

        .fine-subcell {
          background: rgba(6, 182, 212, 0.3);
          display: flex;
          align-items: center;
          justify-content: center;
          font-family: var(--font-mono);
          font-size: 0.55rem;
          color: #fff;
          font-weight: bold;
        }

        .schematic-caption {
          font-size: 0.72rem;
          color: var(--text-muted);
          margin-top: 0.5rem;
        }

        .rules-table-wrap {
          background: rgba(15, 23, 42, 0.5);
          border: 1px solid var(--card-border);
          border-radius: var(--radius-sm);
          padding: 0.75rem 0.9rem;
        }

        .rules-table-title {
          font-size: 0.78rem;
          font-weight: 600;
          color: #cbd5e1;
          margin-bottom: 0.45rem;
        }

        .rules-list {
          display: flex;
          flex-direction: column;
          gap: 0.35rem;
        }

        .rule-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          font-size: 0.74rem;
          font-family: var(--font-mono);
          padding: 0.2rem 0;
          border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        }

        .rule-cond {
          color: #e2e8f0;
        }

        .rule-res {
          padding: 0.1rem 0.4rem;
          border-radius: 4px;
          font-weight: 600;
        }

        .rule-res.res-fine {
          background: rgba(6, 182, 212, 0.2);
          color: #22d3ee;
        }

        .rule-res.res-medium {
          background: rgba(139, 92, 246, 0.2);
          color: #a78bfa;
        }

        .rule-res.res-coarse {
          background: rgba(148, 163, 184, 0.15);
          color: #94a3b8;
        }

        .tradeoff-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 0.75rem;
          margin-top: auto;
        }

        .tradeoff-col {
          padding: 0.65rem 0.8rem;
          border-radius: var(--radius-sm);
          font-size: 0.76rem;
        }

        .tradeoff-col.pro {
          background: rgba(16, 185, 129, 0.06);
          border: 1px solid rgba(16, 185, 129, 0.2);
          color: #6ee7b7;
        }

        .tradeoff-col.con {
          background: rgba(244, 63, 94, 0.06);
          border: 1px solid rgba(244, 63, 94, 0.2);
          color: #fda4af;
        }

        .tradeoff-title {
          font-weight: 700;
          text-transform: uppercase;
          font-size: 0.68rem;
          letter-spacing: 0.05em;
          display: block;
          margin-bottom: 0.25rem;
        }
      `}</style>
    </section>
  );
}
