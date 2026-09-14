import csv
import os

from data import generate_dummy_scene
from uniform_grid import create_uniform_grid
from adaptive_grid import create_adaptive_grid
from metrics import benchmark_function


POINT_COUNTS = [5000, 10000, 25000, 50000]
RUNS = 5


def create_point_cloud(point_count):
    full_cloud = generate_dummy_scene()

    if point_count <= len(full_cloud):
        return full_cloud[:point_count]

    # Repeat data if more points are required
    repeats = (point_count // len(full_cloud)) + 1
    expanded = full_cloud.tolist() * repeats

    return expanded[:point_count]


def main():

    os.makedirs("results", exist_ok=True)

    results = []

    print("\n========== POINT CLOUD SCALING BENCHMARK ==========")

    for point_count in POINT_COUNTS:

        print(f"\n\n******** {point_count} POINTS ********")

        point_cloud = create_point_cloud(point_count)

        for run in range(1, RUNS + 1):

            uniform_result = benchmark_function(
                create_uniform_grid,
                point_cloud,
                resolution=0.5
            )

            adaptive_result = benchmark_function(
                create_adaptive_grid,
                point_cloud
            )

            uniform_grid = uniform_result["result"]
            adaptive_grid = adaptive_result["result"]

            print(
                f"Run {run} | "
                f"Uniform: {uniform_result['latency_ms']:.2f} ms | "
                f"Adaptive: {adaptive_result['latency_ms']:.2f} ms"
            )

            results.append({
                "points": point_count,
                "run": run,
                "method": "Uniform",
                "cells": len(uniform_grid),
                "latency_ms": uniform_result["latency_ms"],
                "fps": uniform_result["fps"]
            })

            results.append({
                "points": point_count,
                "run": run,
                "method": "Adaptive",
                "cells": len(adaptive_grid),
                "latency_ms": adaptive_result["latency_ms"],
                "fps": adaptive_result["fps"]
            })

    filename = "results/scaling_benchmark.csv"

    with open(filename, "w", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "points",
                "run",
                "method",
                "cells",
                "latency_ms",
                "fps"
            ]
        )

        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to {filename}")


if __name__ == "__main__":
    main()