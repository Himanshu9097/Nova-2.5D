import React from 'react';
import { 
  CheckCircle2, 
  Clock, 
  Compass, 
  Sparkles, 
  Calendar,
  Layers,
  ChevronRight
} from 'lucide-react';
import { PROJECT_STATUS } from '../data/benchmarkData';

export default function ProjectStatusSection() {
  const getBadgeStyle = (category) => {
    switch (category) {
      case 'Completed':
        return 'badge-emerald';
      case 'In Progress':
        return 'badge-amber';
      case 'Future Integration':
        return 'badge-cyan';
      default:
        return 'badge-neutral';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'Completed':
        return <CheckCircle2 size={16} className="text-emerald-400" />;
      case 'In Progress':
        return <Clock size={16} className="text-amber-400" />;
      case 'Future Integration':
        return <Compass size={16} className="text-cyan-400" />;
      default:
        return null;
    }
  };

  return (
    <section id="status" className="section-container">
      <div className="section-header">
        <div className="section-title-group">
          <div className="section-tag">
            <Compass size={14} />
            Milestones & Engineering Roadmap
          </div>
          <h2 className="section-title">
            Current Experiment & Integration Status
          </h2>
          <p className="section-desc">
            Granular development audit distinguishing completed benchmarking modules from 
            in-flight validation tasks and downstream simulator integrations.
          </p>
        </div>

        <div className="header-meta">
          <span className="badge badge-emerald">
            Phase 1 Benchmark Complete
          </span>
        </div>
      </div>

      <div className="grid-3">
        {PROJECT_STATUS.map((col) => (
          <div key={col.category} className={`glass-card status-column-card status-${col.color}`}>
            <div className="status-col-header">
              <div className="status-title-wrap">
                {getCategoryIcon(col.category)}
                <h3 className="status-col-title">{col.category}</h3>
              </div>
              <span className={`badge ${getBadgeStyle(col.category)}`}>
                {col.items.length} Modules
              </span>
            </div>

            <ul className="status-item-list">
              {col.items.map((item, idx) => (
                <li key={idx} className="status-item">
                  <div className="status-indicator">
                    {col.category === 'Completed' ? (
                      <span className="bullet-done">✓</span>
                    ) : col.category === 'In Progress' ? (
                      <span className="bullet-prog">○</span>
                    ) : (
                      <span className="bullet-future">◇</span>
                    )}
                  </div>
                  <span className="status-item-text">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <style>{`
        .status-column-card {
          padding: 1.5rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .status-column-card.status-emerald {
          border-top: 3px solid var(--accent-emerald);
        }

        .status-column-card.status-amber {
          border-top: 3px solid var(--accent-amber);
        }

        .status-column-card.status-cyan {
          border-top: 3px solid var(--accent-cyan);
        }

        .status-col-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          border-bottom: 1px solid rgba(255, 255, 255, 0.06);
          padding-bottom: 0.75rem;
        }

        .status-title-wrap {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .status-col-title {
          font-size: 1rem;
          font-weight: 700;
          color: #fff;
        }

        .status-item-list {
          list-style: none;
          display: flex;
          flex-direction: column;
          gap: 0.65rem;
          margin: 0;
          padding: 0;
        }

        .status-item {
          display: flex;
          align-items: flex-start;
          gap: 0.6rem;
          font-size: 0.8rem;
          line-height: 1.45;
          color: #cbd5e1;
        }

        .status-indicator {
          font-family: var(--font-mono);
          font-weight: 700;
          flex-shrink: 0;
          margin-top: 1px;
        }

        .bullet-done {
          color: var(--accent-emerald);
        }

        .bullet-prog {
          color: var(--accent-amber);
        }

        .bullet-future {
          color: var(--accent-cyan);
        }

        .status-item-text {
          color: #e2e8f0;
        }
      `}</style>
    </section>
  );
}
