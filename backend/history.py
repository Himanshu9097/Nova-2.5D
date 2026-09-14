"""
Persistent Benchmark History Storage for NOVA-2.5D

Maintains an archived JSON history of all completed benchmarks on disk,
seeded with the default Synthetic LiDAR 10K baseline.
"""

import os
import json
import time
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "benchmark_history.json")


def get_default_baseline():
    return {
        "id": "baseline_synthetic_10k",
        "timestamp": "2026-09-12T12:00:00Z",
        "formatted_date": "Sept 12, 2026 (Baseline)",
        "dataset_name": "Synthetic LiDAR Scene (Seed 42)",
        "is_baseline": True,
        "points": 10000,
        "has_semantics": True,
        "uniform_fps": 21.14,
        "adaptive_fps": 13.95,
        "uniform_latency_ms": 49.840,
        "adaptive_latency_ms": 77.852,
        "uniform_cells": 3322,
        "adaptive_cells": 3560,
        "runs_count": 10
    }


def load_history() -> list:
    if not os.path.exists(HISTORY_FILE):
        initial = [get_default_baseline()]
        save_all_history(initial)
        return initial

    try:
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)
            if not isinstance(data, list) or len(data) == 0:
                return [get_default_baseline()]
            return data
    except Exception:
        return [get_default_baseline()]


def save_all_history(items: list):
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(items, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save history: {e}")


def add_history_entry(result: dict) -> str:
    history = load_history()
    now = datetime.utcnow()
    run_id = f"run_{int(time.time())}"

    summary = {
        "id": run_id,
        "timestamp": now.isoformat() + "Z",
        "formatted_date": now.strftime("%b %d, %Y - %H:%M UTC"),
        "dataset_name": result["dataset"]["name"],
        "is_baseline": False,
        "points": result["dataset"]["points"],
        "has_semantics": result["dataset"]["has_semantics"],
        "uniform_fps": result["uniform"]["fps_mean"],
        "adaptive_fps": result["adaptive"]["fps_mean"],
        "uniform_latency_ms": result["uniform"]["latency_mean"],
        "adaptive_latency_ms": result["adaptive"]["latency_mean"],
        "uniform_cells": result["uniform"]["cells_mean"],
        "adaptive_cells": result["adaptive"]["cells_mean"],
        "runs_count": result["dataset"]["runs_count"],
        "full_result": result
    }

    # Prepend new run right after or before
    history.insert(0, summary)
    save_all_history(history[:50])  # Keep last 50 runs
    return run_id


def get_history_by_id(run_id: str):
    history = load_history()
    for item in history:
        if item.get("id") == run_id:
            return item
    return None
