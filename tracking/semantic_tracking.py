"""CARLA-independent semantic-results to multi-object tracking integration."""

from typing import Mapping

from .detection_adapter import (
    ClusteringConfig,
    semantic_results_to_detections,
)
from .multi_object_tracker import MultiObjectTracker
from .schemas import Detection, TrackOutput


class SemanticTrackingPipeline:
    """Process semantic results through clustering and one persistent tracker."""

    def __init__(
        self,
        *,
        tracker: MultiObjectTracker | None = None,
        clustering_config: ClusteringConfig | None = None,
    ):
        self.tracker = tracker or MultiObjectTracker()
        self.clustering_config = clustering_config or ClusteringConfig()
        self.last_detections: tuple[Detection, ...] = ()

    def process_frame(
        self,
        results: Mapping[str, object],
        *,
        frame_id: int,
        timestamp: float,
        dt: float | None = None,
    ) -> list[TrackOutput]:
        """Convert one semantic frame and update the persistent tracker."""
        detections = semantic_results_to_detections(
            results,
            frame_id=frame_id,
            timestamp=timestamp,
            config=self.clustering_config,
        )
        self.last_detections = tuple(detections)
        return self.tracker.update(detections, dt=dt)
