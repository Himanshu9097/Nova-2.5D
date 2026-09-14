import React, { useState, useMemo } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as RechartsTooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';
import { 
  FileSpreadsheet, 
  ArrowUpDown, 
  Filter, 
  CheckCircle2, 
  Clock, 
  Cpu, 
  Layers, 
  HardDrive
} from 'lucide-react';
import { useBenchmark } from '../context/BenchmarkContext';

export default function MultiRunSection() {
  const { activeDataset } = useBenchmark();
  const [methodFilter, setMethodFilter] = useState('All'); // 'All', 'Uniform', 'Adaptive'
  const [sortField, setSortField] = useState('run');
  const [sortDirection, setSortDirection] = useState('asc'); // 'asc' or 'desc'
  const [activeChartMetric, setActiveChartMetric] = useState('latency'); // 'latency' or 'fps'

  const runsData = activeDataset?.runs || {};
  const pairedRuns = runsData.paired || [];
  const uniformRuns = runsData.uniform || [];
  const adaptiveRuns = runsData.adaptive || [];

  const allRunsFlattened = useMemo(() => {
    return [...uniformRuns, ...adaptiveRuns];
  }, [uniformRuns, adaptiveRuns]);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const filteredData = useMemo(() => {
    let list = [...allRunsFlattened];
    if (methodFilter !== 'All') {
      list = list.filter(item => item.method === methodFilter);
    }
    list.sort((a, b) => {
      let valA = a[sortField];
      let valB = b[sortField];
      if (typeof valA === 'string') {
        return sortDirection === 'asc' 
          ? valA.localeCompare(valB) 
          : valB.localeCompare(valA);
      }
      return sortDirection === 'asc' ? valA - valB : valB - valA;
    });
    return list;
  }, [allRunsFlattened, methodFilter, sortField, sortDirection]);

  const CustomLineTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-chart-tooltip">
          <div className="tooltip-title">{label}</div>
          {payload.map((entry) => (
            <div key={entry.name} className="tooltip-row">
              <span style={{ color: entry.color }}>{entry.name}:</span>
              <span className="tooltip-val">
                {entry.value} {activeChartMetric === 'latency' ? 'ms' : 'FPS'}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  const uStats = activeDataset?.uniform || {};
  const aStats = activeDataset?.adaptive || {};

  return (
    <section id="multi-run" className="section-container">
      <div className="section-header">
        <div className="section-title-group">
          <div className="section-tag">
            <FileSpreadsheet size={14} />
            Raw Empirical Telemetry Logging
          </div>
          <h2 className="section-title">
            Run-by-Run Iteration Analysis ({pairedRuns.length} Iterations)
          </h2>
          <p className="section-desc">
            Granular iteration telemetry for {activeDataset?.dataset?.name}.
            Sort by any column, filter by grid method, and inspect dispersion across iterations.
          </p>
        </div>

        {/* Filter Toolbar */}
        <div className="table-controls">
          <div className="filter-group">
            <Filter size={14} className="text-slate-400" />
            <span className="filter-lbl">Filter:</span>
            {['All', 'Uniform', 'Adaptive'].map(method => (
              <button
                key={method}
                className={`filter-btn ${methodFilter === method ? 'active' : ''}`}
                onClick={() => setMethodFilter(method)}
              >
                {method}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chart: Run-by-run trendline */}
      <div className="glass-card" style={{ marginBottom: '1.5rem', padding: '1.4rem' }}>
        <div className="chart-header-row">
          <div>
            <h3 className="chart-title">Empirical Variation Across Iterations</h3>
            <span className="chart-subtitle">Direct side-by-side run timeline</span>
          </div>
          <div className="metric-switch-pills">
            <button 
              className={`pill-btn ${activeChartMetric === 'latency' ? 'active' : ''}`}
              onClick={() => setActiveChartMetric('latency')}
            >
              Latency (ms)
            </button>
            <button 
              className={`pill-btn ${activeChartMetric === 'fps' ? 'active' : ''}`}
              onClick={() => setActiveChartMetric('fps')}
            >
              Throughput (FPS)
            </button>
          </div>
        </div>

        <div style={{ width: '100%', height: 260 }}>
          <ResponsiveContainer>
            <LineChart data={pairedRuns} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="run" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <RechartsTooltip content={<CustomLineTooltip />} />
              <Legend wrapperStyle={{ paddingTop: 10 }} />
              <Line 
                type="monotone" 
                dataKey={activeChartMetric === 'latency' ? 'uniformLatency' : 'uniformFps'} 
                name="Uniform Grid" 
                stroke="#3b82f6" 
                strokeWidth={2.5}
                dot={{ r: 4, fill: '#3b82f6' }}
              />
              <Line 
                type="monotone" 
                dataKey={activeChartMetric === 'latency' ? 'adaptiveLatency' : 'adaptiveFps'} 
                name="Adaptive Grid" 
                stroke="#a855f7" 
                strokeWidth={2.5}
                dot={{ r: 4, fill: '#a855f7' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Interactive Table */}
      <div className="glass-card" style={{ padding: '1.25rem' }}>
        <div className="data-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th onClick={() => handleSort('run')}>
                  <div className="th-content">
                    <span>Run</span>
                    <ArrowUpDown size={12} />
                  </div>
                </th>
                <th onClick={() => handleSort('method')}>
                  <div className="th-content">
                    <span>Method</span>
                    <ArrowUpDown size={12} />
                  </div>
                </th>
                <th onClick={() => handleSort('points')}>
                  <div className="th-content">
                    <span>Points</span>
                    <ArrowUpDown size={12} />
                  </div>
                </th>
                <th onClick={() => handleSort('cells')}>
                  <div className="th-content">
                    <span>Occupied Cells</span>
                    <ArrowUpDown size={12} />
                  </div>
                </th>
                <th onClick={() => handleSort('latency_ms')}>
                  <div className="th-content">
                    <span>Latency (ms)</span>
                    <ArrowUpDown size={12} />
                  </div>
                </th>
                <th onClick={() => handleSort('fps')}>
                  <div className="th-content">
                    <span>FPS (Throughput)</span>
                    <ArrowUpDown size={12} />
                  </div>
                </th>
                <th onClick={() => handleSort('memory_mb')}>
                  <div className="th-content">
                    <span>Memory (MB)</span>
                    <ArrowUpDown size={12} />
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredData.map((row, idx) => (
                <tr key={`${row.method}-${row.run}-${idx}`}>
                  <td className="mono" style={{ color: '#fff', fontWeight: 600 }}>Run #{row.run}</td>
                  <td>
                    <span className={`badge ${row.method === 'Uniform' ? 'badge-blue' : 'badge-purple'}`}>
                      {row.method}
                    </span>
                  </td>
                  <td className="mono">{row.points?.toLocaleString()}</td>
                  <td className="mono" style={{ color: row.method === 'Adaptive' ? '#c084fc' : '#93c5fd' }}>
                    {row.cells?.toLocaleString()}
                  </td>
                  <td className="mono font-semibold" style={{ color: row.latency_ms > 70 ? '#fbbf24' : '#38bdf8' }}>
                    {row.latency_ms?.toFixed(3)} ms
                  </td>
                  <td className="mono font-semibold" style={{ color: row.fps >= 20 ? '#34d399' : '#fb7185' }}>
                    {row.fps?.toFixed(2)}
                  </td>
                  <td className="mono" style={{ color: row.memory_mb === 0 ? '#64748b' : '#cbd5e1' }}>
                    {row.memory_mb !== undefined ? `${row.memory_mb.toFixed(3)} MB` : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
            {/* Statistical Summary Footer Rows */}
            <tfoot>
              {(methodFilter === 'All' || methodFilter === 'Uniform') && uStats.latency_mean && (
                <tr className="summary-row uniform-summary">
                  <td colSpan={2} style={{ fontWeight: 700, color: '#3b82f6' }}>
                    UNIFORM MEAN ± σ
                  </td>
                  <td className="mono">{activeDataset?.dataset?.points?.toLocaleString()}</td>
                  <td className="mono font-bold">{Math.round(uStats.cells_mean)} (±{uStats.cells_std || 0})</td>
                  <td className="mono font-bold" style={{ color: '#38bdf8' }}>
                    {uStats.latency_mean.toFixed(3)} ms (±{uStats.latency_std ? uStats.latency_std.toFixed(2) : 0})
                  </td>
                  <td className="mono font-bold" style={{ color: '#34d399' }}>
                    {uStats.fps_mean.toFixed(2)} FPS (±{uStats.fps_std ? uStats.fps_std.toFixed(2) : 0})
                  </td>
                  <td className="mono font-bold">
                    {uStats.memory_mean ? `${uStats.memory_mean.toFixed(3)} MB` : '0.000 MB'}
                  </td>
                </tr>
              )}

              {(methodFilter === 'All' || methodFilter === 'Adaptive') && aStats.latency_mean && (
                <tr className="summary-row adaptive-summary">
                  <td colSpan={2} style={{ fontWeight: 700, color: '#a855f7' }}>
                    ADAPTIVE MEAN ± σ
                  </td>
                  <td className="mono">{activeDataset?.dataset?.points?.toLocaleString()}</td>
                  <td className="mono font-bold" style={{ color: '#c084fc' }}>{Math.round(aStats.cells_mean)} (±{aStats.cells_std || 0})</td>
                  <td className="mono font-bold" style={{ color: '#fbbf24' }}>
                    {aStats.latency_mean.toFixed(3)} ms (±{aStats.latency_std ? aStats.latency_std.toFixed(2) : 0})
                  </td>
                  <td className="mono font-bold" style={{ color: '#fbbf24' }}>
                    {aStats.fps_mean.toFixed(2)} FPS (±{aStats.fps_std ? aStats.fps_std.toFixed(2) : 0})
                  </td>
                  <td className="mono font-bold">
                    {aStats.memory_mean ? `${aStats.memory_mean.toFixed(3)} MB` : '0.000 MB'}
                  </td>
                </tr>
              )}
            </tfoot>
          </table>
        </div>
      </div>

      <style>{`
        .table-controls {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .filter-group {
          display: flex;
          align-items: center;
          gap: 0.4rem;
          background: rgba(15, 23, 42, 0.7);
          border: 1px solid var(--card-border);
          border-radius: var(--radius-sm);
          padding: 3px 6px;
        }

        .filter-lbl {
          font-size: 0.75rem;
          color: var(--text-muted);
          font-family: var(--font-mono);
          margin-right: 0.2rem;
        }

        .filter-btn {
          background: transparent;
          border: none;
          color: var(--text-secondary);
          font-size: 0.76rem;
          padding: 0.25rem 0.6rem;
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.15s ease;
        }

        .filter-btn.active {
          background: var(--accent-cyan);
          color: #070a12;
          font-weight: 700;
        }

        .chart-subtitle {
          font-size: 0.75rem;
          color: var(--text-muted);
          display: block;
          margin-top: 0.2rem;
        }

        .metric-switch-pills {
          display: flex;
          background: rgba(15, 23, 42, 0.8);
          border: 1px solid var(--card-border);
          border-radius: var(--radius-sm);
          padding: 2px;
        }

        .pill-btn {
          background: transparent;
          border: none;
          color: var(--text-secondary);
          font-size: 0.74rem;
          padding: 0.3rem 0.65rem;
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .pill-btn.active {
          background: rgba(255, 255, 255, 0.12);
          color: #fff;
          font-weight: 600;
        }

        .th-content {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 0.4rem;
        }

        .badge-blue {
          background: rgba(59, 130, 246, 0.15);
          color: #93c5fd;
          border: 1px solid rgba(59, 130, 246, 0.3);
        }

        .summary-row {
          background: rgba(15, 23, 42, 0.95);
          border-top: 2px solid var(--card-border);
          border-bottom: 1px solid var(--card-border);
        }

        .summary-row td {
          padding: 0.9rem 1.1rem;
        }

        .uniform-summary td {
          border-left: 3px solid #3b82f6;
        }

        .adaptive-summary td {
          border-left: 3px solid #a855f7;
        }
      `}</style>
    </section>
  );
}
