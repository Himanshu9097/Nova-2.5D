"""
Benchmark Execution Runner for NOVA-2.5D

Reuses existing Python benchmark algorithms in benchmark/ directly without duplication.
Executes multi-run evaluations, computes statistical distributions, and extracts
representative 2.5D output grid structures.
"""

import sys
import os
import statistics
import numpy as np

# Ensure benchmark/ is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCHMARK_DIR = os.path.join(PROJECT_ROOT, "benchmark")
if BENCHMARK_DIR not in sys.path:
    sys.path.insert(0, BENCHMARK_DIR)

from uniform_grid import create_uniform_grid
from adaptive_grid import create_adaptive_grid
from metrics import benchmark_function


def run_benchmark_suite(
    point_cloud: np.ndarray,
    dataset_name: str = "Custom Dataset",
    uniform_resolution: float = 0.5,
    runs_count: int = 10,
    has_semantics: bool = True
) -> dict:
    """
    Executes an empirical benchmark suite over the provided point cloud.
    """
    total_points = len(point_cloud)
    runs_count = max(1, min(runs_count, 25))  # Safe bounds: 1 to 25 runs

    uniform_runs = []
    adaptive_runs = []
    paired_runs = []

    last_uniform_grid = None
    last_adaptive_grid = None

    for r in range(1, runs_count + 1):
        # 1. Run Uniform Grid
        u_bench = benchmark_function(create_uniform_grid, point_cloud, resolution=uniform_resolution)
        uniform_grid = u_bench["result"]
        last_uniform_grid = uniform_grid

        u_data = {
            "run": r,
            "method": "Uniform",
            "points": total_points,
            "cells": len(uniform_grid),
            "latency_ms": round(float(u_bench["latency_ms"]), 3),
            "fps": round(float(u_bench["fps"]), 2),
            "memory_mb": round(float(u_bench["memory_mb"]), 3)
        }
        uniform_runs.append(u_data)

        # 2. Run Adaptive Grid
        a_bench = benchmark_function(create_adaptive_grid, point_cloud)
        adaptive_grid = a_bench["result"]
        last_adaptive_grid = adaptive_grid

        a_data = {
            "run": r,
            "method": "Adaptive",
            "points": total_points,
            "cells": len(adaptive_grid),
            "latency_ms": round(float(a_bench["latency_ms"]), 3),
            "fps": round(float(a_bench["fps"]), 2),
            "memory_mb": round(float(a_bench["memory_mb"]), 3)
        }
        adaptive_runs.append(a_data)

        paired_runs.append({
            "run": f"Run {r}",
            "runNum": r,
            "uniformLatency": u_data["latency_ms"],
            "adaptiveLatency": a_data["latency_ms"],
            "uniformFps": u_data["fps"],
            "adaptiveFps": a_data["fps"],
            "uniformCells": u_data["cells"],
            "adaptiveCells": a_data["cells"],
            "uniformMemory": u_data["memory_mb"],
            "adaptiveMemory": a_data["memory_mb"]
        })

    # Statistical Aggregation
    def compute_stats(runs_list):
        latencies = [r["latency_ms"] for r in runs_list]
        fps_list = [r["fps"] for r in runs_list]
        cells_list = [r["cells"] for r in runs_list]
        memories = [r["memory_mb"] for r in runs_list]

        return {
            "runs_count": len(runs_list),
            "cells_mean": round(statistics.mean(cells_list), 2),
            "cells_std": round(statistics.stdev(cells_list), 2) if len(cells_list) > 1 else 0.0,
            "latency_mean": round(statistics.mean(latencies), 3),
            "latency_std": round(statistics.stdev(latencies), 3) if len(latencies) > 1 else 0.0,
            "latency_min": round(min(latencies), 3),
            "latency_max": round(max(latencies), 3),
            "fps_mean": round(statistics.mean(fps_list), 2),
            "fps_std": round(statistics.stdev(fps_list), 2) if len(fps_list) > 1 else 0.0,
            "fps_min": round(min(fps_list), 2),
            "fps_max": round(max(fps_list), 2),
            "memory_mean": round(statistics.mean(memories), 3),
            "memory_std": round(statistics.stdev(memories), 3) if len(memories) > 1 else 0.0,
        }

    u_stats = compute_stats(uniform_runs)
    a_stats = compute_stats(adaptive_runs)

    # Comparative deltas
    cell_diff = a_stats["cells_mean"] - u_stats["cells_mean"]
    cell_diff_pct = round((cell_diff / u_stats["cells_mean"]) * 100, 2) if u_stats["cells_mean"] > 0 else 0

    latency_diff = a_stats["latency_mean"] - u_stats["latency_mean"]
    latency_diff_pct = round((latency_diff / u_stats["latency_mean"]) * 100, 2) if u_stats["latency_mean"] > 0 else 0

    fps_diff = a_stats["fps_mean"] - u_stats["fps_mean"]
    fps_diff_pct = round((fps_diff / u_stats["fps_mean"]) * 100, 2) if u_stats["fps_mean"] > 0 else 0

    # Extract 2.5D Output Map Sample (downsample to ~300 cells for snappy browser visualization)
    def extract_output_map(grid_dict, max_samples=300):
        items = list(grid_dict.items())
        stride = max(1, len(items) // max_samples)
        sampled = []
        for i in range(0, len(items), stride):
            cell_id, data = items[i]
            # uniform key: (cx, cy)
            # adaptive key: (cx, cy, res)
            if len(cell_id) == 2:
                cx, cy = cell_id
                res = uniform_resolution
            else:
                cx, cy, res = cell_id

            sampled.append({
                "cell_x": int(cx),
                "cell_y": int(cy),
                "resolution": float(res),
                "max_height": round(float(data.get("max_height", 0.0)), 2),
                "point_count": len(data.get("points", [])),
                "semantic_class": int(data["semantic_classes"][0]) if data.get("semantic_classes") else None
            })
            if len(sampled) >= max_samples:
                break
        return sampled

    uniform_map = extract_output_map(last_uniform_grid) if last_uniform_grid else []
    adaptive_map = extract_output_map(last_adaptive_grid) if last_adaptive_grid else []

    return {
        "dataset": {
            "name": dataset_name,
            "points": total_points,
            "has_semantics": has_semantics,
            "uniform_resolution": uniform_resolution,
            "runs_count": runs_count
        },
        "uniform": u_stats,
        "adaptive": a_stats,
        "comparison": {
            "cell_diff": cell_diff,
            "cell_diff_pct": cell_diff_pct,
            "latency_diff_ms": round(latency_diff, 3),
            "latency_diff_pct": latency_diff_pct,
            "fps_diff": round(fps_diff, 2),
            "fps_diff_pct": fps_diff_pct
        },
        "runs": {
            "paired": paired_runs,
            "uniform": uniform_runs,
            "adaptive": adaptive_runs
        },
        "output_map": {
            "uniform_cells_sample": uniform_map,
            "adaptive_cells_sample": adaptive_map,
            "total_uniform_cells": len(last_uniform_grid) if last_uniform_grid else 0,
            "total_adaptive_cells": len(last_adaptive_grid) if last_adaptive_grid else 0
        }
    }
