import csv
import os


def save_results(results, filename="results/benchmark.csv"):

    os.makedirs("results", exist_ok=True)

    file_exists = os.path.exists(filename)

    with open(filename, "a", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "method",
                "run",
                "points",
                "cells",
                "latency_ms",
                "fps",
                "memory_mb"
            ]
        )

        if not file_exists:
            writer.writeheader()

        for result in results:
            writer.writerow(result)