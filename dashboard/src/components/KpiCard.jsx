import React from 'react';

export default function KpiCard({
  title,
  value,
  unit,
  subtitle,
  stdDev,
  accentColor = "cyan", // cyan, emerald, amber, purple, blue
  badge,
  icon: Icon
}) {
  const colorMap = {
    cyan: { text: "var(--accent-cyan)", bg: "var(--accent-cyan-glow)", border: "rgba(6, 182, 212, 0.3)" },
    emerald: { text: "var(--accent-emerald)", bg: "var(--accent-emerald-glow)", border: "rgba(16, 185, 129, 0.3)" },
    amber: { text: "var(--accent-amber)", bg: "var(--accent-amber-glow)", border: "rgba(245, 158, 11, 0.3)" },
    purple: { text: "var(--accent-purple)", bg: "var(--accent-purple-glow)", border: "rgba(139, 92, 246, 0.3)" },
    blue: { text: "var(--accent-blue)", bg: "rgba(59, 130, 246, 0.15)", border: "rgba(59, 130, 246, 0.3)" }
  };

  const currentTheme = colorMap[accentColor] || colorMap.cyan;

  return (
    <div className="glass-card kpi-card-root">
      <div className="kpi-header">
        <span className="kpi-title">{title}</span>
        {Icon && (
          <div 
            className="kpi-icon-wrap"
            style={{ 
              backgroundColor: currentTheme.bg,
              borderColor: currentTheme.border,
              color: currentTheme.text 
            }}
          >
            <Icon size={16} />
          </div>
        )}
      </div>

      <div className="kpi-main">
        <span className="kpi-value">{value}</span>
        {unit && <span className="kpi-unit">{unit}</span>}
      </div>

      <div className="kpi-footer">
        {stdDev && (
          <span className="kpi-std-dev">
            <span className="plus-minus">±</span>{stdDev} {unit} σ
          </span>
        )}
        {subtitle && <span className="kpi-subtitle">{subtitle}</span>}
        {badge && (
          <span className="kpi-badge" style={{ color: currentTheme.text, borderColor: currentTheme.border }}>
            {badge}
          </span>
        )}
      </div>

      <style>{`
        .kpi-card-root {
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          padding: 1.25rem 1.4rem;
        }

        .kpi-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 0.75rem;
        }

        .kpi-title {
          font-size: 0.8rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: var(--text-secondary);
          font-weight: 600;
        }

        .kpi-icon-wrap {
          width: 30px;
          height: 30px;
          border-radius: 8px;
          border: 1px solid transparent;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .kpi-main {
          display: flex;
          align-items: baseline;
          gap: 0.35rem;
          margin-bottom: 0.5rem;
        }

        .kpi-value {
          font-family: var(--font-mono);
          font-size: 1.9rem;
          font-weight: 700;
          color: #fff;
          letter-spacing: -0.03em;
          line-height: 1;
        }

        .kpi-unit {
          font-family: var(--font-mono);
          font-size: 0.95rem;
          color: var(--text-muted);
          font-weight: 500;
        }

        .kpi-footer {
          display: flex;
          align-items: center;
          justify-content: space-between;
          flex-wrap: wrap;
          gap: 0.4rem;
          font-size: 0.75rem;
          color: var(--text-muted);
        }

        .kpi-std-dev {
          font-family: var(--font-mono);
          color: #cbd5e1;
          background: rgba(255, 255, 255, 0.05);
          padding: 0.15rem 0.45rem;
          border-radius: 4px;
        }

        .plus-minus {
          color: var(--text-muted);
          margin-right: 2px;
        }

        .kpi-subtitle {
          color: var(--text-secondary);
        }

        .kpi-badge {
          font-family: var(--font-mono);
          font-size: 0.68rem;
          padding: 0.1rem 0.4rem;
          border-radius: 4px;
          border: 1px solid transparent;
          background: rgba(255, 255, 255, 0.03);
        }
      `}</style>
    </div>
  );
}
