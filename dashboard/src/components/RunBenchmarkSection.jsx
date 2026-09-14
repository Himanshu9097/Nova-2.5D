import React, { useState, useRef, useEffect } from 'react';
import { 
  UploadCloud, 
  FileText, 
  Play, 
  Sliders, 
  AlertTriangle, 
  CheckCircle2, 
  FileSpreadsheet, 
  Sparkles, 
  RefreshCw,
  Info,
  Server,
  X,
  Layers
} from 'lucide-react';
import { useBenchmark } from '../context/BenchmarkContext';
import { validatePointCloudFile, getSampleDatasets } from '../api/client';

export default function RunBenchmarkSection() {
  const { 
    runNewBenchmark, 
    isRunning, 
    runProgress, 
    runError, 
    backendOnline, 
    resetToDemo,
    isDemo 
  } = useBenchmark();

  const fileInputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileValidation, setFileValidation] = useState(null);
  const [isValidating, setIsValidating] = useState(false);
  const [validationError, setValidationError] = useState(null);

  // Configuration parameters
  const [datasetName, setDatasetName] = useState('');
  const [uniformResolution, setUniformResolution] = useState(0.5);
  const [runsCount, setRunsCount] = useState(10);
  const [samples, setSamples] = useState([]);
  const [selectedSample, setSelectedSample] = useState('');

  useEffect(() => {
    if (backendOnline) {
      getSampleDatasets()
        .then(res => setSamples(res.samples || []))
        .catch(err => console.warn('Could not load samples', err));
    }
  }, [backendOnline]);

  const handleFileDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = async (file) => {
    setSelectedFile(file);
    setSelectedSample('');
    setDatasetName(file.name.replace(/\.[^/.]+$/, "").replace(/_/g, " ").replace(/-/g, " "));
    setValidationError(null);
    setIsValidating(true);

    try {
      const val = await validatePointCloudFile(file);
      setFileValidation(val);
    } catch (err) {
      setValidationError(err.message || 'File validation failed');
      setFileValidation(null);
    } finally {
      setIsValidating(false);
    }
  };

  const handleSampleSelect = (sampleFilename) => {
    setSelectedSample(sampleFilename);
    setSelectedFile(null);
    setFileValidation(null);
    setValidationError(null);
    const s = samples.find(item => item.filename === sampleFilename);
    if (s) {
      setDatasetName(s.name);
    }
  };

  const handleRun = async () => {
    if (!selectedFile && !selectedSample) return;

    try {
      await runNewBenchmark({
        file: selectedFile,
        sampleName: selectedSample,
        datasetName: datasetName || 'Custom Point Cloud',
        uniformResolution,
        runsCount
      });
      // Scroll to comparison section smoothly
      const compEl = document.getElementById('comparison');
      if (compEl) {
        compEl.scrollIntoView({ behavior: 'smooth' });
      }
    } catch (err) {
      console.error(err);
    }
  };

  const progressSteps = [
    "Loading Point Cloud",
    "Validating Data",
    "Running Uniform Grid",
    "Running Adaptive Grid",
    "Calculating Metrics",
    "Generating Results"
  ];

  return (
    <section id="run-benchmark" className="section-container">
      <div className="section-header">
        <div className="section-title-group">
          <div className="section-tag">
            <UploadCloud size={14} />
            Input-Driven Evaluation Engine
          </div>
          <h2 className="section-title">
            Run Benchmark on Custom LiDAR Data
          </h2>
          <p className="section-desc">
            Upload custom point cloud datasets (CSV, TXT) or select pre-bundled scenarios.
            The FastAPI backend will execute the real Python Uniform and Adaptive grid engines and dynamically update all metrics.
          </p>
        </div>

        <div className="header-meta">
          <span className={`badge ${backendOnline ? 'badge-emerald' : 'badge-amber'}`}>
            <Server size={12} />
            Backend API: {backendOnline ? 'ONLINE (127.0.0.1:8000)' : 'OFFLINE'}
          </span>
        </div>
      </div>

      <div className="grid-2">
        {/* LEFT: File Upload / Ingestion Zone */}
        <div className="glass-card upload-control-card">
          <div className="card-top-title">
            <h3 className="upload-box-title">Point Cloud Ingestion</h3>
            <span className="badge badge-neutral">Formats: .csv, .txt, .xyz</span>
          </div>

          {/* Drag & Drop Area */}
          <div 
            className={`dropzone ${dragOver ? 'dragover' : ''} ${selectedFile ? 'has-file' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleFileDrop}
            onClick={() => fileInputRef.current && fileInputRef.current.click()}
          >
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileInput} 
              accept=".csv,.txt,.xyz" 
              style={{ display: 'none' }} 
            />

            <UploadCloud size={36} className="drop-icon" />

            {selectedFile ? (
              <div className="drop-file-info">
                <span className="file-name">{selectedFile.name}</span>
                <span className="file-size">({(selectedFile.size / 1024).toFixed(1)} KB)</span>
                <span className="drop-subtext">Click or drag a different file to replace</span>
              </div>
            ) : (
              <div className="drop-prompt">
                <span className="drop-maintext">Drag & drop your point cloud file here</span>
                <span className="drop-subtext">or <strong className="text-cyan-400">browse files</strong> from your system</span>
                <span className="drop-cols-hint">Required columns: <code>x</code>, <code>y</code>, <code>z</code> • Optional: <code>intensity</code>, <code>semantic_class</code></span>
              </div>
            )}
          </div>

          {/* Sample Dataset Selector */}
          <div className="sample-picker-strip">
            <span className="sample-lbl">Quick Demo Presets:</span>
            <div className="sample-buttons">
              {samples.map((s) => (
                <button
                  key={s.filename}
                  className={`sample-btn ${selectedSample === s.filename ? 'active' : ''}`}
                  onClick={() => handleSampleSelect(s.filename)}
                >
                  <Sparkles size={12} />
                  {s.name}
                </button>
              ))}
              {!isDemo && (
                <button className="sample-btn reset-btn" onClick={resetToDemo}>
                  <RefreshCw size={12} />
                  Reset to Baseline (10K)
                </button>
              )}
            </div>
          </div>

          {/* Validation Feedback Card */}
          {isValidating && (
            <div className="callout-box info">
              <RefreshCw size={16} className="spin-icon text-cyan-400" />
              <span>Validating point cloud coordinates, delimiters, and header schema...</span>
            </div>
          )}

          {validationError && (
            <div className="callout-box warning">
              <AlertTriangle size={16} className="text-amber-400" />
              <span>{validationError}</span>
            </div>
          )}

          {fileValidation && (
            <div className="validation-result-card">
              <div className="val-header">
                <div className="val-title">
                  <CheckCircle2 size={15} className="text-emerald-400" />
                  <span>Validation Passed: {fileValidation.total_points.toLocaleString()} Points Detected</span>
                </div>
                <span className="badge badge-emerald">Valid 3D Array</span>
              </div>

              {/* Missing Semantic Notice if applicable */}
              {!fileValidation.has_semantics && (
                <div className="semantic-missing-notice">
                  <Info size={14} className="text-amber-400" />
                  <span>Semantic labels unavailable — semantic accuracy evaluation disabled. Spatial grid benchmarking will proceed normally.</span>
                </div>
              )}

              {/* Columns Detected */}
              <div className="detected-cols-row">
                <span className="det-lbl">Detected Columns:</span>
                {fileValidation.columns_detected.map(c => (
                  <span key={c} className="det-pill"><code>{c}</code></span>
                ))}
              </div>

              {/* 5-Row Data Preview */}
              {fileValidation.preview_rows && fileValidation.preview_rows.length > 0 && (
                <div className="preview-table-wrap">
                  <span className="preview-lbl">Point Cloud Sample Preview:</span>
                  <table className="mini-preview-table">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>x (m)</th>
                        <th>y (m)</th>
                        <th>z (m)</th>
                        <th>Intensity</th>
                        <th>Class</th>
                      </tr>
                    </thead>
                    <tbody>
                      {fileValidation.preview_rows.map((row) => (
                        <tr key={row.index}>
                          <td className="mono">{row.index}</td>
                          <td className="mono">{row.x}</td>
                          <td className="mono">{row.y}</td>
                          <td className="mono">{row.z}</td>
                          <td className="mono">{row.intensity}</td>
                          <td className="mono">{row.semantic_class !== null ? row.semantic_class : 'N/A'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>

        {/* RIGHT: Configuration & Execution Panel */}
        <div className="glass-card benchmark-config-card">
          <div className="card-top-title">
            <h3 className="upload-box-title">Benchmark Parameters</h3>
            <span className="badge badge-purple">Engine Configuration</span>
          </div>

          <div className="config-form">
            {/* Dataset Name */}
            <div className="config-field">
              <label className="config-label">Dataset / Experiment Identifier</label>
              <input 
                type="text" 
                className="config-input" 
                value={datasetName} 
                onChange={(e) => setDatasetName(e.target.value)}
                placeholder="e.g. CARLA Town01 Spinning LiDAR" 
              />
            </div>

            {/* Uniform Resolution Slider */}
            <div className="config-field">
              <div className="field-header-row">
                <label className="config-label">Uniform Grid Resolution (Cell Size)</label>
                <span className="field-value-tag">{uniformResolution.toFixed(2)} m</span>
              </div>
              <input 
                type="range" 
                min="0.1" 
                max="2.0" 
                step="0.05" 
                className="config-slider" 
                value={uniformResolution} 
                onChange={(e) => setUniformResolution(parseFloat(e.target.value))} 
              />
              <span className="field-hint">Default: 0.50m. Finer resolution produces more cells and higher detail.</span>
            </div>

            {/* Number of Runs */}
            <div className="config-field">
              <div className="field-header-row">
                <label className="config-label">Empirical Benchmark Iterations (Runs)</label>
                <span className="field-value-tag">{runsCount} runs</span>
              </div>
              <input 
                type="range" 
                min="1" 
                max="20" 
                step="1" 
                className="config-slider" 
                value={runsCount} 
                onChange={(e) => setRunsCount(parseInt(e.target.value))} 
              />
              <span className="field-hint">Default: 10 runs for robust mean & standard deviation calculation.</span>
            </div>

            {/* Adaptive Policy Rule Summary (Modular) */}
            <div className="adaptive-config-box">
              <span className="ac-title">Adaptive Policy Configuration (Prototype)</span>
              <ul className="ac-rules-list">
                <li>Vehicle & Pedestrian: <code>0.25m (Fine)</code></li>
                <li>Distance &lt; 10m: <code>0.25m (Immediate Safety)</code></li>
                <li>10m &le; Distance &lt; 25m: <code>0.50m (Medium Range)</code></li>
                <li>Distance &ge; 25m: <code>1.00m (Coarse Background)</code></li>
              </ul>
            </div>

            {/* Run Button */}
            <button 
              className={`run-benchmark-btn ${(selectedFile || selectedSample) && backendOnline && !isRunning ? 'active' : 'disabled'}`}
              onClick={handleRun}
              disabled={(!selectedFile && !selectedSample) || !backendOnline || isRunning}
            >
              {isRunning ? (
                <>
                  <RefreshCw size={16} className="spin-icon" />
                  <span>Processing Benchmark ({runProgress?.step || 1}/6)...</span>
                </>
              ) : (
                <>
                  <Play size={16} fill="currentColor" />
                  <span>Execute Benchmark Pipeline</span>
                </>
              )}
            </button>

            {runError && (
              <div className="callout-box warning" style={{ marginTop: '0.75rem' }}>
                <AlertTriangle size={16} className="text-rose-400" />
                <span style={{ color: '#fca5a5' }}>{runError}</span>
              </div>
            )}
          </div>

          {/* Progress Stepper */}
          {isRunning && runProgress && (
            <div className="stepper-wrap">
              <div className="stepper-bar">
                <div 
                  className="stepper-progress" 
                  style={{ width: `${(runProgress.step / 6) * 100}%` }}
                ></div>
              </div>
              <div className="stepper-label-row">
                <span className="step-count">Step {runProgress.step} of 6</span>
                <span className="step-label">{runProgress.label}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      <style>{`
        .upload-control-card, .benchmark-config-card {
          padding: 1.5rem;
          display: flex;
          flex-direction: column;
          gap: 1.25rem;
        }

        .upload-box-title {
          font-size: 1.05rem;
          font-weight: 700;
          color: #fff;
        }

        .dropzone {
          border: 2px dashed rgba(6, 182, 212, 0.35);
          border-radius: var(--radius-md);
          background: rgba(6, 182, 212, 0.03);
          padding: 2.25rem 1.5rem;
          text-align: center;
          cursor: pointer;
          transition: all 0.2s ease;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.75rem;
        }

        .dropzone:hover, .dropzone.dragover {
          border-color: var(--accent-cyan);
          background: rgba(6, 182, 212, 0.08);
          transform: translateY(-2px);
        }

        .dropzone.has-file {
          border-color: var(--accent-emerald);
          background: rgba(16, 185, 129, 0.05);
        }

        .drop-icon {
          color: var(--accent-cyan);
        }

        .drop-maintext {
          font-size: 0.95rem;
          font-weight: 600;
          color: #fff;
          display: block;
        }

        .drop-subtext {
          font-size: 0.8rem;
          color: var(--text-secondary);
          display: block;
          margin-top: 0.2rem;
        }

        .drop-cols-hint {
          font-size: 0.74rem;
          color: var(--text-muted);
          display: block;
          margin-top: 0.5rem;
        }

        .drop-cols-hint code {
          font-family: var(--font-mono);
          color: var(--accent-cyan);
        }

        .drop-file-info {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.25rem;
        }

        .file-name {
          font-family: var(--font-mono);
          font-size: 0.95rem;
          font-weight: 700;
          color: #34d399;
        }

        .file-size {
          font-size: 0.75rem;
          color: var(--text-muted);
        }

        .sample-picker-strip {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          border-top: 1px solid rgba(255, 255, 255, 0.06);
          padding-top: 0.75rem;
        }

        .sample-lbl {
          font-size: 0.75rem;
          font-weight: 600;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .sample-buttons {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .sample-btn {
          background: rgba(15, 23, 42, 0.7);
          border: 1px solid var(--card-border);
          color: #cbd5e1;
          font-size: 0.76rem;
          padding: 0.35rem 0.65rem;
          border-radius: var(--radius-sm);
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 0.4rem;
          transition: all 0.2s ease;
        }

        .sample-btn:hover, .sample-btn.active {
          border-color: var(--accent-cyan);
          background: rgba(6, 182, 212, 0.15);
          color: #fff;
        }

        .sample-btn.reset-btn {
          border-color: rgba(245, 158, 11, 0.4);
          color: #fbbf24;
        }

        .validation-result-card {
          background: rgba(15, 23, 42, 0.6);
          border: 1px solid var(--card-border);
          border-radius: var(--radius-sm);
          padding: 0.85rem 1rem;
          display: flex;
          flex-direction: column;
          gap: 0.6rem;
        }

        .val-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .val-title {
          font-size: 0.82rem;
          font-weight: 700;
          color: #fff;
          display: flex;
          align-items: center;
          gap: 0.4rem;
        }

        .semantic-missing-notice {
          background: rgba(245, 158, 11, 0.08);
          border: 1px solid rgba(245, 158, 11, 0.25);
          border-radius: 4px;
          padding: 0.45rem 0.65rem;
          font-size: 0.75rem;
          color: #fbbf24;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .detected-cols-row {
          display: flex;
          align-items: center;
          gap: 0.4rem;
          flex-wrap: wrap;
          font-size: 0.75rem;
        }

        .det-lbl {
          color: var(--text-muted);
        }

        .det-pill {
          background: rgba(6, 182, 212, 0.1);
          border: 1px solid rgba(6, 182, 212, 0.25);
          padding: 0.1rem 0.4rem;
          border-radius: 4px;
          color: var(--accent-cyan);
          font-family: var(--font-mono);
          font-size: 0.7rem;
        }

        .preview-table-wrap {
          border-top: 1px solid rgba(255, 255, 255, 0.04);
          padding-top: 0.5rem;
        }

        .preview-lbl {
          font-size: 0.72rem;
          color: var(--text-muted);
          margin-bottom: 0.35rem;
          display: block;
        }

        .mini-preview-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.72rem;
        }

        .mini-preview-table th {
          background: rgba(0, 0, 0, 0.3);
          color: var(--text-muted);
          padding: 0.25rem 0.4rem;
          text-align: left;
        }

        .mini-preview-table td {
          padding: 0.25rem 0.4rem;
          border-bottom: 1px solid rgba(255, 255, 255, 0.03);
          color: #cbd5e1;
        }

        .config-form {
          display: flex;
          flex-direction: column;
          gap: 1.15rem;
        }

        .config-field {
          display: flex;
          flex-direction: column;
          gap: 0.35rem;
        }

        .config-label {
          font-size: 0.8rem;
          font-weight: 600;
          color: #e2e8f0;
        }

        .field-header-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .field-value-tag {
          font-family: var(--font-mono);
          font-size: 0.75rem;
          font-weight: 700;
          color: var(--accent-cyan);
          background: rgba(6, 182, 212, 0.1);
          padding: 0.1rem 0.45rem;
          border-radius: 4px;
        }

        .config-input {
          background: rgba(15, 23, 42, 0.8);
          border: 1px solid var(--card-border);
          border-radius: var(--radius-sm);
          padding: 0.6rem 0.8rem;
          font-family: var(--font-sans);
          font-size: 0.85rem;
          color: #fff;
          outline: none;
          transition: border-color 0.2s ease;
        }

        .config-input:focus {
          border-color: var(--accent-cyan);
        }

        .config-slider {
          accent-color: var(--accent-cyan);
          cursor: pointer;
        }

        .field-hint {
          font-size: 0.7rem;
          color: var(--text-muted);
        }

        .adaptive-config-box {
          background: rgba(15, 23, 42, 0.5);
          border: 1px solid var(--card-border);
          border-radius: var(--radius-sm);
          padding: 0.75rem 0.85rem;
        }

        .ac-title {
          font-size: 0.75rem;
          font-weight: 700;
          color: #a78bfa;
          display: block;
          margin-bottom: 0.4rem;
        }

        .ac-rules-list {
          list-style: none;
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
          font-size: 0.72rem;
          color: var(--text-secondary);
        }

        .ac-rules-list code {
          font-family: var(--font-mono);
          color: var(--accent-cyan);
        }

        .run-benchmark-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.6rem;
          padding: 0.85rem 1.5rem;
          border-radius: var(--radius-sm);
          font-family: var(--font-sans);
          font-size: 0.9rem;
          font-weight: 700;
          cursor: pointer;
          border: none;
          transition: all 0.2s ease;
        }

        .run-benchmark-btn.active {
          background: linear-gradient(135deg, var(--accent-cyan) 0%, #0284c7 100%);
          color: #070a12;
          box-shadow: 0 0 16px var(--accent-cyan-glow);
        }

        .run-benchmark-btn.active:hover {
          transform: translateY(-1px);
          box-shadow: 0 0 24px rgba(6, 182, 212, 0.4);
        }

        .run-benchmark-btn.disabled {
          background: rgba(255, 255, 255, 0.05);
          color: var(--text-muted);
          cursor: not-allowed;
        }

        .stepper-wrap {
          display: flex;
          flex-direction: column;
          gap: 0.45rem;
          margin-top: 0.5rem;
        }

        .stepper-bar {
          height: 6px;
          background: rgba(255, 255, 255, 0.08);
          border-radius: 9999px;
          overflow: hidden;
        }

        .stepper-progress {
          height: 100%;
          background: linear-gradient(90deg, var(--accent-cyan), var(--accent-emerald));
          transition: width 0.3s ease;
        }

        .stepper-label-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          font-size: 0.74rem;
        }

        .step-count {
          font-family: var(--font-mono);
          color: var(--accent-cyan);
          font-weight: 600;
        }

        .step-label {
          color: #cbd5e1;
        }

        .spin-icon {
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </section>
  );
}
