import React, { useState } from 'react';
import { 
  Layers, 
  Activity, 
  UploadCloud,
  Map,
  History,
  GitBranch, 
  AlertTriangle,
  Menu,
  X,
  Server,
  RotateCcw,
  Sparkles
} from 'lucide-react';
import { BENCHMARK_METADATA } from '../data/benchmarkData';
import { useBenchmark } from '../context/BenchmarkContext';

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { isDemo, activeDataset, resetToDemo, backendOnline } = useBenchmark();

  const navLinks = [
    { label: 'Overview', href: '#overview' },
    { label: 'Run Benchmark', href: '#run-benchmark', highlight: true },
    { label: 'Input Data', href: '#input-data' },
    { label: 'Pipeline', href: '#pipeline' },
    { label: 'Grid Methods', href: '#grid-methods' },
    { label: 'Comparison', href: '#comparison' },
    { label: 'Run-by-Run', href: '#multi-run' },
    { label: 'Output Map', href: '#output-map' },
    { label: 'Scaling', href: '#scaling' },
    { label: 'History', href: '#history' },
    { label: 'Status', href: '#status' },
    { label: 'Insights', href: '#insights' }
  ];

  return (
    <header className="navbar-root">
      {/* Top Advisory Banner */}
      <div className="advisory-strip">
        <div className="advisory-content">
          <div className="advisory-left">
            {isDemo ? (
              <span className="badge badge-amber">
                <AlertTriangle size={12} className="text-amber-400" />
                DEMO DATASET • SYNTHETIC LiDAR
              </span>
            ) : (
              <div className="active-user-dataset-pill">
                <span className="pulse-dot" style={{ color: 'var(--accent-emerald)' }}></span>
                <span>Active Dataset: <strong>{activeDataset?.dataset?.name}</strong></span>
                <button className="reset-inline-btn" onClick={resetToDemo} title="Return to synthetic baseline">
                  <RotateCcw size={11} />
                  Reset to Baseline
                </button>
              </div>
            )}
            <span className="advisory-text">
              {isDemo 
                ? "Initial synthetic testbed loaded. Upload custom point-clouds below to benchmark live." 
                : `Live empirical evaluation on ${activeDataset?.dataset?.points?.toLocaleString()} points.`}
            </span>
          </div>

          <div className="advisory-right">
            <span className={`backend-indicator ${backendOnline ? 'online' : 'offline'}`}>
              <span className="pulse-dot" style={{ color: backendOnline ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}></span>
              <span>API: {backendOnline ? 'Online (Port 8000)' : 'Connecting...'}</span>
            </span>
            <span className="branch-tag">
              <GitBranch size={12} />
              {BENCHMARK_METADATA.branch}
            </span>
          </div>
        </div>
      </div>

      {/* Main Navbar */}
      <div className="nav-container">
        <div className="nav-brand">
          <a href="#overview" className="brand-link">
            <div className="brand-logo-glow">
              <Layers size={22} className="brand-icon" />
            </div>
            <div className="brand-text">
              <div className="brand-title">
                {BENCHMARK_METADATA.projectName}
                <span className="version-pill">v2.5D</span>
              </div>
              <div className="brand-subtitle">{BENCHMARK_METADATA.subtitle}</div>
            </div>
          </a>
        </div>

        {/* Author Badge */}
        <div className="author-badge-container">
          <div className="author-pill">
            <span className="pulse-dot" style={{ color: 'var(--accent-cyan)' }}></span>
            <span className="author-name">{BENCHMARK_METADATA.author}</span>
            <span className="author-role">• {BENCHMARK_METADATA.role}</span>
          </div>
        </div>

        {/* Desktop Nav Links */}
        <nav className="desktop-nav">
          {navLinks.map((link) => (
            <a 
              key={link.href} 
              href={link.href}
              className={`nav-item ${link.highlight ? 'nav-highlight' : ''}`}
            >
              {link.label}
            </a>
          ))}
        </nav>

        {/* Mobile menu button */}
        <button 
          className="mobile-menu-btn"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle navigation menu"
        >
          {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="mobile-drawer">
          {navLinks.map((link) => (
            <a 
              key={link.href} 
              href={link.href}
              className="mobile-nav-item"
              onClick={() => setMobileMenuOpen(false)}
            >
              {link.label}
            </a>
          ))}
        </div>
      )}

      <style>{`
        .navbar-root {
          position: sticky;
          top: 0;
          z-index: 50;
          background: rgba(7, 10, 18, 0.94);
          backdrop-filter: blur(14px);
          -webkit-backdrop-filter: blur(14px);
          border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }

        .advisory-strip {
          background: linear-gradient(90deg, rgba(245, 158, 11, 0.1) 0%, rgba(6, 182, 212, 0.08) 50%, rgba(139, 92, 246, 0.08) 100%);
          border-bottom: 1px solid rgba(245, 158, 11, 0.2);
          padding: 0.35rem 1.5rem;
          font-size: 0.75rem;
        }

        .advisory-content {
          max-width: 1440px;
          margin: 0 auto;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 1rem;
        }

        .advisory-left {
          display: flex;
          align-items: center;
          gap: 0.85rem;
        }

        .advisory-right {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .advisory-text {
          color: #cbd5e1;
          font-size: 0.76rem;
          font-weight: 500;
        }

        .active-user-dataset-pill {
          display: flex;
          align-items: center;
          gap: 0.45rem;
          background: rgba(16, 185, 129, 0.12);
          border: 1px solid rgba(16, 185, 129, 0.35);
          color: #6ee7b7;
          font-size: 0.72rem;
          padding: 0.2rem 0.55rem;
          border-radius: 9999px;
        }

        .reset-inline-btn {
          background: rgba(0, 0, 0, 0.3);
          border: 1px solid rgba(255, 255, 255, 0.1);
          color: #fff;
          font-size: 0.68rem;
          padding: 0.15rem 0.45rem;
          border-radius: 4px;
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          gap: 0.25rem;
          margin-left: 0.3rem;
        }

        .reset-inline-btn:hover {
          background: rgba(245, 158, 11, 0.3);
          color: #fbbf24;
        }

        .backend-indicator {
          display: flex;
          align-items: center;
          gap: 0.35rem;
          font-family: var(--font-mono);
          font-size: 0.7rem;
        }

        .backend-indicator.online {
          color: #34d399;
        }

        .backend-indicator.offline {
          color: #fb7185;
        }

        .branch-tag {
          display: flex;
          align-items: center;
          gap: 0.3rem;
          font-family: var(--font-mono);
          font-size: 0.72rem;
          color: var(--accent-cyan);
          background: rgba(6, 182, 212, 0.1);
          padding: 0.15rem 0.5rem;
          border-radius: 4px;
          border: 1px solid rgba(6, 182, 212, 0.25);
        }

        .nav-container {
          max-width: 1440px;
          margin: 0 auto;
          padding: 0.75rem 1.5rem;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 1.5rem;
        }

        .nav-brand {
          display: flex;
          align-items: center;
        }

        .brand-link {
          display: flex;
          align-items: center;
          gap: 0.85rem;
          text-decoration: none;
          color: inherit;
        }

        .brand-logo-glow {
          width: 38px;
          height: 38px;
          border-radius: 10px;
          background: linear-gradient(135deg, rgba(6, 182, 212, 0.25) 0%, rgba(59, 130, 246, 0.1) 100%);
          border: 1px solid rgba(6, 182, 212, 0.4);
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 0 12px rgba(6, 182, 212, 0.3);
        }

        .brand-icon {
          color: var(--accent-cyan);
        }

        .brand-title {
          font-size: 1.15rem;
          font-weight: 800;
          letter-spacing: -0.02em;
          color: #fff;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .version-pill {
          font-family: var(--font-mono);
          font-size: 0.65rem;
          background: rgba(6, 182, 212, 0.15);
          color: var(--accent-cyan);
          padding: 0.1rem 0.4rem;
          border-radius: 4px;
          border: 1px solid rgba(6, 182, 212, 0.3);
        }

        .brand-subtitle {
          font-size: 0.72rem;
          color: var(--text-muted);
          font-weight: 500;
          letter-spacing: 0.03em;
        }

        .author-pill {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: rgba(16, 24, 40, 0.8);
          border: 1px solid rgba(255, 255, 255, 0.08);
          padding: 0.35rem 0.75rem;
          border-radius: 9999px;
          font-size: 0.78rem;
        }

        .author-name {
          color: #fff;
          font-weight: 600;
        }

        .author-role {
          color: var(--text-secondary);
        }

        .desktop-nav {
          display: flex;
          align-items: center;
          gap: 0.25rem;
        }

        .nav-item {
          color: var(--text-secondary);
          text-decoration: none;
          font-size: 0.8rem;
          font-weight: 500;
          padding: 0.35rem 0.55rem;
          border-radius: var(--radius-sm);
          transition: all 0.2s ease;
          white-space: nowrap;
        }

        .nav-item:hover {
          color: #fff;
          background: rgba(255, 255, 255, 0.06);
        }

        .nav-item.nav-highlight {
          color: var(--accent-cyan);
          background: rgba(6, 182, 212, 0.12);
          border: 1px solid rgba(6, 182, 212, 0.3);
          font-weight: 600;
        }

        .mobile-menu-btn {
          display: none;
          background: transparent;
          border: 1px solid rgba(255, 255, 255, 0.1);
          color: #fff;
          padding: 0.4rem;
          border-radius: var(--radius-sm);
          cursor: pointer;
        }

        .mobile-drawer {
          display: none;
          flex-direction: column;
          background: var(--bg-secondary);
          border-bottom: 1px solid var(--card-border);
          padding: 1rem 1.5rem;
          gap: 0.5rem;
        }

        .mobile-nav-item {
          color: var(--text-secondary);
          text-decoration: none;
          font-size: 0.9rem;
          padding: 0.5rem 0;
          border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        }

        @media (max-width: 1200px) {
          .desktop-nav {
            display: none;
          }
          .author-badge-container {
            display: none;
          }
          .mobile-menu-btn {
            display: block;
          }
          .mobile-drawer {
            display: flex;
          }
          .advisory-text {
            display: none;
          }
        }
      `}</style>
    </header>
  );
}
