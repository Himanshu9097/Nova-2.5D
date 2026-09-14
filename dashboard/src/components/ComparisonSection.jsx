import React from 'react';
import { 
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
  Scale, 
  Clock, 
  Cpu, 
  Layers, 
  HardDrive, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle,
  Info
} from 'lucide-react';
import { useBenchmark } from '../context/BenchmarkContext';

export default function ComparisonSection() {
  const { activeDataset, isDemo } = useBenchmark();

  const u = activeDataset?.uniform || {
    cells_mean: 3322,
    latency_mean: 49.840,
    latency_std: 11.980,
    fps_mean: 21.14,
    fps_std: 5.09,
    memory_mean: 0.632,
    runs_count: 10
  };

  const a = activeDataset?.adaptive || {
    cells_mean: 3560,
    latency_mean: 77.852,
    latency_std: 25.578,
    fps_mean: 13.95,
    fps_std: 3.83,
    memory_mean: 0.393,
    runs_count: 10
  };

  const comp = activeDataset?.comparison || {
    cell_diff: 238,
    cell_diff_pct: 7.16,
    latency_diff_ms: 28.012,
    latency_diff_pct: 56.2,
    fps_diff: -7.19,
    fps_diff_pct: -34.0
  };

  const datasetName = activeDataset?.dataset?.name || "Active Benchmark";
  const points = activeDataset?.dataset?.points || 10000;

  const CustomBarTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-chart-tooltip">
          <div className="tooltip-title">{label}</div>
          {payload.map((item) => (
            <div key={item.name} className="tooltip-row">
              <span style={{ color: item.color, fontWeight: 600 }}>{item.name}:</span>
              <span className="tooltip-val">{item.value}</span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <section id="comparison" className="section-container">
      <div className="section-header">
        <div className="section-title-group">
          <div className="section-tag">
            <Scale size={14} />
            Empirical Benchmark Head-to-Head
          </div>
          <h2 className="section-title">
            Uniform Grid vs Adaptive Grid ({datasetName})
          </h2>
          <p className="section-desc">
            Direct statistical comparison across {u.runs_count || 10} empirical iterations on {points.toLocaleString()} points.
            All metrics computed dynamically by the Python benchmark engine.
          </p>
        </div>

        <div className="header-meta">
          <span className="badge badge-purple">{u.runs_count || 10} Multi-Run Iterations</span>
        </div>
      </div>

      {/* Primary Comparison Summary Cards (Head-to-Head) */}
      <div className="comparison-cards-grid">
        {/* Cell Count Card */}
        <div className="glass-card stat-compare-card">
          <div className="stat-card-title">
            <Layers size={16} className="text-cyan-400" />
            Occupied Grid Cells
          </div>
          <div className="stat-compare-split">
            <div className="stat-half uniform">
              <span className="stat-label">Uniform</span>
              <span className="stat-num">{Math.round(u.cells_mean).toLocaleString()}</span>
              <span className="stat-sub">Fixed 0.50m</span>
            </div>
            <div className="stat-divider">VS</div>
            <div className="stat-half adaptive">
              <span className="stat-label">Adaptive</span>
              <span className="stat-num text-purple-400">{Math.round(a.cells_mean).toLocaleString()}</span>
              <span className="stat-sub">0.25m - 1.0m</span>
            </div>
          </div>
          <div className="stat-delta-row warning">
            {comp.cell_diff > 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            <span>
              {comp.cell_diff > 0 ? `+${comp.cell_diff.toLocaleString()}` : comp.cell_diff.toLocaleString()} cells ({comp.cell_diff_pct > 0 ? `+${comp.cell_diff_pct}%` : `${comp.cell_diff_pct}%`})
            </span>
          </div>
          <p className="stat-explanation">
            {comp.cell_diff > 0 
              ? "Dense near-field objects split into fine 0.25m cells, exceeding uniform cell count." 
              : "Hierarchical coarse cells achieved spatial compression over uniform baseline."}
          </p>
        </div>

        {/* Latency Card */}
        <div className="glass-card stat-compare-card">
          <div className="stat-card-title">
            <Clock size={16} className="text-blue-400" />
            Execution Latency (Mean ± σ)
          </div>
          <div className="stat-compare-split">
            <div className="stat-half uniform">
              <span className="stat-label">Uniform</span>
              <span className="stat-num">{u.latency_mean.toFixed(2)} ms</span>
              <span className="stat-sub">σ = ±{u.latency_std ? u.latency_std.toFixed(2) : '0.00'} ms</span>
            </div>
            <div className="stat-divider">VS</div>
            <div className="stat-half adaptive">
              <span className="stat-label">Adaptive</span>
              <span className="stat-num text-amber-400">{a.latency_mean.toFixed(2)} ms</span>
              <span className="stat-sub">σ = ±{a.latency_std ? a.latency_std.toFixed(2) : '0.00'} ms</span>
            </div>
          </div>
          <div className="stat-delta-row warning">
            {comp.latency_diff_ms > 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            <span>
              {comp.latency_diff_ms > 0 ? `+${comp.latency_diff_ms}` : comp.latency_diff_ms} ms ({comp.latency_diff_pct > 0 ? `+${comp.latency_diff_pct}%` : `${comp.latency_diff_pct}%`})
            </span>
          </div>
          <p className="stat-explanation">
            Dynamic Euclidean distance checks and 3-tuple hash keys add per-point interpreted branching cost.
          </p>
        </div>

        {/* FPS Card */}
        <div className="glass-card stat-compare-card">
          <div className="stat-card-title">
            <Cpu size={16} className="text-emerald-400" />
            Throughput (Frames Per Second)
          </div>
          <div className="stat-compare-split">
            <div className="stat-half uniform">
              <span className="stat-label">Uniform</span>
              <span className="stat-num text-emerald-400">{u.fps_mean.toFixed(2)}</span>
              <span className="stat-sub">σ = ±{u.fps_std ? u.fps_std.toFixed(2) : '0.00'} FPS</span>
            </div>
            <div className="stat-divider">VS</div>
            <div className="stat-half adaptive">
              <span className="stat-label">Adaptive</span>
              <span className="stat-num text-amber-400">{a.fps_mean.toFixed(2)}</span>
              <span className="stat-sub">σ = ±{a.fps_std ? a.fps_std.toFixed(2) : '0.00'} FPS</span>
            </div>
          </div>
          <div className="stat-delta-row warning">
            {comp.fps_diff > 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            <span>
              {comp.fps_diff > 0 ? `+${comp.fps_diff}` : comp.fps_diff} FPS ({comp.fps_diff_pct > 0 ? `+${comp.fps_diff_pct}%` : `${comp.fps_diff_pct}%`})
            </span>
          </div>
          <p className="stat-explanation">
            Uniform direct floor indexing executes faster in pure Python than interpreted multi-level branching.
          </p>
        </div>

        {/* Memory Card */}
        <div className="glass-card stat-compare-card">
          <div className="stat-card-title">
            <HardDrive size={16} className="text-purple-400" />
            Process Memory Delta
          </div>
          <div className="stat-compare-split">
            <div className="stat-half uniform">
              <span className="stat-label">Uniform</span>
              <span className="stat-num">{u.memory_mean ? u.memory_mean.toFixed(3) : '0.000'} MB</span>
              <span className="stat-sub">Per iteration delta</span>
            </div>
            <div className="stat-divider">VS</div>
            <div className="stat-half adaptive">
              <span className="stat-label">Adaptive</span>
              <span className="stat-num">{a.memory_mean ? a.memory_mean.toFixed(3) : '0.000'} MB</span>
              <span className="stat-sub">Per iteration delta</span>
            </div>
          </div>
          <div className="stat-delta-row neutral">
            <Info size={14} />
            <span>Preliminary / Profiling limitation</span>
          </div>
          <p className="stat-explanation">
            Short iterations report small or zero RSS deltas due to OS process page pooling.
          </p>
        </div>
      </div>

      {/* Grouped Bar Charts */}
      <div className="grid-2" style={{ marginTop: '1.5rem' }}>
        <div className="glass-card" style={{ padding: '1.4rem' }}>
          <div className="chart-header-row">
            <h3 className="chart-title">Throughput (FPS) & Latency (ms)</h3>
            <span className="badge badge-neutral">Mean of {u.runs_count || 10} Runs</span>
          </div>

          <div style={{ width: '100%', height: 280 }}>
            <ResponsiveContainer>
              <BarChart data={[
                { name: 'FPS (Hz)', Uniform: u.fps_mean, Adaptive: a.fps_mean },
                { name: 'Latency (ms)', Uniform: u.latency_mean, Adaptive: a.latency_mean }
              ]} margin={{ top: 20, right: 30, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="name" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <RechartsTooltip content={<CustomBarTooltip />} />
                <Legend 
                  wrapperStyle={{ paddingTop: 10 }}
                  formatter={(value) => <span style={{ color: '#cbd5e1', fontSize: 12 }}>{value} Grid</span>}
                />
                <Bar dataKey="Uniform" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Adaptive" fill="#a855f7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card" style={{ padding: '1.4rem' }}>
          <div className="chart-header-row">
            <h3 className="chart-title">Occupied Cell Count Comparison</h3>
            <span className="badge badge-neutral">{points.toLocaleString()} Points Input</span>
          </div>

          <div style={{ width: '100%', height: 280 }}>
            <ResponsiveContainer>
              <BarChart data={[
                { name: 'Occupied Cells', Uniform: Math.round(u.cells_mean), Adaptive: Math.round(a.cells_mean) }
              ]} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="name" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <RechartsTooltip content={<CustomBarTooltip />} />
                <Legend 
                  wrapperStyle={{ paddingTop: 10 }}
                  formatter={(value) => <span style={{ color: '#cbd5e1', fontSize: 12 }}>{value} Grid</span>}
                />
                <Bar dataKey="Uniform" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Adaptive" fill="#a855f7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Comprehensive Statistical Summary Table */}
      <div className="glass-card" style={{ marginTop: '1.5rem', padding: '1.4rem' }}>
        <h3 className="chart-title" style={{ marginBottom: '1rem' }}>
          Empirical Statistical Breakdown: {datasetName}
        </h3>

        <div className="data-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Evaluation Metric</th>
                <th>Uniform Grid</th>
                <th>Adaptive Grid</th>
                <th>Empirical Delta</th>
                <th>Status / Interpretation</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{ fontWeight: 600 }}>Occupied Cell Count</td>
                <td className="mono">{Math.round(u.cells_mean).toLocaleString()} cells</td>
                <td className="mono" style={{ color: '#c084fc' }}>{Math.round(a.cells_mean).toLocaleString()} cells</td>
                <td className="mono" style={{ color: '#fbbf24' }}>
                  {comp.cell_diff > 0 ? `+${comp.cell_diff.toLocaleString()}` : comp.cell_diff.toLocaleString()} ({comp.cell_diff_pct}%)
                </td>
                <td><span className="badge badge-amber">{comp.cell_diff > 0 ? 'Near-Field Subcells' : 'Coarse Compression'}</span></td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Execution Latency (Mean)</td>
                <td className="mono">{u.latency_mean.toFixed(3)} ms</td>
                <td className="mono" style={{ color: '#c084fc' }}>{a.latency_mean.toFixed(3)} ms</td>
                <td className="mono" style={{ color: '#fbbf24' }}>
                  {comp.latency_diff_ms > 0 ? `+${comp.latency_diff_ms}` : comp.latency_diff_ms} ms ({comp.latency_diff_pct}%)
                </td>
                <td><span className="badge badge-rose">Interpreted Python Overhead</span></td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Latency Std Deviation (σ)</td>
                <td className="mono">{u.latency_std ? u.latency_std.toFixed(3) : '0.000'} ms</td>
                <td className="mono" style={{ color: '#c084fc' }}>{a.latency_std ? a.latency_std.toFixed(3) : '0.000'} ms</td>
                <td className="mono">
                  {u.latency_std && a.latency_std ? `±${(a.latency_std - u.latency_std).toFixed(3)} ms` : 'N/A'}
                </td>
                <td><span className="badge badge-amber">Algorithmic Jitter</span></td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Throughput (Mean FPS)</td>
                <td className="mono" style={{ color: '#34d399' }}>{u.fps_mean.toFixed(2)} FPS</td>
                <td className="mono" style={{ color: '#fbbf24' }}>{a.fps_mean.toFixed(2)} FPS</td>
                <td className="mono" style={{ color: '#fbbf24' }}>
                  {comp.fps_diff > 0 ? `+${comp.fps_diff}` : comp.fps_diff} FPS ({comp.fps_diff_pct}%)
                </td>
                <td><span className={`badge ${a.fps_mean >= 20 ? 'badge-emerald' : 'badge-amber'}`}>
                  {a.fps_mean >= 20 ? 'Real-time (>=20 FPS)' : 'Below Real-time Target'}
                </span></td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Input Point Cloud Load</td>
                <td className="mono">{points.toLocaleString()} points</td>
                <td className="mono">{points.toLocaleString()} points</td>
                <td className="mono">Identical</td>
                <td><span className="badge badge-cyan">{isDemo ? "Deterministic Seed 42" : "Custom Ingestion"}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <style>{`
        .comparison-cards-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 1.25rem;
        }

        .stat-compare-card {
          display: flex;
          flex-direction: column;
          padding: 1.25rem;
        }

        .stat-card-title {
          font-size: 0.8rem;
          font-weight: 700;
          color: #fff;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          margin-bottom: 0.85rem;
        }

        .stat-compare-split {
          display: flex;
          align-items: center;
          justify-content: space-between;
          background: rgba(15, 23, 42, 0.6);
          border: 1px solid var(--card-border);
          border-radius: var(--radius-sm);
          padding: 0.75rem 0.85rem;
          margin-bottom: 0.75rem;
        }

        .stat-half {
          display: flex;
          flex-direction: column;
        }

        .stat-half.adaptive {
          align-items: flex-end;
        }

        .stat-label {
          font-size: 0.7rem;
          color: var(--text-muted);
          text-transform: uppercase;
        }

        .stat-num {
          font-family: var(--font-mono);
          font-size: 1.15rem;
          font-weight: 700;
          color: #fff;
        }

        .stat-sub {
          font-family: var(--font-mono);
          font-size: 0.68rem;
          color: var(--text-muted);
        }

        .stat-divider {
          font-family: var(--font-mono);
          font-size: 0.7rem;
          font-weight: 800;
          color: var(--text-muted);
          background: rgba(255, 255, 255, 0.04);
          padding: 0.2rem 0.4rem;
          border-radius: 4px;
        }

        .stat-delta-row {
          display: flex;
          align-items: center;
          gap: 0.4rem;
          font-size: 0.75rem;
          font-weight: 600;
          font-family: var(--font-mono);
          margin-bottom: 0.5rem;
        }

        .stat-delta-row.warning {
          color: #fbbf24;
        }

        .stat-delta-row.neutral {
          color: #94a3b8;
        }

        .stat-explanation {
          font-size: 0.74rem;
          color: var(--text-secondary);
          line-height: 1.4;
          margin-top: auto;
        }

        .chart-header-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 1rem;
        }

        .chart-title {
          font-size: 0.95rem;
          font-weight: 700;
          color: #fff;
        }

        @media (max-width: 1200px) {
          .comparison-cards-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }
      `}</style>
    </section>
  );
}
