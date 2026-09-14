import csv
import matplotlib.pyplot as plt


def load_results(filename="results/benchmark.csv"):

    results = []

    with open(filename, "r") as file:

        reader = csv.DictReader(file)

        for row in reader:

            results.append({
                "method": row["method"],
                "points": int(row["points"]),
                "cells": int(row["cells"]),
                "latency_ms": float(row["latency_ms"]),
                "fps": float(row["fps"]),
                "memory_mb": float(row["memory_mb"])
            })

    return results


def create_graphs():

    results = load_results()

    methods = [result["method"] for result in results]

    cells = [result["cells"] for result in results]

    latency = [
        result["latency_ms"]
        for result in results
    ]

    fps = [
        result["fps"]
        for result in results
    ]

    memory = [
        result["memory_mb"]
        for result in results
    ]


    # -----------------------------
    # Cells Comparison
    # -----------------------------

    plt.figure()

    plt.bar(methods, cells)

    plt.title("Grid Cell Comparison")

    plt.ylabel("Number of Cells")

    plt.savefig(
        "results/cells_comparison.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


    # -----------------------------
    # Latency Comparison
    # -----------------------------

    plt.figure()

    plt.bar(methods, latency)

    plt.title("Latency Comparison")

    plt.ylabel("Latency (ms)")

    plt.savefig(
        "results/latency_comparison.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


    # -----------------------------
    # FPS Comparison
    # -----------------------------

    plt.figure()

    plt.bar(methods, fps)

    plt.title("FPS Comparison")

    plt.ylabel("Frames Per Second")

    plt.savefig(
        "results/fps_comparison.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


    # -----------------------------
    # Memory Comparison
    # -----------------------------

    plt.figure()

    plt.bar(methods, memory)

    plt.title("Memory Usage Comparison")

    plt.ylabel("Memory (MB)")

    plt.savefig(
        "results/memory_comparison.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


    print("Graphs generated successfully!")

    print("\nSaved files:")

    print("results/cells_comparison.png")

    print("results/latency_comparison.png")

    print("results/fps_comparison.png")

    print("results/memory_comparison.png")


if __name__ == "__main__":

    create_graphs()