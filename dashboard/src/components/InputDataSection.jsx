import React, { useState } from 'react';
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  Tooltip as RechartsTooltip,
  Legend
} from 'recharts';
import { 
  Database, 
  Tag, 
  Layers, 
  Info, 
  Maximize2,
  Code,
  ShieldCheck,
  AlertTriangle
} from 'lucide-react';
import { useBenchmark } from '../context/BenchmarkContext';

export default function InputDataSection() {
  const { activeDataset, isDemo } = useBenchmark();
  const [activeClassIndex, setActiveClassIndex] = useState(null);

  const datasetInfo = activeDataset?.dataset || {};
  const totalPoints = datasetInfo.points || 10000;
  const hasSemantics = datasetInfo.has_semantics !== false;
  const classesList = datasetInfo.classes || [];
  const columnsDetected = datasetInfo.columns || ["x", "y", "z", "intensity", "semantic_class"];
  const bounds = datasetInfo.bounds || { x: [-30, 30], y: [-10, 10], z: [-2, 5] };
  const previewRows = datasetInfo.preview || [];

  const defaultColors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4', '#ec4899'];

  const chartData = classesList.map((c, i) => ({
    name: c.name,
    value: c.count,
    percentage: c.percentage,
    color: c.color || defaultColors[i % defaultColors.length],
    id: c.id
  }));

  const CustomPieTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="custom-chart-tooltip">
          <div className="tooltip-title" style={{ color: data.color }}>
            Class {data.id}: {data.name}
          </div>
          <div className="tooltip-row">
            <span>Points:</span>
            <span className="tooltip-val">{data.value.toLocaleString()} pts</span>
          </div>
          <div className="tooltip-row">
            <span>Proportion:</span>
            <span className="tooltip-val">{data.percentage}%</span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <section id="input-data" className="section-container">
      <div className="section-header">
        <div className="section-title-group">
          <div className="section-tag">
            <Database size={14} />
            Input Dataset & Point Cloud Breakdown
          </div>
          <h2 className="section-title">
            {datasetInfo.name || "Point Cloud Ingestion"}
          </h2>
          <p className="section-desc">
            {isDemo 
              ? "Deterministic 10,000-point synthetic testbed scene generated via NumPy (seed 42) incorporating road plane, vehicle, pedestrian, and wall."
              : `Active dataset with ${totalPoints.toLocaleString()} points and ${columnsDetected.length} detected feature channels.`}
          </p>
        </div>
        <div className="header-meta">
          <span className="badge badge-cyan">
            <ShieldCheck size={13} />
            {totalPoints.toLocaleString()} Points Loaded
          </span>
        </div>
      </div>

      {/* Point Schema Bar */}
      <div className="glass-card" style={{ marginBottom: '1.5rem', padding: '1.25rem 1.5rem' }}>
        <div className="schema-header">
          <span className="schema-label">
            <Code size={15} className="text-cyan-400" />
            Detected Feature Channels & Spatial Extents
          </span>
          <span className="badge badge-neutral">
            Bounds: X [{bounds.x?.[0]}, {bounds.x?.[1]}]m • Y [{bounds.y?.[0]}, {bounds.y?.[1]}]m • Z [{bounds.z?.[0]}, {bounds.z?.[1]}]m
          </span>
        </div>
        <div className="schema-pills">
          {columnsDetected.map((col, idx) => (
            <div key={col} className="schema-pill">
              <span className="schema-idx">[{idx}]</span>
              <span className="schema-name">{col}</span>
              <span className="schema-desc">
                {col === 'x' ? 'Longitudinal axis' : col === 'y' ? 'Lateral axis' : col === 'z' ? 'Elevation axis' : col === 'intensity' ? 'Reflectance' : 'Semantic class'}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* If semantic labels are missing */}
      {!hasSemantics ? (
        <div className="callout-box warning" style={{ marginBottom: '1.5rem' }}>
          <AlertTriangle size={18} className="text-amber-400" style={{ flexShrink: 0 }} />
          <div>
            <strong>Semantic labels unavailable in this dataset.</strong>
            <p style={{ fontSize: '0.82rem', marginTop: '0.2rem', color: '#cbd5e1' }}>
              The benchmark executed all spatial grid discretization, latency profiling, FPS measurement, and cell compression calculations. 
              Semantic IoU accuracy and object-specific retention metrics are disabled for this input.
            </p>
          </div>
        </div>
      ) : (
        /* Semantic Distribution Grid */
        <div className="grid-2">
          {/* Donut Chart */}
          <div className="glass-card chart-card">
            <div className="card-header-line">
              <h3 className="card-subheading">Semantic Class Distribution</h3>
              <span className="badge badge-cyan">{totalPoints.toLocaleString()} Total Points</span>
            </div>

            <div style={{ width: '100%', height: 290 }}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={65}
                    outerRadius={105}
                    paddingAngle={3}
                    dataKey="value"
                    onMouseEnter={(_, index) => setActiveClassIndex(index)}
                    onMouseLeave={() => setActiveClassIndex(null)}
                  >
                    {chartData.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={entry.color} 
                        stroke="#070a12"
                        strokeWidth={2}
                        style={{
                          filter: activeClassIndex === index ? `drop-shadow(0 0 8px ${entry.color})` : 'none',
                          cursor: 'pointer'
                        }}
                      />
                    ))}
                  </Pie>
                  <RechartsTooltip content={<CustomPieTooltip />} />
                  <Legend 
                    formatter={(value) => (
                      <span style={{ color: '#cbd5e1', fontSize: '0.8rem', marginRight: 10 }}>
                        {value}
                      </span>
                    )}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="donut-center-info">
              <span className="donut-center-title">
                {totalPoints >= 1000 ? `${(totalPoints / 1000).toFixed(0)}K` : totalPoints}
              </span>
              <span className="donut-center-sub">Total Pts</span>
            </div>
          </div>

          {/* Class Breakdown List */}
          <div className="class-cards-container">
            {classesList.map((cls, idx) => {
              const colColor = cls.color || defaultColors[idx % defaultColors.length];
              return (
                <div 
                  key={cls.id} 
                  className={`class-card ${activeClassIndex === idx ? 'active' : ''}`}
                  style={{ borderLeftColor: colColor }}
                  onMouseEnter={() => setActiveClassIndex(idx)}
                  onMouseLeave={() => setActiveClassIndex(null)}
                >
                  <div className="class-card-top">
                    <div className="class-id-badge" style={{ backgroundColor: `${colColor}22`, color: colColor, borderColor: `${colColor}55` }}>
                      Class {cls.id}
                    </div>
                    <div className="class-name" style={{ color: '#fff' }}>
                      {cls.name}
                    </div>
                    <div className="class-stats">
                      <span className="class-count">{cls.count.toLocaleString()} pts</span>
                      <span className="class-pct">({cls.percentage}%)</span>
                    </div>
                  </div>
                  {cls.spatialBounds && (
                    <div className="class-bounds-row">
                      <span className="bounds-label">Bounds:</span>
                      <span className="bounds-val">{cls.spatialBounds}</span>
                    </div>
                  )}
                  {cls.description && <p className="class-desc-text">{cls.description}</p>}
                </div>
              );
            })}
          </div>
        </div>
      )}

      <style>{`
        .schema-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 0.85rem;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .schema-label {
          font-size: 0.85rem;
          font-weight: 600;
          color: #fff;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-family: var(--font-mono);
        }

        .schema-pills {
          display: flex;
          gap: 0.65rem;
          flex-wrap: wrap;
        }

        .schema-pill {
          background: rgba(15, 23, 42, 0.7);
          border: 1px solid var(--card-border);
          border-radius: var(--radius-sm);
          padding: 0.6rem 0.85rem;
          display: flex;
          flex-direction: column;
          gap: 0.15rem;
          min-width: 140px;
        }

        .schema-idx {
          font-family: var(--font-mono);
          font-size: 0.68rem;
          color: var(--accent-cyan);
        }

        .schema-name {
          font-family: var(--font-mono);
          font-size: 0.85rem;
          font-weight: 700;
          color: #fff;
        }

        .schema-desc {
          font-size: 0.72rem;
          color: var(--text-muted);
        }

        .chart-card {
          position: relative;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
        }

        .card-header-line {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 0.5rem;
        }

        .card-subheading {
          font-size: 0.95rem;
          font-weight: 700;
          color: #fff;
        }

        .donut-center-info {
          position: absolute;
          top: 45%;
          left: 50%;
          transform: translate(-50%, -50%);
          display: flex;
          flex-direction: column;
          align-items: center;
          pointer-events: none;
        }

        .donut-center-title {
          font-family: var(--font-mono);
          font-size: 1.6rem;
          font-weight: 800;
          color: #fff;
          line-height: 1;
        }

        .donut-center-sub {
          font-size: 0.7rem;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .class-cards-container {
          display: flex;
          flex-direction: column;
          gap: 0.65rem;
        }

        .class-card {
          background: var(--card-bg);
          border: 1px solid var(--card-border);
          border-left-width: 4px;
          border-radius: var(--radius-sm);
          padding: 0.75rem 1rem;
          transition: all 0.2s ease;
        }

        .class-card:hover, .class-card.active {
          background: rgba(255, 255, 255, 0.04);
          transform: translateX(4px);
        }

        .class-card-top {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 0.35rem;
        }

        .class-id-badge {
          font-family: var(--font-mono);
          font-size: 0.68rem;
          font-weight: 700;
          padding: 0.15rem 0.45rem;
          border-radius: 4px;
          border: 1px solid transparent;
        }

        .class-name {
          font-size: 0.9rem;
          font-weight: 700;
          flex: 1;
        }

        .class-stats {
          display: flex;
          align-items: baseline;
          gap: 0.35rem;
          font-family: var(--font-mono);
          font-size: 0.85rem;
        }

        .class-count {
          color: #fff;
          font-weight: 600;
        }

        .class-pct {
          color: var(--text-muted);
          font-size: 0.75rem;
        }

        .class-bounds-row {
          display: flex;
          align-items: center;
          gap: 0.4rem;
          font-size: 0.75rem;
          font-family: var(--font-mono);
          margin-bottom: 0.25rem;
        }

        .bounds-label {
          color: var(--text-muted);
        }

        .bounds-val {
          color: #cbd5e1;
        }

        .class-desc-text {
          font-size: 0.76rem;
          color: var(--text-secondary);
        }
      `}</style>
    </section>
  );
}
