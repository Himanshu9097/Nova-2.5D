"""Typed data structures used by the tracking module."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Detection:
    """One object-level position measurement."""

    class_id: int
    x: float
    y: float
    z: float
    confidence: float
    frame_id: int
    timestamp: float

    @property
    def position(self) -> tuple[float, float, float]:
        """Return the measured position as an (x, y, z) tuple."""
        return self.x, self.y, self.z


@dataclass(frozen=True)
class TrackOutput:
    """Public representation of a tracked object."""

    track_id: int
    class_id: int
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    dynamic_probability: float
    state: int
