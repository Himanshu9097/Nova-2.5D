import React, { createContext, useContext, useState, useEffect } from 'react';
import { 
  BENCHMARK_METADATA, 
  STATISTICAL_SUMMARY, 
  SYNTHETIC_INPUT_DATA, 
  PAIRED_RUNS, 
  MULTI_RUN_RESULTS 
} from '../data/benchmarkData';
import { 
  checkBackendHealth, 
  executeBenchmark, 
  getBenchmarkHistory, 
  getSingleHistoryItem 
} from '../api/client';

const BenchmarkContext = createContext(null);

// Initial default synthetic baseline dataset
const DEFAULT_BASELINE_STATE = {
  id: 'baseline_synthetic_10k',
  dataset: {
    name: "Synthetic LiDAR Scene (Deterministic)",
    points: 10000,
    has_semantics: true,
    uniform_resolution: 0.5,
    runs_count: 10,
    bounds: { x: [-30, 30], y: [-10, 10], z: [-2, 5] },
    columns: ["x", "y", "z", "intensity", "semantic_class"],
    classes: SYNTHETIC_INPUT_DATA.classes,
    preview: [
      { index: 0, x: -14.28, y: 3.12, z: 0.01, intensity: 0.54, semantic_class: 0 },
      { index: 1, x: 10.45, y: -0.85, z: 1.12, intensity: 0.82, semantic_class: 1 },
      { index: 2, x: -4.50, y: 3.55, z: 1.20, intensity: 0.74, semantic_class: 2 },
      { index: 3, x: 18.20, y: 7.10, z: 2.45, intensity: 0.61, semantic_class: 3 },
      { index: 4, x: -22.10, y: -8.40, z: 3.80, intensity: 0.15, semantic_class: 4 }
    ]
  },
  uniform: {
    runs_count: 10,
    cells_mean: STATISTICAL_SUMMARY.uniform.cellsMean,
    cells_std: STATISTICAL_SUMMARY.uniform.cellsStd,
    latency_mean: STATISTICAL_SUMMARY.uniform.latencyMean,
    latency_std: STATISTICAL_SUMMARY.uniform.latencyStd,
    fps_mean: STATISTICAL_SUMMARY.uniform.fpsMean,
    fps_std: STATISTICAL_SUMMARY.uniform.fpsStd,
    memory_mean: STATISTICAL_SUMMARY.uniform.memoryMean,
    memory_std: STATISTICAL_SUMMARY.uniform.memoryStd
  },
  adaptive: {
    runs_count: 10,
    cells_mean: STATISTICAL_SUMMARY.adaptive.cellsMean,
    cells_std: STATISTICAL_SUMMARY.adaptive.cellsStd,
    latency_mean: STATISTICAL_SUMMARY.adaptive.latencyMean,
    latency_std: STATISTICAL_SUMMARY.adaptive.latencyStd,
    fps_mean: STATISTICAL_SUMMARY.adaptive.fpsMean,
    fps_std: STATISTICAL_SUMMARY.adaptive.fpsStd,
    memory_mean: STATISTICAL_SUMMARY.adaptive.memoryMean,
    memory_std: STATISTICAL_SUMMARY.adaptive.memoryStd
  },
  comparison: {
    cell_diff: 238,
    cell_diff_pct: 7.16,
    latency_diff_ms: 28.012,
    latency_diff_pct: 56.2,
    fps_diff: -7.19,
    fps_diff_pct: -34.0
  },
  runs: {
    paired: PAIRED_RUNS,
    uniform: MULTI_RUN_RESULTS.filter(r => r.method === 'Uniform'),
    adaptive: MULTI_RUN_RESULTS.filter(r => r.method === 'Adaptive')
  },
  output_map: {
    uniform_cells_sample: [],
    adaptive_cells_sample: [],
    total_uniform_cells: 3322,
    total_adaptive_cells: 3560
  }
};

export function BenchmarkProvider({ children }) {
  const [activeDataset, setActiveDataset] = useState(DEFAULT_BASELINE_STATE);
  const [isDemo, setIsDemo] = useState(true);
  const [backendOnline, setBackendOnline] = useState(false);
  const [historyList, setHistoryList] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [runProgress, setRunProgress] = useState(null); // { step: 1, label: "..." }
  const [runError, setRunError] = useState(null);

  // Check backend health and load history on mount
  useEffect(() => {
    async function initBackend() {
      const health = await checkBackendHealth();
      setBackendOnline(health.online);

      if (health.online) {
        try {
          const hist = await getBenchmarkHistory();
          if (hist && hist.history) {
            setHistoryList(hist.history);
          }
        } catch (e) {
          console.warn('Could not load history:', e);
        }
      }
    }
    initBackend();
  }, []);

  const refreshHistory = async () => {
    try {
      const hist = await getBenchmarkHistory();
      if (hist && hist.history) {
        setHistoryList(hist.history);
      }
    } catch (e) {
      console.warn('Failed to refresh history', e);
    }
  };

  const runNewBenchmark = async ({ file, sampleName, datasetName, uniformResolution, runsCount }) => {
    setIsRunning(true);
    setRunError(null);
    setRunProgress({ step: 1, label: "Loading Point Cloud & Ingestion..." });

    try {
      await new Promise(r => setTimeout(r, 400));
      setRunProgress({ step: 2, label: "Validating 3D Coordinates & Schema..." });

      await new Promise(r => setTimeout(r, 400));
      setRunProgress({ step: 3, label: `Executing Uniform Grid (${uniformResolution}m, ${runsCount} runs)...` });

      await new Promise(r => setTimeout(r, 400));
      setRunProgress({ step: 4, label: "Executing Prototype Adaptive Grid..." });

      await new Promise(r => setTimeout(r, 400));
      setRunProgress({ step: 5, label: "Calculating Statistical Metrics & 2.5D Elevation Raster..." });

      const result = await executeBenchmark({
        file,
        sampleName,
        datasetName,
        uniformResolution,
        runsCount
      });

      setRunProgress({ step: 6, label: "Finalizing Benchmark Results..." });
      await new Promise(r => setTimeout(r, 300));

      setActiveDataset(result);
      setIsDemo(false);
      await refreshHistory();
      return result;
    } catch (err) {
      setRunError(err.message || 'Benchmark execution failed');
      throw err;
    } finally {
      setIsRunning(false);
      setRunProgress(null);
    }
  };

  const selectHistoryItem = async (runId) => {
    if (runId === 'baseline_synthetic_10k') {
      resetToDemo();
      return;
    }

    try {
      const item = await getSingleHistoryItem(runId);
      if (item && item.full_result) {
        setActiveDataset(item.full_result);
        setIsDemo(false);
      }
    } catch (err) {
      console.error("Failed to load history run:", err);
    }
  };

  const resetToDemo = () => {
    setActiveDataset(DEFAULT_BASELINE_STATE);
    setIsDemo(true);
  };

  return (
    <BenchmarkContext.Provider value={{
      activeDataset,
      isDemo,
      backendOnline,
      historyList,
      isRunning,
      runProgress,
      runError,
      runNewBenchmark,
      selectHistoryItem,
      resetToDemo,
      refreshHistory
    }}>
      {children}
    </BenchmarkContext.Provider>
  );
}

export function useBenchmark() {
  const context = useContext(BenchmarkContext);
  if (!context) {
    throw new Error("useBenchmark must be used within a BenchmarkProvider");
  }
  return context;
}
