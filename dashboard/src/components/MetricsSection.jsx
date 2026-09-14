import React from 'react';
import { 
  Activity, 
  Cpu, 
  Layers, 
  BarChart3, 
  TrendingUp, 
  CheckCircle2, 
  Clock, 
  Code,
  ShieldCheck
} from 'lucide-react';
import { METRICS_TAXONOMY } from '../data/benchmarkData';

export default function MetricsSection() {
  return (
    <section id="metrics" className="section-container">
      <div className="section-header">
        <div className="section-title-group">
          <div className="section-tag">
            <Activity size={14} />
            Scientific Measurement Framework
          </div>
          <h2 className="section-title">
            What We Measure (Metric Taxonomy)
          </h2>
          <p className="section-desc">
            Formal mathematical definitions, instrumentation points, and measurement criteria across 
            computational performance, spatial mapping fidelity, statistical dispersion, and stress scaling.
          </p>
        </div>
      </div>

      <div className="grid-2">
        {METRICS_TAXONOMY.map((group, idx) => (
          <div key={group.category} className="glass-card metric-group-card">
            <div className="metric-group-header">
              <div>
                <h3 className="group-title">{group.category}</h3>
                <span className="group-desc">{group.desc}</span>
              </div>
              <span className="badge badge-neutral">
                {group.metrics.length} Parameters
              </span>
            </div>

            <div className="metric-cards-list">
              {group.metrics.map((m, mIdx) => (
                <div key={mIdx} className="metric-item-card">
                  <div className="metric-top-line">
                    <span className="metric-name">{m.name}</span>
                    <span className={`badge ${m.status === 'Active' ? 'badge-emerald' : m.status === 'Preliminary' ? 'badge-amber' : 'badge-neutral'}`}>
                      {m.status === 'Active' ? 'ACTIVE' : m.status === 'Preliminary' ? 'PRELIMINARY' : 'COMING SOON'}
                    </span>
                  </div>

                  <div className="metric-formula-row">
                    <Code size={12} className="text-cyan-400" />
                    <code>{m.formula}</code>
                  </div>

                  <div className="metric-val-row">
                    <span className="val-lbl">Observed / Value:</span>
                    <span className="val-text mono">{m.value}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <style>{`
        .metric-group-card {
          padding: 1.5rem;
          display: flex;
          flex-direction: column;
          gap: 1.25rem;
        }

        .metric-group-header {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          border-bottom: 1px solid rgba(255, 255, 255, 0.06);
          padding-bottom: 0.75rem;
        }

        .group-title {
          font-size: 1.05rem;
          font-weight: 700;
          color: #fff;
        }

        .group-desc {
          font-size: 0.76rem;
          color: var(--text-muted);
          display: block;
          margin-top: 0.2rem;
        }

        .metric-cards-list {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .metric-item-card {
          background: rgba(15, 23, 42, 0.6);
          border: 1px solid var(--card-border);
          border-radius: var(--radius-sm);
          padding: 0.85rem 1rem;
          display: flex;
          flex-direction: column;
          gap: 0.4rem;
        }

        .metric-top-line {
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .metric-name {
          font-size: 0.88rem;
          font-weight: 600;
          color: #fff;
        }

        .metric-formula-row {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.76rem;
          color: var(--accent-cyan);
          background: rgba(6, 182, 212, 0.05);
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
        }

        .metric-formula-row code {
          font-family: var(--font-mono);
        }

        .metric-val-row {
          display: flex;
          align-items: baseline;
          justify-content: space-between;
          font-size: 0.78rem;
          margin-top: 0.2rem;
        }

        .val-lbl {
          color: var(--text-muted);
        }

        .val-text {
          color: #cbd5e1;
          font-weight: 500;
        }
      `}</style>
    </section>
  );
}
