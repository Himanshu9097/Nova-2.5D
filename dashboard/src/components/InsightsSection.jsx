import React from 'react';
import { 
  Lightbulb, 
  CheckCircle2, 
  AlertTriangle, 
  TrendingUp, 
  Layers, 
  Cpu, 
  ShieldCheck, 
  ArrowRight,
  Info
} from 'lucide-react';
import { RESEARCH_INSIGHTS } from '../data/benchmarkData';

export default function InsightsSection() {
  const getInsightStyle = (type) => {
    switch (type) {
      case 'success':
        return {
          border: 'rgba(16, 185, 129, 0.4)',
          badgeClass: 'badge-emerald',
          icon: CheckCircle2,
          iconColor: 'var(--accent-emerald)'
        };
      case 'warning':
        return {
          border: 'rgba(245, 158, 11, 0.4)',
          badgeClass: 'badge-amber',
          icon: AlertTriangle,
          iconColor: 'var(--accent-amber)'
        };
      case 'info':
        return {
          border: 'rgba(6, 182, 212, 0.4)',
          badgeClass: 'badge-cyan',
          icon: Info,
          iconColor: 'var(--accent-cyan)'
        };
      case 'milestone':
        return {
          border: 'rgba(139, 92, 246, 0.4)',
          badgeClass: 'badge-purple',
          icon: ShieldCheck,
          iconColor: 'var(--accent-purple)'
        };
      default:
        return {
          border: 'var(--card-border)',
          badgeClass: 'badge-neutral',
          icon: Info,
          iconColor: 'var(--text-muted)'
        };
    }
  };

  return (
    <section id="insights" className="section-container">
      <div className="section-header">
        <div className="section-title-group">
          <div className="section-tag">
            <Lightbulb size={14} />
            Empirical Findings & Research Takeaways
          </div>
          <h2 className="section-title">
            Current Findings & Baseline Synthesis
          </h2>
          <p className="section-desc">
            Evidence-based conclusions drawn strictly from actual recorded benchmark results.
            Establishes the empirical foundation for upcoming optimization iterations.
          </p>
        </div>

        <div className="header-meta">
          <span className="badge badge-emerald">
            Evidence-Based Analysis
          </span>
        </div>
      </div>

      <div className="insights-cards-list">
        {RESEARCH_INSIGHTS.map((insight, idx) => {
          const style = getInsightStyle(insight.type);
          const IconComponent = style.icon;

          return (
            <div 
              key={idx} 
              className="glass-card insight-item-card"
              style={{ borderLeftColor: style.iconColor }}
            >
              <div className="insight-card-top">
                <div className="insight-icon-wrap" style={{ color: style.iconColor }}>
                  <IconComponent size={18} />
                </div>
                <h3 className="insight-item-title">{insight.title}</h3>
                <span className={`badge ${style.badgeClass}`} style={{ marginLeft: 'auto' }}>
                  {insight.status}
                </span>
              </div>

              <p className="insight-content-text">{insight.content}</p>
            </div>
          );
        })}
      </div>

      {/* Synthesis Conclusion Box */}
      <div className="glass-card conclusion-box" style={{ marginTop: '1.5rem' }}>
        <h4 className="concl-title">Executive Scientific Conclusion</h4>
        <p className="concl-text">
          Rather than viewing the prototype Adaptive Grid as underperforming, the empirical data 
          demonstrates that <strong>the current prototype provides an essential baseline for optimization and final engine evaluation</strong>. 
          By isolating the computational cost of interpreted per-point distance calculations in pure Python, 
          the benchmark proves where acceleration is required (C++/CUDA spatial indexing) and validates the complete telemetry logging and evaluation harness ahead of full CARLA deployment.
        </p>
      </div>

      <style>{`
        .insights-cards-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .insight-item-card {
          padding: 1.25rem 1.5rem;
          border-left-width: 4px;
          display: flex;
          flex-direction: column;
          gap: 0.6rem;
        }

        .insight-card-top {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .insight-icon-wrap {
          flex-shrink: 0;
        }

        .insight-item-title {
          font-size: 0.95rem;
          font-weight: 700;
          color: #fff;
        }

        .insight-content-text {
          font-size: 0.84rem;
          color: #cbd5e1;
          line-height: 1.6;
        }

        .conclusion-box {
          border-top: 3px solid var(--accent-emerald);
          padding: 1.5rem 1.75rem;
          background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(16, 24, 40, 0.8) 100%);
        }

        .concl-title {
          font-size: 1.05rem;
          font-weight: 800;
          color: #fff;
          margin-bottom: 0.5rem;
        }

        .concl-text {
          font-size: 0.88rem;
          color: #cbd5e1;
          line-height: 1.6;
        }

        .concl-text strong {
          color: #fff;
        }
      `}</style>
    </section>
  );
}
