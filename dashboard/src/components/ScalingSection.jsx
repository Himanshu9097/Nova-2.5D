import React, { useState } from 'react';
import { 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as RechartsTooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';
import { 
  TrendingUp, 
  AlertTriangle, 
  BarChart3, 
  Clock, 
  Cpu, 
  Layers, 
  Info,
  Maximize2
} from 'lucide-react';
import { 
  SCALING_SUMMARY, 
  SCALING_CHART_DATA, 
  SCALING_LIMITATION_NOTE 
} from '../data/benchmarkData';

export default function ScalingSection() {
  const [selectedPointCount, setSelectedPointCount] = useState(50000);

  const CustomScalingTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-chart-tooltip">
          <div className="tooltip-title">{label} Points Input</div>
          {payload.map((item) => (
            <div key={item.name} className="tooltip-row">
              <span style={{ color: item.color }}>{item.name}:</span>
              <span className="tooltip-val">{item.value}</span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <section id="scaling" className="section-container">
      <div className="section-header">
        <div className="section-title-group">
          <div className="section-tag">
            <TrendingUp size={14} />
            Computational Stress & Load Scaling
          </div>
          <h2 className="section-title">
            Point Cloud Size Scaling Analysis (5k – 50k Points)
          </h2>
          <p className="section-desc">
            Empirical runtime performance under 5k, 10k, 25k, and 50k point loads from 
            <code style={{ color: 'var(--accent-cyan)' }}> benchmark/results/scaling_benchmark.csv</code> (5 runs each).
          </p>
        </div>

        <div className="header-meta">
          <span className="badge badge-amber">
            <AlertTriangle size={12} />
            Synthetic Load Multiplier
          </span>
        </div>
      </div>

      {/* Prominent Limitation Callout Box as Required */}
      <div className="callout-box warning" style={{ marginBottom: '1.5rem' }}>
        <AlertTriangle size={20} className="text-amber-400" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div>
          <strong style={{ color: '#fbbf24' }}>Experimental Constraint & Dataset Limitation:</strong>
          <p style={{ marginTop: '0.25rem', color: '#e2e8f0', fontSize: '0.84rem' }}>
            {SCALING_LIMITATION_NOTE}
          </p>
        </div>
      </div>

      {/* 3 Interactive Scaling Charts */}
      <div className="grid-3">
        {/* CHART 1: Point Count vs Latency */}
        <div className="glass-card chart-card">
          <div className="chart-card-header">
            <div>
              <h3 className="chart-title">Point Count vs Latency (ms)</h3>
              <span className="chart-sub">Computational processing time</span>
            </div>
            <Clock size={16} className="text-cyan-400" />
          </div>

          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer>
              <LineChart data={SCALING_CHART_DATA} margin={{ top: 15, right: 20, left: -5, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="pointsLabel" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <RechartsTooltip content={<CustomScalingTooltip />} />
                <Legend wrapperStyle={{ paddingTop: 8 }} />
                <Line 
                  type="monotone" 
                  dataKey="uniformLatency" 
                  name="Uniform Latency (ms)" 
                  stroke="#3b82f6" 
                  strokeWidth={2.5}
                  dot={{ r: 4, fill: '#3b82f6' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="adaptiveLatency" 
                  name="Adaptive Latency (ms)" 
                  stroke="#a855f7" 
                  strokeWidth={2.5}
                  dot={{ r: 4, fill: '#a855f7' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* CHART 2: Point Count vs FPS */}
        <div className="glass-card chart-card">
          <div className="chart-card-header">
            <div>
              <h3 className="chart-title">Point Count vs FPS</h3>
              <span className="chart-sub">Throughput degradation curve</span>
            </div>
            <Cpu size={16} className="text-emerald-400" />
          </div>

          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer>
              <LineChart data={SCALING_CHART_DATA} margin={{ top: 15, right: 20, left: -5, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="pointsLabel" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <RechartsTooltip content={<CustomScalingTooltip />} />
                <Legend wrapperStyle={{ paddingTop: 8 }} />
                <Line 
                  type="monotone" 
                  dataKey="uniformFps" 
                  name="Uniform FPS" 
                  stroke="#10b981" 
                  strokeWidth={2.5}
                  dot={{ r: 4, fill: '#10b981' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="adaptiveFps" 
                  name="Adaptive FPS" 
                  stroke="#f59e0b" 
                  strokeWidth={2.5}
                  dot={{ r: 4, fill: '#f59e0b' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* CHART 3: Point Count vs Cells */}
        <div className="glass-card chart-card">
          <div className="chart-card-header">
            <div>
              <h3 className="chart-title">Point Count vs Cell Count</h3>
              <span className="chart-sub">Spatial occupancy saturation</span>
            </div>
            <Layers size={16} className="text-purple-400" />
          </div>

          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer>
              <BarChart data={SCALING_CHART_DATA} margin={{ top: 15, right: 20, left: -5, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="pointsLabel" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <YAxis domain={[0, 4200]} stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <RechartsTooltip content={<CustomScalingTooltip />} />
                <Legend wrapperStyle={{ paddingTop: 8 }} />
                <Bar dataKey="uniformCells" name="Uniform Cells" fill="#3b82f6" radius={[3, 3, 0, 0]} />
                <Bar dataKey="adaptiveCells" name="Adaptive Cells" fill="#a855f7" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Scaling Data Cards for Each Point Load */}
      <div className="scaling-cards-grid" style={{ marginTop: '1.5rem' }}>
        {SCALING_SUMMARY.map((tier) => (
          <div 
            key={tier.points} 
            className={`glass-card scaling-tier-card ${selectedPointCount === tier.points ? 'active-tier' : ''}`}
            onClick={() => setSelectedPointCount(tier.points)}
          >
            <div className="tier-header">
              <span className="tier-points">{tier.pointsLabel} Points</span>
              <span className="badge badge-neutral">5 Runs</span>
            </div>

            <div className="tier-metric-split">
              {/* Uniform column */}
              <div className="tier-col">
                <span className="tier-col-title text-blue-400">Uniform</span>
                <div className="tier-data-line">
                  <span className="tier-key">Cells:</span>
                  <span className="tier-val">{tier.uniform.cells}</span>
                </div>
                <div className="tier-data-line">
                  <span className="tier-key">Latency:</span>
                  <span className="tier-val">{tier.uniform.latencyMean.toFixed(2)} ms</span>
                </div>
                <div className="tier-data-line">
                  <span className="tier-key">FPS:</span>
                  <span className="tier-val" style={{ color: '#34d399' }}>{tier.uniform.fpsMean.toFixed(2)}</span>
                </div>
              </div>

              <div className="tier-sep"></div>

              {/* Adaptive column */}
              <div className="tier-col">
                <span className="tier-col-title text-purple-400">Adaptive</span>
                <div className="tier-data-line">
                  <span className="tier-key">Cells:</span>
                  <span className="tier-val">{tier.adaptive.cells}</span>
                </div>
                <div className="tier-data-line">
                  <span className="tier-key">Latency:</span>
                  <span className="tier-val">{tier.adaptive.latencyMean.toFixed(2)} ms</span>
                </div>
                <div className="tier-data-line">
                  <span className="tier-key">FPS:</span>
                  <span className="tier-val" style={{ color: '#fbbf24' }}>{tier.adaptive.fpsMean.toFixed(2)}</span>
                </div>
              </div>
            </div>

            <div className="tier-footer">
              <span className="tier-delta">
                Latency: +{(tier.adaptive.latencyMean - tier.uniform.latencyMean).toFixed(2)} ms in Adaptive
              </span>
            </div>
          </div>
        ))}
      </div>

      <style>{`
        .chart-card-header {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          margin-bottom: 0.85rem;
        }

        .chart-title {
          font-size: 0.9rem;
          font-weight: 700;
          color: #fff;
        }

        .chart-sub {
          font-size: 0.72rem;
          color: var(--text-muted);
          display: block;
        }

        .scaling-cards-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 1.25rem;
        }

        .scaling-tier-card {
          padding: 1.25rem;
          display: flex;
          flex-direction: column;
          gap: 0.85rem;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .scaling-tier-card:hover, .scaling-tier-card.active-tier {
          border-color: var(--accent-cyan);
          background: rgba(6, 182, 212, 0.04);
        }

        .tier-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          border-bottom: 1px solid rgba(255, 255, 255, 0.06);
          padding-bottom: 0.5rem;
        }

        .tier-points {
          font-family: var(--font-mono);
          font-size: 1.05rem;
          font-weight: 700;
          color: #fff;
        }

        .tier-metric-split {
          display: flex;
          align-items: stretch;
          justify-content: space-between;
          gap: 0.75rem;
        }

        .tier-col {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 0.3rem;
        }

        .tier-sep {
          width: 1px;
          background: rgba(255, 255, 255, 0.08);
        }

        .tier-col-title {
          font-family: var(--font-mono);
          font-size: 0.72rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          margin-bottom: 0.15rem;
        }

        .tier-data-line {
          display: flex;
          align-items: baseline;
          justify-content: space-between;
          font-size: 0.75rem;
        }

        .tier-key {
          color: var(--text-muted);
        }

        .tier-val {
          font-family: var(--font-mono);
          font-weight: 600;
          color: #e2e8f0;
        }

        .tier-footer {
          border-top: 1px solid rgba(255, 255, 255, 0.05);
          padding-top: 0.4rem;
          font-size: 0.7rem;
          font-family: var(--font-mono);
          color: #fbbf24;
        }

        @media (max-width: 1080px) {
          .scaling-cards-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }
      `}</style>
    </section>
  );
}
