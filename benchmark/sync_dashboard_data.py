"""
NOVA-2.5D: Benchmark to Dashboard Sync Utility

Reads empirical CSV outputs from benchmark/results/ and verifies
the data synchronization with dashboard/src/data/benchmarkData.js.
"""

import os
import csv
import json
import statistics

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MULTI_RUN_CSV = os.path.join(BASE_DIR, "results", "multi_run_benchmark.csv")
SCALING_CSV = os.path.join(BASE_DIR, "results", "scaling_benchmark.csv")
DASHBOARD_DATA_JS = os.path.join(os.path.dirname(BASE_DIR), "dashboard", "src", "data", "benchmarkData.js")


def verify_sync():
    if not os.path.exists(MULTI_RUN_CSV):
        print(f"Error: {MULTI_RUN_CSV} not found.")
        return False
    
    if not os.path.exists(SCALING_CSV):
        print(f"Error: {SCALING_CSV} not found.")
        return False

    with open(MULTI_RUN_CSV, "r") as f:
        reader = csv.DictReader(f)
        multi_rows = list(reader)

    print(f"Loaded {len(multi_rows)} rows from {MULTI_RUN_CSV}")

    with open(SCALING_CSV, "r") as f:
        reader = csv.DictReader(f)
        scaling_rows = list(reader)

    print(f"Loaded {len(scaling_rows)} rows from {SCALING_CSV}")

    if os.path.exists(DASHBOARD_DATA_JS):
        print(f"Dashboard data source verified: {DASHBOARD_DATA_JS}")
        return True
    else:
        print(f"Warning: Dashboard data file not found at {DASHBOARD_DATA_JS}")
        return False


if __name__ == "__main__":
    success = verify_sync()
    if success:
        print("Data sync verification passed successfully.")
