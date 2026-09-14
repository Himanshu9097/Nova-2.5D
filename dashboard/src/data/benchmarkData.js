/**
 * NOVA-2.5D Benchmark Data Source
 * 
 * Sourced directly from:
 * - benchmark/results/multi_run_benchmark.csv
 * - benchmark/results/scaling_benchmark.csv
 * - benchmark/results/benchmark.csv
 * - benchmark/data.py
 * - benchmark/stats.py
 * - benchmark/scaling_stats.py
 * 
 * IMPORTANT: All data points here reflect actual recorded benchmark measurements.
 * Zero metrics are fabricated or extrapolated.
 */

export const BENCHMARK_METADATA = {
  projectName: "NOVA-2.5D",
  projectConcept: "Adaptive Variable Resolution 2.5D LiDAR Mapping System",
  subtitle: "Benchmark & Evaluation Dashboard",
  author: "Riddhima",
  role: "Benchmark, Performance & Visualization",
  branch: "riddhima-benchmark",
  statusBadge: "PRELIMINARY RESULTS • SYNTHETIC LiDAR DATA",
  timestamp: "September 2026",
  preliminaryNote: "The current benchmark measures a prototype adaptive resolution policy on a deterministic synthetic LiDAR scene. Final evaluation will integrate the complete Adaptive Grid Engine with real CARLA LiDAR point clouds."
};

// 1. Synthetic LiDAR Input Scene Breakdown
export const SYNTHETIC_INPUT_DATA = {
  totalPoints: 10000,
  schema: ["x", "y", "z", "intensity", "semantic_class"],
  schemaDescription: [
    { field: "x", desc: "Longitudinal position (meters), range [-30, 30]" },
    { field: "y", desc: "Lateral position (meters), range [-10, 10]" },
    { field: "z", desc: "Elevation / height (meters), range [-2, 5]" },
    { field: "intensity", desc: "LiDAR reflectance intensity [0.0 - 1.0]" },
    { field: "semantic_class", desc: "Ground-truth category label [0 - 4]" }
  ],
  classes: [
    {
      id: 0,
      name: "Road",
      count: 5000,
      percentage: 50.0,
      color: "#3b82f6",
      spatialBounds: "x: [-30, 30], y: [-10, 10], z: ~0m",
      description: "Flat drivable surface; base elevation layer"
    },
    {
      id: 1,
      name: "Vehicle",
      count: 2000,
      percentage: 20.0,
      color: "#10b981",
      spatialBounds: "x: [8, 12], y: [-2, 2], z: [0, 2m]",
      description: "Dynamic bounding volume; high-priority object"
    },
    {
      id: 2,
      name: "Pedestrian",
      count: 1000,
      percentage: 10.0,
      color: "#f59e0b",
      spatialBounds: "x: [-5, -4], y: [3, 4], z: [0, 1.8m]",
      description: "Vulnerable road user; critical safety feature"
    },
    {
      id: 3,
      name: "Wall",
      count: 1500,
      percentage: 15.0,
      color: "#8b5cf6",
      spatialBounds: "x: [15, 25], y: [7, 7.2], z: [0, 4m]",
      description: "Static vertical boundary / obstacle"
    },
    {
      id: 4,
      name: "Noise",
      count: 500,
      percentage: 5.0,
      color: "#ef4444",
      spatialBounds: "x: [-30, 30], y: [-10, 10], z: [-2, 5m]",
      description: "Atmospheric or sensor reflection artifacts"
    }
  ],
  explanation: "The current benchmark uses a deterministic synthetic LiDAR scene to validate the evaluation pipeline before integrating actual CARLA LiDAR data."
};

// 2. Uniform vs Adaptive Algorithm Specs
export const GRID_ALGORITHMS = {
  uniform: {
    name: "Uniform Grid",
    resolutionMeters: 0.5,
    indexing: "cell_x = floor(x / 0.5), cell_y = floor(y / 0.5)",
    keyStructure: "(cell_x, cell_y)",
    cellPayload: ["points (list)", "max_height (float)", "semantic_classes (list)"],
    occupiedCells: 3322,
    pointsProcessed: 10000,
    policySummary: "Fixed 0.5m grid cell spacing across the entire region of interest.",
    pros: "O(1) direct indexing, trivial rasterization, deterministic footprint.",
    cons: "Oversamples uniform empty road; undersamples fine object edges and distant obstacles."
  },
  adaptive: {
    name: "Adaptive Grid (Prototype)",
    isPrototype: true,
    policyRules: [
      { condition: "semantic_class in [1, 2] (Vehicle or Pedestrian)", resolution: 0.25, level: "Fine" },
      { condition: "distance = sqrt(x² + y²) < 10m", resolution: 0.25, level: "Fine" },
      { condition: "10m <= distance < 25m", resolution: 0.5, level: "Medium" },
      { condition: "distance >= 25m (Far field)", resolution: 1.0, level: "Coarse" }
    ],
    indexing: "cell_x = floor(x / res), cell_y = floor(y / res)",
    keyStructure: "(cell_x, cell_y, resolution)",
    cellPayload: ["points (list)", "resolution (float)", "max_height (float)", "semantic_classes (list)"],
    occupiedCells: 3560,
    pointsProcessed: 10000,
    policySummary: "Multi-resolution spatial hash based on distance thresholding and semantic importance.",
    pros: "High spatial fidelity near safety-critical agents and the ego-vehicle vicinity.",
    cons: "Additional per-point distance computation and multi-resolution key generation create prototype overhead.",
    prototypeDisclaimer: "This is a prototype/dummy adaptive policy for benchmark infrastructure testing. The final Adaptive Grid Engine will be integrated later and the complete benchmark will be repeated."
  }
};

// 3. Multi-run benchmark results (Raw 10 runs from multi_run_benchmark.csv)
export const MULTI_RUN_RESULTS = [
  { run: 1, method: "Uniform", points: 10000, cells: 3322, latency_ms: 62.0688, fps: 16.11, memory_mb: 3.074 },
  { run: 1, method: "Adaptive", points: 10000, cells: 3560, latency_ms: 58.3033, fps: 17.15, memory_mb: 3.063 },
  { run: 2, method: "Uniform", points: 10000, cells: 3322, latency_ms: 32.5010, fps: 30.77, memory_mb: 3.105 },
  { run: 2, method: "Adaptive", points: 10000, cells: 3560, latency_ms: 72.0523, fps: 13.88, memory_mb: 0.855 },
  { run: 3, method: "Uniform", points: 10000, cells: 3322, latency_ms: 43.5310, fps: 22.97, memory_mb: 0.145 },
  { run: 3, method: "Adaptive", points: 10000, cells: 3560, latency_ms: 52.1177, fps: 19.19, memory_mb: 0.008 },
  { run: 4, method: "Uniform", points: 10000, cells: 3322, latency_ms: 41.7471, fps: 23.95, memory_mb: 0.000 },
  { run: 4, method: "Adaptive", points: 10000, cells: 3560, latency_ms: 57.2274, fps: 17.47, memory_mb: 0.000 },
  { run: 5, method: "Uniform", points: 10000, cells: 3322, latency_ms: 41.8278, fps: 23.91, memory_mb: 0.000 },
  { run: 5, method: "Adaptive", points: 10000, cells: 3560, latency_ms: 63.6562, fps: 15.71, memory_mb: 0.000 },
  { run: 6, method: "Uniform", points: 10000, cells: 3322, latency_ms: 55.1339, fps: 18.14, memory_mb: 0.000 },
  { run: 6, method: "Adaptive", points: 10000, cells: 3560, latency_ms: 124.7294, fps: 8.02, memory_mb: 0.000 },
  { run: 7, method: "Uniform", points: 10000, cells: 3322, latency_ms: 67.3696, fps: 14.84, memory_mb: 0.000 },
  { run: 7, method: "Adaptive", points: 10000, cells: 3560, latency_ms: 114.9642, fps: 8.70, memory_mb: 0.000 },
  { run: 8, method: "Uniform", points: 10000, cells: 3322, latency_ms: 65.5003, fps: 15.27, memory_mb: 0.000 },
  { run: 8, method: "Adaptive", points: 10000, cells: 3560, latency_ms: 65.6929, fps: 15.22, memory_mb: 0.000 },
  { run: 9, method: "Uniform", points: 10000, cells: 3322, latency_ms: 40.4023, fps: 24.75, memory_mb: 0.000 },
  { run: 9, method: "Adaptive", points: 10000, cells: 3560, latency_ms: 98.3335, fps: 10.17, memory_mb: 0.000 },
  { run: 10, method: "Uniform", points: 10000, cells: 3322, latency_ms: 48.3156, fps: 20.70, memory_mb: 0.000 },
  { run: 10, method: "Adaptive", points: 10000, cells: 3560, latency_ms: 71.4446, fps: 14.00, memory_mb: 0.000 }
];

// Pair runs for side-by-side run-by-run charts
export const PAIRED_RUNS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(runNum => {
  const u = MULTI_RUN_RESULTS.find(r => r.run === runNum && r.method === "Uniform");
  const a = MULTI_RUN_RESULTS.find(r => r.run === runNum && r.method === "Adaptive");
  return {
    run: `Run ${runNum}`,
    runNum,
    uniformLatency: Number(u.latency_ms.toFixed(2)),
    adaptiveLatency: Number(a.latency_ms.toFixed(2)),
    uniformFps: Number(u.fps.toFixed(2)),
    adaptiveFps: Number(a.fps.toFixed(2)),
    uniformCells: u.cells,
    adaptiveCells: a.cells,
    uniformMemory: Number(u.memory_mb.toFixed(3)),
    adaptiveMemory: Number(a.memory_mb.toFixed(3))
  };
});

// 4. Ten-run statistical summary (verified against stats.py)
export const STATISTICAL_SUMMARY = {
  uniform: {
    name: "Uniform Grid",
    runsCount: 10,
    points: 10000,
    cellsMean: 3322.00,
    cellsStd: 0.00,
    latencyMean: 49.840,
    latencyStd: 11.980,
    fpsMean: 21.14,
    fpsStd: 5.09,
    memoryMean: 0.632,
    memoryStd: 1.258
  },
  adaptive: {
    name: "Adaptive Grid (Prototype)",
    runsCount: 10,
    points: 10000,
    cellsMean: 3560.00,
    cellsStd: 0.00,
    latencyMean: 77.852,
    latencyStd: 25.578,
    fpsMean: 13.95,
    fpsStd: 3.83,
    memoryMean: 0.393,
    memoryStd: 0.957
  },
  comparisonNote: "These are preliminary synthetic-data results from the current prototype Adaptive Grid implementation. They are NOT final system performance results.",
  memoryCaveat: "Preliminary / requires improved profiling: several benchmark runs reported 0 MB delta due to standard process RSS granularity in short iterations."
};

// 5. Scaling benchmark statistics (verified against scaling_stats.py and scaling_benchmark.csv)
export const SCALING_SUMMARY = [
  {
    points: 5000,
    pointsLabel: "5,000",
    uniform: {
      cells: 3136,
      latencyMean: 20.483,
      latencyStd: 5.176,
      fpsMean: 51.49,
      fpsStd: 13.41
    },
    adaptive: {
      cells: 3128,
      latencyMean: 32.645,
      latencyStd: 5.127,
      fpsMean: 31.28,
      fpsStd: 5.18
    }
  },
  {
    points: 10000,
    pointsLabel: "10,000",
    uniform: {
      cells: 3322,
      latencyMean: 42.121,
      latencyStd: 7.632,
      fpsMean: 24.36,
      fpsStd: 4.14
    },
    adaptive: {
      cells: 3560,
      latencyMean: 48.201,
      latencyStd: 2.748,
      fpsMean: 20.80,
      fpsStd: 1.25
    }
  },
  {
    points: 25000,
    pointsLabel: "25,000",
    uniform: {
      cells: 3322,
      latencyMean: 74.103,
      latencyStd: 13.791,
      fpsMean: 13.84,
      fpsStd: 2.36
    },
    adaptive: {
      cells: 3560,
      latencyMean: 87.749,
      latencyStd: 3.666,
      fpsMean: 11.41,
      fpsStd: 0.49
    }
  },
  {
    points: 50000,
    pointsLabel: "50,000",
    uniform: {
      cells: 3322,
      latencyMean: 126.291,
      latencyStd: 16.353,
      fpsMean: 8.02,
      fpsStd: 0.98
    },
    adaptive: {
      cells: 3560,
      latencyMean: 178.844,
      latencyStd: 25.688,
      fpsMean: 5.67,
      fpsStd: 0.73
    }
  }
];

// Flat chart format for scaling charts
export const SCALING_CHART_DATA = SCALING_SUMMARY.map(item => ({
  points: item.points,
  pointsLabel: item.pointsLabel,
  uniformLatency: item.uniform.latencyMean,
  adaptiveLatency: item.adaptive.latencyMean,
  uniformFps: item.uniform.fpsMean,
  adaptiveFps: item.adaptive.fpsMean,
  uniformCells: item.uniform.cells,
  adaptiveCells: item.adaptive.cells
}));

export const SCALING_LIMITATION_NOTE = 
  "Scaling experiment limitation: point counts above 10K currently reuse/repeat the synthetic spatial dataset. This measures increased processing load but does not yet represent genuinely denser spatial LiDAR sampling. A realistic density-scaling experiment will be performed later.";

// 6. Project Status Matrix
export const PROJECT_STATUS = [
  { category: "Completed", icon: "CheckCircle", color: "emerald", items: [
    "Synthetic LiDAR scene generator with deterministic seeding",
    "Multi-class semantic label generation (Road, Vehicle, Pedestrian, Wall, Noise)",
    "Uniform 2.5D elevation grid generation (0.5m resolution)",
    "Prototype Adaptive 2.5D grid generation (distance + semantic heuristic)",
    "Reproducible benchmark execution framework (metrics.py)",
    "Precise latency profiling via time.perf_counter",
    "Frames Per Second (FPS) evaluation",
    "Structured CSV result logging with headers & automated directory creation",
    "Multi-run 10-iteration empirical benchmark",
    "Statistical analysis suite (Mean & Standard Deviation calculations)",
    "Scaling benchmark across 5K, 10K, 25K, and 50K point loads",
    "Matplotlib comparison visualization generation"
  ]},
  { category: "In Progress", icon: "Clock", color: "amber", items: [
    "Realistic LiDAR density scaling (replacing spatial point repetition)",
    "Improved sub-millisecond and per-allocation memory profiling",
    "Semantic representation accuracy metric calculation",
    "Elevation ground-truth Mean Absolute Error (MAE) evaluation",
    "Vulnerable road user & vehicle feature preservation quantification",
    "Interactive browser-based research visualization dashboard"
  ]},
  { category: "Future Integration", icon: "Compass", color: "cyan", items: [
    "CARLA autonomous driving simulator bridge",
    "Virtual multi-channel spinning LiDAR streaming integration",
    "Deep semantic segmentation AI model inference integration",
    "Kalman-filter dynamic object tracking & velocity vectoring",
    "Production-grade C++/Cython/Numba Adaptive Grid Engine",
    "End-to-end continuous closed-loop real-time benchmark",
    "Academic research paper evaluation against state-of-the-art baselines"
  ]}
];

// 7. Metrics Taxonomy ("What We Measure")
export const METRICS_TAXONOMY = [
  {
    category: "Performance Metrics",
    desc: "Computational efficiency and runtime throughput for real-time robotic deployment",
    metrics: [
      { name: "Frames Per Second (FPS)", formula: "1.0 / latency_seconds", status: "Active", value: "Uniform: 21.14 | Adaptive: 13.95" },
      { name: "Execution Latency", formula: "perf_counter() end - start (ms)", status: "Active", value: "Uniform: 49.84 ms | Adaptive: 77.85 ms" },
      { name: "Memory Delta", formula: "psutil RSS (MB) difference", status: "Preliminary", value: "Uniform: ~0.63 MB | Adaptive: ~0.39 MB" }
    ]
  },
  {
    category: "Mapping Metrics",
    desc: "Geometric fidelity, spatial occupancy, and semantic conservation",
    metrics: [
      { name: "Occupied Cell Count", formula: "len(grid.keys())", status: "Active", value: "Uniform: 3,322 | Adaptive: 3,560" },
      { name: "Elevation Error", formula: "MAE = (1/N) Σ |z_true - z_grid|", status: "Future", value: "Coming Soon (CARLA integration)" },
      { name: "Semantic Accuracy", formula: "Class intersection over union (mIoU)", status: "Future", value: "Coming Soon (AI pipeline)" },
      { name: "Object Preservation", formula: "% key object points retained in fine cells", status: "Future", value: "Coming Soon (Tracking pipeline)" }
    ]
  },
  {
    category: "Statistical Metrics",
    desc: "Reproducibility, dispersion, and run-to-run variance",
    metrics: [
      { name: "Mean (Average)", formula: "μ = (1/N) Σ x_i", status: "Active", value: "Calculated across 10 runs" },
      { name: "Standard Deviation (σ)", formula: "σ = sqrt(Σ(x - μ)² / (N-1))", status: "Active", value: "Latency σ: 11.98ms (U) vs 25.58ms (A)" },
      { name: "Run-to-Run Consistency", formula: "Coefficient of variation (σ / μ)", status: "Active", value: "Uniform: 24.0% | Adaptive: 32.8%" }
    ]
  },
  {
    category: "Scaling Metrics",
    desc: "Behavior under increasing point cloud stress loads",
    metrics: [
      { name: "Input Point Cloud Load", formula: "[5k, 10k, 25k, 50k points]", status: "Active", value: "Evaluated over 5 runs each" },
      { name: "Latency Scaling Slope", formula: "ΔLatency / ΔPoints", status: "Active", value: "Uniform: ~2.35 ms/k | Adaptive: ~3.25 ms/k" },
      { name: "Throughput Drop-off", formula: "FPS at 50k vs FPS at 5k", status: "Active", value: "Uniform: 51.5→8.0 | Adaptive: 31.3→5.7" },
      { name: "Cell Saturation", formula: "Cells vs Point load", status: "Active", value: "Plateaus at 3,322 (U) & 3,560 (A)" }
    ]
  }
];

// 8. Research Insights (Honest & Objective)
export const RESEARCH_INSIGHTS = [
  {
    title: "Benchmark Pipeline is Fully Operational",
    status: "Validated",
    type: "success",
    content: "The synthetic point cloud generation, uniform grid rasterization, prototype multi-resolution mapping, and multi-run instrumentation pipeline are working reliably with clean CSV logging and statistical aggregation."
  },
  {
    title: "Prototype Adaptive Grid Exhibits Computational Overhead",
    status: "Observed",
    type: "warning",
    content: "The current pure-Python prototype Adaptive Grid is slower than the Uniform Grid (77.85 ms vs 49.84 ms average latency; 13.95 vs 21.14 FPS). This is expected because calculating Euclidean distances, branching logic per-point in Python, and generating 3-tuple keys ((cell_x, cell_y, resolution)) adds substantial interpreted overhead."
  },
  {
    title: "Prototype Occupied Cell Count is Higher for 10K Points",
    status: "Observed",
    type: "info",
    content: "The prototype generated 3,560 cells compared to Uniform's 3,322 cells. Because points within 10m and vehicle/pedestrian clusters are assigned fine 0.25m cells (4x finer area than 0.5m uniform), dense nearby clusters split into multiple smaller cells before distant coarse cells (1.0m) can offset the count."
  },
  {
    title: "Linear Latency Growth Under Point Scaling",
    status: "Observed",
    type: "info",
    content: "Both methods exhibit near-linear execution time growth as point load increases from 5,000 to 50,000. Adaptive latency climbs from 32.65 ms to 178.84 ms, while Uniform climbs from 20.48 ms to 126.29 ms."
  },
  {
    title: "Baseline Established for Future Optimized Engine",
    status: "Milestone",
    type: "milestone",
    content: "The current prototype serves as an essential empirical baseline. It establishes the testing infrastructure, verification harness, and baseline metrics against which the future optimized C++/Cython Adaptive Grid Engine will be evaluated."
  }
];
