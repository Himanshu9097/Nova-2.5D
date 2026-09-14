import time
import os
import psutil


def get_memory_usage_mb():
    """
    Get current process memory usage in MB.
    """

    process = psutil.Process(os.getpid())

    memory = process.memory_info().rss

    return memory / (1024 * 1024)


def benchmark_function(function, *args, **kwargs):
    """
    Measure execution time and memory usage
    of a mapping function.
    """

    memory_before = get_memory_usage_mb()

    start_time = time.perf_counter()

    result = function(*args, **kwargs)

    end_time = time.perf_counter()

    memory_after = get_memory_usage_mb()

    latency = end_time - start_time

    latency_ms = latency * 1000

    if latency > 0:
        fps = 1 / latency
    else:
        fps = 0

    memory_used = max(
        0,
        memory_after - memory_before
    )

    return {
        "latency_ms": latency_ms,
        "fps": fps,
        "memory_mb": memory_used,
        "result": result
    }