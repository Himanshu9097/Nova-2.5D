import csv
import statistics


def load_results(filename="results/multi_run_benchmark.csv"):

    results = []

    with open(filename, "r") as file:

        reader = csv.DictReader(file)

        for row in reader:

            results.append({
                "method": row["method"],
                "run": int(row["run"]),
                "points": int(row["points"]),
                "cells": int(row["cells"]),
                "latency_ms": float(row["latency_ms"]),
                "fps": float(row["fps"]),
                "memory_mb": float(row["memory_mb"])
            })

    return results


def calculate_statistics():

    results = load_results()

    uniform = [
        result
        for result in results
        if result["method"] == "Uniform"
    ]

    adaptive = [
        result
        for result in results
        if result["method"] == "Adaptive"
    ]


    print("\n========== STATISTICAL SUMMARY ==========")


    for name, data in [
        ("Uniform Grid", uniform),
        ("Adaptive Grid", adaptive)
    ]:

        latency_values = [
            result["latency_ms"]
            for result in data
        ]

        fps_values = [
            result["fps"]
            for result in data
        ]

        cell_values = [
            result["cells"]
            for result in data
        ]


        latency_mean = statistics.mean(latency_values)
        latency_std = statistics.stdev(latency_values)

        fps_mean = statistics.mean(fps_values)
        fps_std = statistics.stdev(fps_values)

        cells_mean = statistics.mean(cell_values)


        print(f"\n{name}")

        print(
            f"Average Cells   : "
            f"{cells_mean:.2f}"
        )

        print(
            f"Latency Mean    : "
            f"{latency_mean:.3f} ms"
        )

        print(
            f"Latency Std Dev : "
            f"{latency_std:.3f} ms"
        )

        print(
            f"FPS Mean        : "
            f"{fps_mean:.2f}"
        )

        print(
            f"FPS Std Dev     : "
            f"{fps_std:.2f}"
        )


if __name__ == "__main__":

    calculate_statistics()