import React from 'react';
import { 
  History, 
  RotateCcw, 
  Eye, 
  Clock, 
  Calendar, 
  Layers, 
  ArrowRight,
  Database,
  CheckCircle2
} from 'lucide-react';
import { useBenchmark } from '../context/BenchmarkContext';

export default function HistorySection() {
  const { historyList, selectHistoryItem, resetToDemo, isDemo, activeDataset } = useBenchmark();

  return (
    <section id="history" className="section-container">
      <div className="section-header">
        <div className="section-title-group">
          <div className="section-tag">
            <History size={14} />
            Persistent Evaluation Archive
          </div>
          <h2 className="section-title">
            Benchmark Execution History
          </h2>
          <p className="section-desc">
            All completed empirical evaluations stored on disk. Click "Inspect Results" on any historical run 
            to dynamically load its metrics, charts, and 2.5D output grid into the dashboard.
          </p>
        </div>

        <div className="header-meta">
          {!isDemo && (
            <button className="badge badge-amber" onClick={resetToDemo} style={{ cursor: 'pointer', border: '1px solid rgba(245, 158, 11, 0.4)' }}>
              <RotateCcw size={12} />
              Reset to Synthetic Baseline
            </button>
          )}
        </div>
      </div>

      <div className="glass-card" style={{ padding: '1.25rem' }}>
        <div className="data-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Dataset Identifier</th>
                <th>Execution Date</th>
                <th>Points</th>
                <th>Uniform FPS</th>
                <th>Adaptive FPS</th>
                <th>Uniform Latency</th>
                <th>Adaptive Latency</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {historyList.map((item) => {
                const isCurrent = activeDataset?.id === item.id || (isDemo && item.is_baseline);
                return (
                  <tr key={item.id} className={isCurrent ? 'active-history-row' : ''}>
                    <td>
                      <div className="hist-name-cell">
                        <span className="hist-name">{item.dataset_name}</span>
                        {item.is_baseline && (
                          <span className="badge badge-cyan" style={{ fontSize: '0.65rem' }}>
                            Default Baseline
                          </span>
                        )}
                        {isCurrent && (
                          <span className="badge badge-emerald" style={{ fontSize: '0.65rem' }}>
                            Active View
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="mono" style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                      {item.formatted_date || item.timestamp}
                    </td>
                    <td className="mono">{item.points?.toLocaleString()} pts</td>
                    <td className="mono text-emerald-400 font-semibold">{item.uniform_fps?.toFixed(2)}</td>
                    <td className="mono text-amber-400 font-semibold">{item.adaptive_fps?.toFixed(2)}</td>
                    <td className="mono">{item.uniform_latency_ms?.toFixed(2)} ms</td>
                    <td className="mono">{item.adaptive_latency_ms?.toFixed(2)} ms</td>
                    <td>
                      <button 
                        className={`inspect-btn ${isCurrent ? 'current' : ''}`}
                        onClick={() => selectHistoryItem(item.id)}
                        disabled={isCurrent}
                      >
                        <Eye size={12} />
                        {isCurrent ? 'Viewing' : 'Inspect Results'}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <style>{`
        .hist-name-cell {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .hist-name {
          font-weight: 700;
          color: #fff;
        }

        .active-history-row td {
          background: rgba(6, 182, 212, 0.04);
        }

        .inspect-btn {
          background: rgba(15, 23, 42, 0.8);
          border: 1px solid var(--card-border);
          color: #cbd5e1;
          font-family: var(--font-sans);
          font-size: 0.75rem;
          padding: 0.3rem 0.65rem;
          border-radius: var(--radius-sm);
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          gap: 0.35rem;
          transition: all 0.2s ease;
        }

        .inspect-btn:hover:not(:disabled) {
          border-color: var(--accent-cyan);
          background: var(--accent-cyan);
          color: #070a12;
          font-weight: 700;
        }

        .inspect-btn.current {
          border-color: var(--accent-emerald);
          color: var(--accent-emerald);
          cursor: default;
          background: rgba(16, 185, 129, 0.1);
        }
      `}</style>
    </section>
  );
}
