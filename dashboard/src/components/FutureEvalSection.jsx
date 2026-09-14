import React from 'react';
import { 
  Compass, 
  Cpu, 
  Target, 
  ShieldCheck, 
  Car, 
  User, 
  Layers, 
  TrendingDown, 
  ArrowRight,
  Sparkles
} from 'lucide-react';

export default function FutureEvalSection() {
  const evalDimensions = [
    {
      title: "Computational Efficiency",
      icon: Cpu,
      color: "cyan",
      metrics: [
        { name: "End-to-End Latency", target: "< 33.3 ms (< 30 Hz real-time loop)" },
        { name: "Throughput (FPS)", target: "30 - 60 FPS continuous streaming" },
        { name: "CPU Utilization", target: "Multi-threaded SIMD / GPU kernel offload" },
        { name: "Dynamic Memory Heap", target: "Zero per-frame allocation with ring buffers" },
        { name: "Occupied Cell Compression", target: "30% - 50% cell reduction in sparse regions" }
      ]
    },
    {
      title: "Mapping Quality & Accuracy",
      icon: Target,
      color: "purple",
      metrics: [
        { name: "Elevation MAE & RMSE", target: "Mean Absolute Error < 2.0 cm on drivable road" },
        { name: "Semantic Segmentation mIoU", target: "> 85% IoU across safety-critical classes" },
        { name: "Class Precision & Recall", target: "High recall on dynamic obstacles to prevent misses" },
        { name: "F1 Score by Class", target: "Harmonic mean of precision & recall per voxel" },
        { name: "Elevation Discontinuity Preservation", target: "Preserve curb, barrier & step geometry" }
      ]
    },
    {
      title: "Object & Safety Retention",
      icon: ShieldCheck,
      color: "emerald",
      metrics: [
        { name: "Vehicle Preservation Ratio", target: "100% vehicle surface points in 0.25m cells" },
        { name: "Pedestrian Silhouette Retention", target: "Fine resolution bound for VRU detection" },
        { name: "Thin Obstacle Retention", target: "Poles, wires, guardrails preserved from downsampling" },
        { name: "Safety Margin Conservation", target: "No coarse merging within ego braking distance" },
        { name: "Dynamic Tracklet Consistency", target: "Velocity vector stability across map updates" }
      ]
    }
  ];

  return (
    <section id="future-eval" className="section-container">
      <div className="section-header">
        <div className="section-title-group">
          <div className="section-tag">
            <Compass size={14} />
            CARLA Simulator & Real-LiDAR Roadmap
          </div>
          <h2 className="section-title">
            Downstream Full-System Evaluation Protocol
          </h2>
          <p className="section-desc">
            The core research hypothesis: can adaptive variable resolution achieve substantial computational savings 
            and cell reduction without sacrificing mapping precision or safety-critical object preservation?
          </p>
        </div>

        <div className="header-meta">
          <span className="badge badge-purple">
            Target Research Evaluation
          </span>
        </div>
      </div>

      {/* Hypothesis Banner */}
      <div className="glass-card hypothesis-card" style={{ marginBottom: '1.5rem' }}>
        <div className="hypo-badge">
          <Sparkles size={14} />
          <span>CENTRAL RESEARCH QUESTION</span>
        </div>
        <h3 className="hypo-title">
          Uniform High-Resolution Map vs Adaptive Variable-Resolution Map
        </h3>
        <p className="hypo-desc">
          When the production C++ Adaptive Grid Engine is fed live 64-channel virtual LiDAR point clouds inside CARLA:
          does multi-resolution spatial hashing reduce cell storage and rasterization latency by <strong>30–50%</strong> 
          while maintaining equal or superior object detection recall compared to a brute-force 0.25m uniform grid?
        </p>
      </div>

      {/* 3 Dimension Cards */}
      <div className="grid-3">
        {evalDimensions.map((dim) => {
          const IconComp = dim.icon;
          return (
            <div key={dim.title} className={`glass-card eval-dim-card dim-${dim.color}`}>
              <div className="dim-header">
                <div className="dim-icon-wrap">
                  <IconComp size={16} />
                </div>
                <h4 className="dim-title">{dim.title}</h4>
              </div>

              <div className="dim-metric-list">
                {dim.metrics.map((m, idx) => (
                  <div key={idx} className="dim-metric-item">
                    <div className="dim-m-name">{m.name}</div>
                    <div className="dim-m-target">
                      <ArrowRight size={11} className="dim-arrow" />
                      <span>{m.target}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      <style>{`
        .hypothesis-card {
          border-left: 3px solid var(--accent-purple);
          background: linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(16, 24, 40, 0.85) 100%);
          padding: 1.5rem 1.75rem;
        }

        .hypo-badge {
          display: inline-flex;
          align-items: center;
          gap: 0.4rem;
          font-family: var(--font-mono);
          font-size: 0.72rem;
          font-weight: 700;
          color: var(--accent-purple);
          margin-bottom: 0.5rem;
        }

        .hypo-title {
          font-size: 1.2rem;
          font-weight: 800;
          color: #fff;
          margin-bottom: 0.5rem;
        }

        .hypo-desc {
          font-size: 0.88rem;
          color: #cbd5e1;
          line-height: 1.6;
          max-width: 960px;
        }

        .hypo-desc strong {
          color: #fff;
        }

        .eval-dim-card {
          padding: 1.5rem;
          display: flex;
          flex-direction: column;
          gap: 1.25rem;
        }

        .eval-dim-card.dim-cyan {
          border-top: 3px solid var(--accent-cyan);
        }

        .eval-dim-card.dim-purple {
          border-top: 3px solid var(--accent-purple);
        }

        .eval-dim-card.dim-emerald {
          border-top: 3px solid var(--accent-emerald);
        }

        .dim-header {
          display: flex;
          align-items: center;
          gap: 0.65rem;
          border-bottom: 1px solid rgba(255, 255, 255, 0.06);
          padding-bottom: 0.75rem;
        }

        .dim-icon-wrap {
          width: 32px;
          height: 32px;
          border-radius: 8px;
          background: rgba(255, 255, 255, 0.05);
          display: flex;
          align-items: center;
          justify-content: center;
          color: #fff;
        }

        .dim-title {
          font-size: 0.95rem;
          font-weight: 700;
          color: #fff;
        }

        .dim-metric-list {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .dim-metric-item {
          background: rgba(15, 23, 42, 0.5);
          border: 1px solid var(--card-border);
          border-radius: var(--radius-sm);
          padding: 0.65rem 0.8rem;
          display: flex;
          flex-direction: column;
          gap: 0.2rem;
        }

        .dim-m-name {
          font-size: 0.82rem;
          font-weight: 600;
          color: #fff;
        }

        .dim-m-target {
          display: flex;
          align-items: flex-start;
          gap: 0.4rem;
          font-size: 0.74rem;
          color: var(--text-secondary);
        }

        .dim-arrow {
          color: var(--accent-cyan);
          flex-shrink: 0;
          margin-top: 3px;
        }
      `}</style>
    </section>
  );
}
