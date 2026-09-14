from logger import save_results
from data import generate_dummy_scene
from uniform_grid import create_uniform_grid
from adaptive_grid import create_adaptive_grid
from metrics import benchmark_function


NUMBER_OF_RUNS = 10


def main():

    print("Generating LiDAR data...")

    point_cloud = generate_dummy_scene()

    print(f"Points generated: {len(point_cloud)}")

    all_results = []

    print(f"\nRunning benchmark for {NUMBER_OF_RUNS} runs...")

    for run in range(1, NUMBER_OF_RUNS + 1):

        print(f"\n========== RUN {run} ==========")

        # -----------------------------
        # Uniform Grid
        # -----------------------------

        uniform_result = benchmark_function(
            create_uniform_grid,
            point_cloud,
            resolution=0.5
        )

        uniform_grid = uniform_result["result"]

        print("\nUniform Grid")

        print(f"Cells   : {len(uniform_grid)}")

        print(
            f"Latency : "
            f"{uniform_result['latency_ms']:.3f} ms"
        )

        print(
            f"FPS     : "
            f"{uniform_result['fps']:.2f}"
        )

        print(
            f"Memory  : "
            f"{uniform_result['memory_mb']:.3f} MB"
        )


        # -----------------------------
        # Adaptive Grid
        # -----------------------------

        adaptive_result = benchmark_function(
            create_adaptive_grid,
            point_cloud
        )

        adaptive_grid = adaptive_result["result"]

        print("\nAdaptive Grid")

        print(f"Cells   : {len(adaptive_grid)}")

        print(
            f"Latency : "
            f"{adaptive_result['latency_ms']:.3f} ms"
        )

        print(
            f"FPS     : "
            f"{adaptive_result['fps']:.2f}"
        )

        print(
            f"Memory  : "
            f"{adaptive_result['memory_mb']:.3f} MB"
        )


        # -----------------------------
        # Store Results
        # -----------------------------

        all_results.append({
            "method": "Uniform",
            "run": run,
            "points": len(point_cloud),
            "cells": len(uniform_grid),
            "latency_ms": uniform_result["latency_ms"],
            "fps": uniform_result["fps"],
            "memory_mb": uniform_result["memory_mb"]
        })

        all_results.append({
            "method": "Adaptive",
            "run": run,
            "points": len(point_cloud),
            "cells": len(adaptive_grid),
            "latency_ms": adaptive_result["latency_ms"],
            "fps": adaptive_result["fps"],
            "memory_mb": adaptive_result["memory_mb"]
        })


    # -----------------------------
    # Save Results
    # -----------------------------

    save_results(
        all_results,
        "results/multi_run_benchmark.csv"
    )

    print(
        "\nAll benchmark results saved to "
        "results/multi_run_benchmark.csv"
    )


if __name__ == "__main__":
    main()