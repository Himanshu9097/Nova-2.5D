import React, { useState } from 'react';
import { 
  GitMerge, 
  CheckCircle2, 
  Clock, 
  ArrowDown, 
  ArrowRight, 
  Cpu, 
  Layers, 
  BarChart3, 
  Eye, 
  Zap, 
  Car, 
  Radio, 
  BrainCircuit, 
  Compass,
  ChevronRight
} from 'lucide-react';

export default function PipelineSection() {
  const [pipelineView, setPipelineView] = useState('both'); // 'both', 'benchmark', 'full'

  const benchmarkSteps = [
    {
      id: 1,
      title: "Synthetic LiDAR Testbed",
      subtitle: "Deterministic 10,000 pts (seed 42)",
      status: "implemented",
      icon: Radio,
      details: "5-channel synthetic point cloud [x, y, z, intensity, class] generated via NumPy."
    },
    {
      id: 2,
      title: "Point Cloud Ingestion",
      subtitle: "Array memory representation",
      status: "implemented",
      icon: Layers,
      details: "In-memory structured buffer passed into discretization algorithms."
    },
    {
      id: 3,
      title: "Discretization Dual-Branch",
      subtitle: "Uniform (0.5m) vs Prototype Adaptive",
      status: "implemented",
      icon: GitMerge,
      details: "Parallel benchmarking of fixed floor hashing vs variable distance/semantic hashing."
    },
    {
      id: 4,
      title: "2.5D Elevation Rasterization",
      subtitle: "Max-height + Semantic accumulation",
      status: "implemented",
      icon: Layers,
      details: "Cell hash mapping maintaining maximum Z elevation and semantic class occurrences."
    },
    {
      id: 5,
      title: "Empirical Metrics Instrumentation",
      subtitle: "perf_counter & psutil RSS",
      status: "implemented",
      icon: Zap,
      details: "Sub-millisecond execution duration, frames-per-second, and process memory delta."
    },
    {
      id: 6,
      title: "Statistical Aggregation",
      subtitle: "10-run Mean & Std Dev",
      status: "implemented",
      icon: BarChart3,
      details: "Automated CSV logging to multi_run_benchmark.csv and scaling_benchmark.csv."
    },
    {
      id: 7,
      title: "Visualization & Web Dashboard",
      subtitle: "Matplotlib & React Interface",
      status: "implemented",
      icon: Eye,
      details: "Interactive visual analytics and publication-grade comparison graphics."
    }
  ];

  const fullArchitecture = [
    { name: "CARLA Simulator", status: "future", type: "Simulation", desc: "Autonomous driving simulation platform" },
    { name: "Virtual Spinning LiDAR", status: "future", type: "Sensor", desc: "Multi-channel simulated LiDAR beam packet stream" },
    { name: "Point Cloud Streaming", status: "future", type: "Input", desc: "Real-time coordinate point buffer" },
    { name: "Point Cloud Preprocessing", status: "future", type: "Filter", desc: "Ground removal, range clipping & voxel filtering" },
    { name: "Semantic AI Inference", status: "future", type: "Perception", desc: "Deep point cloud semantic segmentation" },
    { name: "Dynamic Object Tracking", status: "future", type: "Tracking", desc: "Kalman filtering & tracklet velocity estimation" },
    { name: "Adaptive Grid Engine", status: "future", type: "Core Engine", desc: "Optimized C++/CUDA variable resolution engine" },
    { name: "Semantic 2.5D Elevation Map", status: "future", type: "Output", desc: "Continuous variable-resolution top-down map" },
    { name: "Empirical Benchmark & Evaluation", status: "implemented", type: "Validation", desc: "Standardized performance & fidelity benchmarking suite (Current Work)" }
  ];

  return (
    <section id="pipeline" className="section-container">
      <div className="section-header">
        <div className="section-title-group">
          <div className="section-tag">
            <GitMerge size={14} />
            System Architecture & Evaluation Flow
          </div>
          <h2 className="section-title">
            Processing & Evaluation Pipelines
          </h2>
          <p className="section-desc">
            Visualizing the currently executed benchmark evaluation workflow alongside the 
            target end-to-end NOVA-2.5D autonomous vehicle system architecture.
          </p>
        </div>

        {/* View Toggle */}
        <div className="pipeline-toggle">
          <button 
            className={`toggle-btn ${pipelineView === 'both' ? 'active' : ''}`}
            onClick={() => setPipelineView('both')}
          >
            All Pipelines
          </button>
          <button 
            className={`toggle-btn ${pipelineView === 'benchmark' ? 'active' : ''}`}
            onClick={() => setPipelineView('benchmark')}
          >
            Benchmark Flow
          </button>
          <button 
            className={`toggle-btn ${pipelineView === 'full' ? 'active' : ''}`}
            onClick={() => setPipelineView('full')}
          >
            Full Architecture
          </button>
        </div>
      </div>

      {/* Distinction Banner */}
      <div className="pipeline-legend-strip">
        <div className="legend-item">
          <span className="badge badge-emerald">
            <CheckCircle2 size={12} />
            CURRENTLY IMPLEMENTED
          </span>
          <span className="legend-desc">Fully functional in benchmark/ with deterministic testbed & CSV logs</span>
        </div>
        <div className="legend-item">
          <span className="badge badge-cyan">
            <Clock size={12} />
            FUTURE INTEGRATION
          </span>
          <span className="legend-desc">Planned CARLA + Deep Learning + C++ Engine deployment</span>
        </div>
      </div>

      <div className="pipelines-wrapper">
        {/* PIPELINE 1: Current Benchmark Flow */}
        {(pipelineView === 'both' || pipelineView === 'benchmark') && (
          <div className="glass-card pipeline-card">
            <div className="card-top-title">
              <div className="pipe-badge-wrap">
                <span className="badge badge-emerald">CURRENTLY IMPLEMENTED</span>
              </div>
              <h3 className="pipe-heading">Benchmark Evaluation Pipeline</h3>
              <p className="pipe-sub">Operational workflow executed by <code style={{ color: 'var(--accent-cyan)' }}>benchmark.py</code> and <code style={{ color: 'var(--accent-cyan)' }}>benchmark_scaling.py</code></p>
            </div>

            <div className="step-pipeline-list">
              {benchmarkSteps.map((step, idx) => {
                const IconComponent = step.icon;
                return (
                  <div key={step.id} className="pipe-step-item">
                    <div className="pipe-step-num-col">
                      <div className="pipe-circle active">
                        <IconComponent size={14} />
                      </div>
                      {idx < benchmarkSteps.length - 1 && <div className="pipe-line active"></div>}
                    </div>

                    <div className="pipe-content-col">
                      <div className="pipe-title-row">
                        <span className="pipe-step-title">{step.title}</span>
                        <span className="pipe-step-sub">{step.subtitle}</span>
                      </div>
                      <p className="pipe-details">{step.details}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* PIPELINE 2: Overall System Architecture */}
        {(pipelineView === 'both' || pipelineView === 'full') && (
          <div className="glass-card pipeline-card">
            <div className="card-top-title">
              <div className="pipe-badge-wrap">
                <span className="badge badge-purple">SYSTEM ARCHITECTURE</span>
              </div>
              <h3 className="pipe-heading">Overall Autonomous Vehicle Integration Pipeline</h3>
              <p className="pipe-sub">Full target system pipeline from raw sensor input to 2.5D semantic mapping</p>
            </div>

            <div className="architecture-grid">
              {fullArchitecture.map((stage, idx) => (
                <div 
                  key={stage.name} 
                  className={`arch-stage-card ${stage.status === 'implemented' ? 'arch-implemented' : 'arch-future'}`}
                >
                  <div className="arch-card-top">
                    <span className="arch-idx">0{idx + 1}</span>
                    <span className={`badge ${stage.status === 'implemented' ? 'badge-emerald' : 'badge-cyan'}`}>
                      {stage.status === 'implemented' ? 'IMPLEMENTED' : 'PLANNED'}
                    </span>
                  </div>
                  <div className="arch-type">{stage.type}</div>
                  <div className="arch-name">{stage.name}</div>
                  <div className="arch-desc">{stage.desc}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <style>{`
        .pipeline-toggle {
          display: flex;
          background: rgba(15, 23, 42, 0.7);
          border: 1px solid var(--card-border);
          border-radius: var(--radius-sm);
          padding: 3px;
        }

        .toggle-btn {
          background: transparent;
          border: none;
          color: var(--text-secondary);
          font-family: var(--font-sans);
          font-size: 0.8rem;
          font-weight: 500;
          padding: 0.35rem 0.75rem;
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .toggle-btn.active {
          background: var(--accent-cyan);
          color: #070a12;
          font-weight: 700;
        }

        .pipeline-legend-strip {
          display: flex;
          align-items: center;
          gap: 2rem;
          background: rgba(16, 24, 40, 0.5);
          border: 1px solid var(--card-border);
          border-radius: var(--radius-sm);
          padding: 0.75rem 1.25rem;
          margin-bottom: 1.5rem;
          flex-wrap: wrap;
        }

        .legend-item {
          display: flex;
          align-items: center;
          gap: 0.65rem;
        }

        .legend-desc {
          font-size: 0.8rem;
          color: var(--text-secondary);
        }

        .pipelines-wrapper {
          display: grid;
          grid-template-columns: ${pipelineView === 'both' ? '1fr 1fr' : '1fr'};
          gap: 1.5rem;
        }

        .pipeline-card {
          padding: 1.5rem;
        }

        .card-top-title {
          margin-bottom: 1.25rem;
          border-bottom: 1px solid rgba(255, 255, 255, 0.06);
          padding-bottom: 0.85rem;
        }

        .pipe-badge-wrap {
          margin-bottom: 0.4rem;
        }

        .pipe-heading {
          font-size: 1.05rem;
          font-weight: 700;
          color: #fff;
        }

        .pipe-sub {
          font-size: 0.78rem;
          color: var(--text-muted);
          margin-top: 0.2rem;
        }

        .step-pipeline-list {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .pipe-step-item {
          display: flex;
          gap: 0.85rem;
        }

        .pipe-step-num-col {
          display: flex;
          flex-direction: column;
          align-items: center;
        }

        .pipe-circle {
          width: 28px;
          height: 28px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(16, 185, 129, 0.15);
          border: 1px solid var(--accent-emerald);
          color: var(--accent-emerald);
          flex-shrink: 0;
        }

        .pipe-line {
          width: 2px;
          flex: 1;
          min-height: 22px;
          background: rgba(16, 185, 129, 0.3);
          margin: 3px 0;
        }

        .pipe-content-col {
          padding-bottom: 0.85rem;
          flex: 1;
        }

        .pipe-title-row {
          display: flex;
          align-items: baseline;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .pipe-step-title {
          font-size: 0.88rem;
          font-weight: 600;
          color: #fff;
        }

        .pipe-step-sub {
          font-family: var(--font-mono);
          font-size: 0.72rem;
          color: var(--accent-cyan);
        }

        .pipe-details {
          font-size: 0.76rem;
          color: var(--text-secondary);
          margin-top: 0.15rem;
          line-height: 1.4;
        }

        .architecture-grid {
          display: flex;
          flex-direction: column;
          gap: 0.65rem;
        }

        .arch-stage-card {
          background: rgba(15, 23, 42, 0.6);
          border: 1px solid var(--card-border);
          border-radius: var(--radius-sm);
          padding: 0.75rem 1rem;
          transition: all 0.2s ease;
        }

        .arch-implemented {
          border-left: 3px solid var(--accent-emerald);
          background: rgba(16, 185, 129, 0.05);
        }

        .arch-future {
          border-left: 3px solid rgba(6, 182, 212, 0.5);
        }

        .arch-card-top {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 0.2rem;
        }

        .arch-idx {
          font-family: var(--font-mono);
          font-size: 0.7rem;
          color: var(--text-muted);
        }

        .arch-type {
          font-family: var(--font-mono);
          font-size: 0.68rem;
          color: var(--accent-cyan);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .arch-name {
          font-size: 0.88rem;
          font-weight: 700;
          color: #fff;
          margin-bottom: 0.15rem;
        }

        .arch-desc {
          font-size: 0.75rem;
          color: var(--text-secondary);
        }

        @media (max-width: 1024px) {
          .pipelines-wrapper {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </section>
  );
}
