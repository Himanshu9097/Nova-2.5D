"""Convert point-level semantic LiDAR records into object detections."""

from dataclasses import dataclass
import math
from typing import Iterable, Mapping

from .schemas import Detection


@dataclass(frozen=True)
class ClusteringConfig:
    """Parameters for the lightweight semantic point clustering."""

    eps: float = 1.0
    min_points: int = 3
    confidence_threshold: float = 0.5

    def __post_init__(self) -> None:
        if self.eps <= 0:
            raise ValueError("eps must be positive")
        if self.min_points < 1:
            raise ValueError("min_points must be positive")
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be between 0 and 1")


def semantic_points_to_detections(
    semantic_points: Iterable[Mapping[str, object]],
    *,
    frame_id: int,
    timestamp: float,
    config: ClusteringConfig | None = None,
) -> list[Detection]:
    """Cluster semantic points and return object-level :class:`Detection` values.

    ``frame_id`` and ``timestamp`` are required caller metadata. The adapter
    does not infer or generate either value.
    """
    settings = config or ClusteringConfig()
    valid_points = _valid_points(semantic_points, settings.confidence_threshold)
    detections: list[Detection] = []

    points_by_class: dict[int, list[tuple[float, float, float]]] = {}
    for point in valid_points:
        points_by_class.setdefault(point[3], []).append(point[:3])

    for class_id in sorted(points_by_class):
        for cluster in _clusters(points_by_class[class_id], settings.eps):
            if len(cluster) < settings.min_points:
                continue
            centroid = tuple(
                sum(point[axis] for point in cluster) / len(cluster)
                for axis in range(3)
            )
            cluster_confidences = _cluster_confidences(
                valid_points, class_id, cluster
            )
            detections.append(Detection(
                class_id=class_id,
                x=centroid[0],
                y=centroid[1],
                z=centroid[2],
                confidence=sum(cluster_confidences) / len(cluster_confidences),
                frame_id=frame_id,
                timestamp=timestamp,
            ))
    return detections


def semantic_results_to_detections(
    results: Mapping[str, object],
    *,
    frame_id: int,
    timestamp: float,
    config: ClusteringConfig | None = None,
) -> list[Detection]:
    """Adapt Vivek's ``{"points": [...]}`` result to object detections.

    Frame and timestamp metadata remain the caller's responsibility. This
    helper only unwraps the verified result shape and reuses the existing
    point-level clustering implementation.
    """
    if "points" not in results:
        raise KeyError("semantic results must contain a 'points' field")
    semantic_points = results["points"]
    if isinstance(semantic_points, (str, bytes)) or not isinstance(
        semantic_points, Iterable
    ):
        raise TypeError("semantic results 'points' field must be iterable")
    return semantic_points_to_detections(
        semantic_points,
        frame_id=frame_id,
        timestamp=timestamp,
        config=config,
    )


def _valid_points(
    semantic_points: Iterable[Mapping[str, object]],
    confidence_threshold: float,
) -> list[tuple[float, float, float, int, float]]:
    valid: list[tuple[float, float, float, int, float]] = []
    for point in semantic_points:
        try:
            x = float(point["x"])
            y = float(point["y"])
            z = float(point["z"])
            class_id = int(point["semantic_class"])
            confidence = float(point["confidence"])
        except (KeyError, TypeError, ValueError):
            continue
        if not all(math.isfinite(value) for value in (x, y, z, confidence)):
            continue
        if not 0.0 <= confidence <= 1.0 or confidence < confidence_threshold:
            continue
        valid.append((x, y, z, class_id, confidence))
    return valid


def _clusters(
    points: list[tuple[float, float, float]],
    eps: float,
) -> list[list[tuple[float, float, float]]]:
    """Return connected spatial components using an O(n^2) distance search."""
    eps_squared = eps * eps
    unvisited = set(range(len(points)))
    clusters: list[list[tuple[float, float, float]]] = []

    while unvisited:
        seed = unvisited.pop()
        component_indices = [seed]
        pending = [seed]
        while pending:
            current = pending.pop()
            neighbors = [
                index for index in unvisited
                if _squared_distance(points[current], points[index]) <= eps_squared
            ]
            for index in neighbors:
                unvisited.remove(index)
                pending.append(index)
                component_indices.append(index)
        clusters.append([points[index] for index in component_indices])
    return clusters


def _cluster_confidences(
    valid_points: list[tuple[float, float, float, int, float]],
    class_id: int,
    cluster: list[tuple[float, float, float]],
) -> list[float]:
    """Match confidence values to a cluster while retaining duplicate points."""
    remaining = list(cluster)
    confidences: list[float] = []
    for x, y, z, point_class_id, confidence in valid_points:
        if point_class_id != class_id:
            continue
        for index, candidate in enumerate(remaining):
            if candidate == (x, y, z):
                confidences.append(confidence)
                remaining.pop(index)
                break
    return confidences


def _squared_distance(
    first: tuple[float, float, float],
    second: tuple[float, float, float],
) -> float:
    return sum((first[axis] - second[axis]) ** 2 for axis in range(3))
