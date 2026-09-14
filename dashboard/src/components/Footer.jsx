import React from 'react';
import { 
  GitBranch, 
  Layers, 
  ShieldCheck, 
  Code2, 
  Terminal, 
  FileText,
  Radio
} from 'lucide-react';
import { BENCHMARK_METADATA } from '../data/benchmarkData';

export default function Footer() {
  return (
    <footer className="footer-root">
      <div className="footer-container">
        {/* Brand and Summary */}
        <div className="footer-brand-col">
          <div className="footer-logo">
            <Radio size={20} className="text-cyan-400" />
            <span className="footer-title">{BENCHMARK_METADATA.projectName}</span>
            <span className="version-pill">v2.5D</span>
          </div>
          <p className="footer-desc">
            {BENCHMARK_METADATA.projectConcept}. Empirical benchmarking and spatial evaluation suite 
            validating 2.5D elevation representations for autonomous driving perception.
          </p>
          <div className="footer-badges">
            <span className="badge badge-amber">{BENCHMARK_METADATA.statusBadge}</span>
            <span className="branch-tag">
              <GitBranch size={11} />
              {BENCHMARK_METADATA.branch}
            </span>
          </div>
        </div>

        {/* Evaluation Details */}
        <div className="footer-col">
          <h4 className="footer-col-title">Evaluation Authorship</h4>
          <ul className="footer-link-list">
            <li><strong>Lead:</strong> {BENCHMARK_METADATA.author}</li>
            <li><strong>Domain:</strong> {BENCHMARK_METADATA.role}</li>
            <li><strong>Methodology:</strong> Multi-run empirical statistics (N=10)</li>
            <li><strong>Input:</strong> Deterministic synthetic LiDAR (10k pts)</li>
          </ul>
        </div>

        {/* Benchmark Files */}
        <div className="footer-col">
          <h4 className="footer-col-title">Benchmark Source Suite</h4>
          <ul className="footer-link-list mono-links">
            <li><code>benchmark/benchmark.py</code></li>
            <li><code>benchmark/benchmark_scaling.py</code></li>
            <li><code>benchmark/uniform_grid.py</code></li>
            <li><code>benchmark/adaptive_grid.py</code></li>
            <li><code>benchmark/results/*.csv</code></li>
          </ul>
        </div>
      </div>

      <div className="footer-bottom">
        <div className="footer-bottom-content">
          <span>NOVA-2.5D Research Project • Academic Evaluation Dashboard</span>
          <span>Git Branch: <code>{BENCHMARK_METADATA.branch}</code> • No Fabricated Data Rule Enforced</span>
        </div>
      </div>

      <style>{`
        .footer-root {
          background: #050810;
          border-top: 1px solid rgba(255, 255, 255, 0.08);
          padding-top: 3rem;
          margin-top: 4rem;
        }

        .footer-container {
          max-width: 1440px;
          margin: 0 auto;
          padding: 0 2rem 2.5rem 2rem;
          display: grid;
          grid-template-columns: 2fr 1fr 1fr;
          gap: 3rem;
        }

        .footer-logo {
          display: flex;
          align-items: center;
          gap: 0.65rem;
          margin-bottom: 0.75rem;
        }

        .footer-title {
          font-size: 1.15rem;
          font-weight: 800;
          color: #fff;
          letter-spacing: -0.02em;
        }

        .footer-desc {
          font-size: 0.82rem;
          color: var(--text-secondary);
          line-height: 1.55;
          max-width: 480px;
          margin-bottom: 1rem;
        }

        .footer-badges {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          flex-wrap: wrap;
        }

        .footer-col-title {
          font-size: 0.82rem;
          font-weight: 700;
          color: #fff;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          margin-bottom: 0.85rem;
          font-family: var(--font-mono);
        }

        .footer-link-list {
          list-style: none;
          display: flex;
          flex-direction: column;
          gap: 0.45rem;
          font-size: 0.8rem;
          color: var(--text-secondary);
        }

        .footer-link-list strong {
          color: #fff;
        }

        .mono-links code {
          font-family: var(--font-mono);
          font-size: 0.75rem;
          color: var(--accent-cyan);
        }

        .footer-bottom {
          border-top: 1px solid rgba(255, 255, 255, 0.04);
          padding: 1.25rem 2rem;
          background: rgba(0, 0, 0, 0.4);
        }

        .footer-bottom-content {
          max-width: 1440px;
          margin: 0 auto;
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 0.75rem;
          color: var(--text-muted);
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .footer-bottom-content code {
          font-family: var(--font-mono);
          color: var(--accent-cyan);
        }

        @media (max-width: 900px) {
          .footer-container {
            grid-template-columns: 1fr;
            gap: 2rem;
          }
        }
      `}</style>
    </footer>
  );
}
