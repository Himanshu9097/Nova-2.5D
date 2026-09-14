import React from 'react';
import { 
  Activity, 
  Layers, 
  Cpu, 
  Clock, 
  Box, 
  Info, 
  ShieldAlert,
  Sparkles,
  Database
} from 'lucide-react';
import KpiCard from './KpiCard';
import { useBenchmark } from '../context/BenchmarkContext';

export default function OverviewSection() {
  const { activeDataset, isDemo } = useBenchmark();

  const datasetName = activeDataset?.dataset?.name || "Synthetic LiDAR Scene";
  const points = activeDataset?.dataset?.points || 10000;
  const uniformRes = activeDataset?.dataset?.uniform_resolution || 0.5;

  const u = activeDataset?.uniform || {
    cells_mean: 3322,
    cells_std: 0,
    fps_mean: 21.14,
    fps_std: 5.09,
    latency_mean: 49.840,
    latency_std: 11.980,
    runs_count: 10
  };

  const a = activeDataset?.adaptive || {
    cells_mean: 3560,
    cells_std: 0,
    fps_mean: 13.95,
    fps_std: 3.83,
    latency_mean: 77.852,
    latency_std: 25.578,
    runs_count: 10
  };

  return (
    <section id="overview" className="section-container">
      {/* Title block */}
      <div className="section-header">
        <div className="section-title-group">
          <div className="section-tag">
            <Activity size={14} />
            Active Benchmark Telemetry
          </div>
          <h1 className="section-title">
            {datasetName}
          </h1>
          <p className="section-desc">
            Comparative spatial occupancy, execution latency, and throughput evaluation between 
            fixed-resolution uniform grid discretization and prototype adaptive variable-resolution policy.
          </p>
        </div>
        <div className="header-meta">
          {isDemo ? (
            <span className="badge badge-amber">
              <ShieldAlert size={13} />
              DEMO DATASET • SYNTHETIC LiDAR
            </span>
          ) : (
            <span className="badge badge-emerald">
              <Sparkles size={13} />
              USER DATASET • LIVE BENCHMARK RESULT
            </span>
          )}
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid-4" style={{ marginBottom: '1.25rem' }}>
        <KpiCard 
          title="Point Cloud Size"
          value={points.toLocaleString()}
          unit="pts"
          subtitle="Input coordinate buffer"
          accentColor="cyan"
          icon={Box}
          badge={isDemo ? "Deterministic Seed 42" : "Custom Ingestion"}
        />
        <KpiCard 
          title="Uniform Grid Cells"
          value={Math.round(u.cells_mean).toLocaleString()}
          unit="cells"
          subtitle={`${uniformRes}m fixed grid cell size`}
          accentColor="blue"
          icon={Layers}
          badge={`Res = ${uniformRes.toFixed(2)}m`}
        />
        <KpiCard 
          title="Adaptive Grid Cells"
          value={Math.round(a.cells_mean).toLocaleString()}
          unit="cells"
          subtitle="Prototype policy (0.25m - 1.0m)"
          accentColor="purple"
          icon={Layers}
          badge="Variable Resolution"
        />
        <KpiCard 
          title="Benchmark Iterations"
          value={u.runs_count || 10}
          unit="runs"
          subtitle="Empirical statistical suite"
          accentColor="emerald"
          icon={Activity}
          badge="Multi-Run Validated"
        />
      </div>

      {/* Secondary KPI Grid (Throughput & Latency) */}
      <div className="grid-4" style={{ marginBottom: '1.5rem' }}>
        <KpiCard 
          title="Uniform Mean FPS"
          value={u.fps_mean.toFixed(2)}
          unit="FPS"
          stdDev={u.fps_std ? u.fps_std.toFixed(2) : undefined}
          subtitle="Direct O(1) floor indexing"
          accentColor="emerald"
          icon={Cpu}
        />
        <KpiCard 
          title="Adaptive Mean FPS"
          value={a.fps_mean.toFixed(2)}
          unit="FPS"
          stdDev={a.fps_std ? a.fps_std.toFixed(2) : undefined}
          subtitle="Interpreted prototype heuristic"
          accentColor="amber"
          icon={Cpu}
        />
        <KpiCard 
          title="Uniform Mean Latency"
          value={u.latency_mean.toFixed(3)}
          unit="ms"
          stdDev={u.latency_std ? u.latency_std.toFixed(3) : undefined}
          subtitle="Rasterization time per frame"
          accentColor="blue"
          icon={Clock}
        />
        <KpiCard 
          title="Adaptive Mean Latency"
          value={a.latency_mean.toFixed(3)}
          unit="ms"
          stdDev={a.latency_std ? a.latency_std.toFixed(3) : undefined}
          subtitle="Distance + semantic branching"
          accentColor="purple"
          icon={Clock}
        />
      </div>

      {/* Neutral Scientific Baseline Notice */}
      <div className="glass-card overview-notice-card">
        <div className="notice-header">
          <div className="notice-icon-glow">
            <Info size={18} className="text-cyan-400" />
          </div>
          <div>
            <h3 className="notice-title">Baseline Comparison Protocol & Methodology Notice</h3>
            <span className="notice-subtitle">Preliminary Benchmark Architecture • Academic Rigor</span>
          </div>
        </div>

        <p className="notice-body">
          <strong>Neutral Evaluation Baseline:</strong> The current benchmark measures a prototype/dummy 
          adaptive resolution policy written in Python to validate the measurement harness, CSV logging pipeline, 
          and statistical evaluation framework. Under this active dataset, the Uniform Grid achieves 
          <strong> {u.fps_mean.toFixed(2)} FPS ({u.latency_mean.toFixed(2)} ms)</strong> compared to the Prototype Adaptive Grid's <strong>{a.fps_mean.toFixed(2)} FPS ({a.latency_mean.toFixed(2)} ms)</strong>.
        </p>

        <div className="notice-pills">
          <div className="notice-pill">
            <span className="pill-dot"></span>
            <span>Current Adaptive algorithm is a prototype policy for testbed validation</span>
          </div>
          <div className="notice-pill">
            <span className="pill-dot"></span>
            <span>Will be replaced by high-performance C++/Cython Adaptive Grid Engine</span>
          </div>
          <div className="notice-pill">
            <span className="pill-dot"></span>
            <span>Upload custom point cloud datasets to run benchmarks on custom scenes</span>
          </div>
        </div>
      </div>

      <style>{`
        .overview-notice-card {
          border-left: 3px solid var(--accent-cyan);
          background: linear-gradient(135deg, rgba(6, 182, 212, 0.05) 0%, rgba(16, 24, 40, 0.85) 100%);
        }

        .notice-header {
          display: flex;
          align-items: center;
          gap: 0.85rem;
          margin-bottom: 0.85rem;
        }

        .notice-icon-glow {
          width: 34px;
          height: 34px;
          border-radius: 8px;
          background: rgba(6, 182, 212, 0.15);
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--accent-cyan);
        }

        .notice-title {
          font-size: 1rem;
          font-weight: 700;
          color: #fff;
          letter-spacing: -0.01em;
        }

        .notice-subtitle {
          font-size: 0.75rem;
          color: var(--text-muted);
          font-family: var(--font-mono);
        }

        .notice-body {
          font-size: 0.88rem;
          color: #cbd5e1;
          line-height: 1.6;
          margin-bottom: 1rem;
        }

        .notice-body strong {
          color: #fff;
        }

        .notice-pills {
          display: flex;
          flex-wrap: wrap;
          gap: 0.6rem;
        }

        .notice-pill {
          display: flex;
          align-items: center;
          gap: 0.45rem;
          background: rgba(255, 255, 255, 0.04);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 9999px;
          padding: 0.25rem 0.75rem;
          font-size: 0.78rem;
          color: #e2e8f0;
        }

        .pill-dot {
          width: 5px;
          height: 5px;
          border-radius: 50%;
          background: var(--accent-cyan);
        }
      `}</style>
    </section>
  );
}
