"""Track lifecycle and public output representation."""

from enum import IntEnum
import math
from typing import Optional

from .dynamic_probability import DynamicProbabilityConfig, dynamic_probability
from .kalman_filter import KalmanFilter
from .schemas import Detection, TrackOutput


class TrackState(IntEnum):
    """Track lifecycle states."""

    TENTATIVE = 0
    CONFIRMED = 1
    LOST = 2


class Track:
    """A single class-specific object track."""

    _next_track_id = 1

    def __init__(
        self,
        detection: Detection,
        *,
        confirmation_hits: int = 3,
        max_missed_frames: int = 3,
        kalman_filter: Optional[KalmanFilter] = None,
        probability_config: Optional[DynamicProbabilityConfig] = None,
    ):
        if confirmation_hits < 1 or max_missed_frames < 1:
            raise ValueError("confirmation_hits and max_missed_frames must be positive")
        self.track_id = Track._next_track_id
        Track._next_track_id += 1
        self.class_id = detection.class_id
        self.confidence = detection.confidence
        self.hits = 1
        self.missed_frames = 0
        self.confirmation_hits = confirmation_hits
        self.max_missed_frames = max_missed_frames
        self.probability_config = probability_config or DynamicProbabilityConfig()
        self.filter = kalman_filter or KalmanFilter(detection.position)
        self.state = TrackState.TENTATIVE
        if self.hits >= self.confirmation_hits:
            self.state = TrackState.CONFIRMED

    def predict(self, dt: float) -> tuple[float, float, float]:
        """Predict the next position."""
        return self.filter.predict(dt)

    def update(self, detection: Detection) -> None:
        """Apply a matching detection and update lifecycle counters."""
        if detection.class_id != self.class_id:
            raise ValueError("detection class_id does not match track class_id")
        self.filter.update(detection.position)
        self.confidence = detection.confidence
        self.hits += 1
        self.missed_frames = 0
        if self.state == TrackState.TENTATIVE and self.hits >= self.confirmation_hits:
            self.state = TrackState.CONFIRMED
        elif self.state == TrackState.LOST:
            self.state = TrackState.CONFIRMED

    def mark_missed(self) -> None:
        """Record a frame without a matching detection."""
        self.missed_frames += 1
        if self.missed_frames >= self.max_missed_frames:
            self.state = TrackState.LOST

    def to_output(self) -> TrackOutput:
        """Return the track in the team-facing output shape."""
        position = self.filter.position
        velocity = self.filter.velocity
        probability = dynamic_probability(velocity, self.probability_config)
        return TrackOutput(
            track_id=self.track_id,
            class_id=self.class_id,
            x=position[0],
            y=position[1],
            z=position[2],
            vx=velocity[0],
            vy=velocity[1],
            vz=velocity[2],
            dynamic_probability=probability,
            state=int(self.state),
        )

    @property
    def speed(self) -> float:
        """Return the estimated speed."""
        return math.sqrt(sum(component * component for component in self.filter.velocity))
