"""Explainable nearest-distance association for multiple object tracks."""

import math
from typing import Iterable

from .schemas import Detection, TrackOutput
from .track import Track, TrackState


class MultiObjectTracker:
    """Maintain and associate multiple class-specific object tracks."""

    def __init__(
        self,
        *,
        association_distance: float = 2.5,
        confirmation_hits: int = 3,
        max_missed_frames: int = 3,
        default_dt: float = 1.0,
    ):
        if association_distance <= 0:
            raise ValueError("association_distance must be positive")
        if confirmation_hits < 1 or max_missed_frames < 1:
            raise ValueError("confirmation_hits and max_missed_frames must be positive")
        if default_dt <= 0:
            raise ValueError("default_dt must be positive")

        self.association_distance = float(association_distance)
        self.confirmation_hits = confirmation_hits
        self.max_missed_frames = max_missed_frames
        self.default_dt = float(default_dt)
        self._tracks: dict[int, Track] = {}
        self._last_timestamp: float | None = None

    @property
    def tracks(self) -> tuple[Track, ...]:
        """Return all tracks, including tracks currently marked Lost."""
        return tuple(self._tracks.values())

    def update(
        self,
        detections: Iterable[Detection],
        dt: float | None = None,
    ) -> list[TrackOutput]:
        """Predict, associate, update, and return all current track outputs."""
        detection_list = list(detections)
        timestep = self._resolve_dt(detection_list, dt)

        active_tracks = [
            track for track in self._tracks.values()
            if track.state != TrackState.LOST
        ]
        predictions = {
            track.track_id: track.predict(timestep)
            for track in active_tracks
        }
        matches = self._associate(active_tracks, predictions, detection_list)
        matched_track_ids = {track.track_id for track, _ in matches}
        matched_detection_indices = {index for _, index in matches}

        for track, detection_index in matches:
            track.update(detection_list[detection_index])

        for track in active_tracks:
            if track.track_id not in matched_track_ids:
                track.mark_missed()

        for detection_index, detection in enumerate(detection_list):
            if detection_index not in matched_detection_indices:
                track = Track(
                    detection,
                    confirmation_hits=self.confirmation_hits,
                    max_missed_frames=self.max_missed_frames,
                )
                self._tracks[track.track_id] = track

        return [track.to_output() for track in self._tracks.values()]

    def _resolve_dt(self, detections: list[Detection], dt: float | None) -> float:
        if dt is not None:
            if dt <= 0:
                raise ValueError("dt must be positive")
            timestep = float(dt)
        elif detections and self._last_timestamp is not None:
            timestep = detections[0].timestamp - self._last_timestamp
            if timestep <= 0:
                timestep = self.default_dt
        else:
            timestep = self.default_dt

        if detections:
            self._last_timestamp = detections[0].timestamp
        return timestep

    def _associate(
        self,
        tracks: list[Track],
        predictions: dict[int, tuple[float, float, float]],
        detections: list[Detection],
    ) -> list[tuple[Track, int]]:
        candidates: list[tuple[float, int, int]] = []
        for track_index, track in enumerate(tracks):
            predicted_position = predictions[track.track_id]
            for detection_index, detection in enumerate(detections):
                if detection.class_id != track.class_id:
                    continue
                distance = math.sqrt(sum(
                    (predicted_position[axis] - detection.position[axis]) ** 2
                    for axis in range(3)
                ))
                if distance <= self.association_distance:
                    candidates.append((distance, track_index, detection_index))

        matches: list[tuple[Track, int]] = []
        used_tracks: set[int] = set()
        used_detections: set[int] = set()
        for _, track_index, detection_index in sorted(candidates):
            if track_index in used_tracks or detection_index in used_detections:
                continue
            used_tracks.add(track_index)
            used_detections.add(detection_index)
            matches.append((tracks[track_index], detection_index))
        return matches
