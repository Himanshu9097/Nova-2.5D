import csv
import statistics


def load_results(filename="results/scaling_benchmark.csv"):

    results = []

    with open(filename, "r") as file:

        reader = csv.DictReader(file)

        for row in reader:

            results.append({
                "points": int(row["points"]),
                "run": int(row["run"]),
                "method": row["method"],
                "cells": int(row["cells"]),
                "latency_ms": float(row["latency_ms"]),
                "fps": float(row["fps"])
            })

    return results


def calculate_statistics():

    results = load_results()

    point_counts = sorted(
        set(result["points"] for result in results)
    )

    print("\n========== SCALING STATISTICAL SUMMARY ==========")

    for points in point_counts:

        print(f"\n\n===== {points} POINTS =====")

        for method in ["Uniform", "Adaptive"]:

            data = [
                result
                for result in results
                if result["points"] == points
                and result["method"] == method
            ]

            latency = [
                result["latency_ms"]
                for result in data
            ]

            fps = [
                result["fps"]
                for result in data
            ]

            cells = [
                result["cells"]
                for result in data
            ]

            print(f"\n{method}")
            print(f"Average Cells : {statistics.mean(cells):.2f}")
            print(f"Latency Mean  : {statistics.mean(latency):.3f} ms")
            print(f"Latency Std   : {statistics.stdev(latency):.3f} ms")
            print(f"FPS Mean      : {statistics.mean(fps):.2f}")
            print(f"FPS Std       : {statistics.stdev(fps):.2f}")


if __name__ == "__main__":
    calculate_statistics()