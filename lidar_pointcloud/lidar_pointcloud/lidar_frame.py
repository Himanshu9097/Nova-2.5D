"""
lidar_frame.py — Core LidarFrame dataclass.

This is the central data structure for the entire pipeline.
Every stage (converter, publisher, Vivek's segmentation) operates on LidarFrame objects.

Coordinate convention: ROS REP-103 (right-handed)
  x = forward, y = left, z = up, units = meters
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class LidarFrame:
    """A single LiDAR sweep in ROS coordinate convention.

    Attributes:
        frame_id:     Sequential frame number from CARLA simulation.
        timestamp:    Time of capture in seconds (simulation time or epoch).
        points:       (N, 3) float32 array of xyz coordinates in ROS convention (meters).
        intensity:    (N,) float32 array of per-point intensity values (0.0–1.0).
        sensor_pose:  (4, 4) float64 homogeneous transform, sensor frame → world frame.
        frame_ref:    ROS TF frame ID for this sensor. Default "lidar_link".
        num_channels: Number of vertical LiDAR channels (e.g. 32, 64). Metadata only.
    """

    frame_id: int
    timestamp: float
    points: np.ndarray       # (N, 3) float32
    intensity: np.ndarray    # (N,)   float32
    sensor_pose: np.ndarray  # (4, 4) float64
    frame_ref: str = "lidar_link"
    num_channels: int = 0

    def __post_init__(self):
        """Validate array shapes on construction."""
        assert self.points.ndim == 2 and self.points.shape[1] == 3, \
            f"points must be (N,3), got {self.points.shape}"
        assert self.intensity.ndim == 1, \
            f"intensity must be (N,), got {self.intensity.shape}"
        assert self.points.shape[0] == self.intensity.shape[0], \
            f"points/intensity length mismatch: {self.points.shape[0]} vs {self.intensity.shape[0]}"
        assert self.sensor_pose.shape == (4, 4), \
            f"sensor_pose must be (4,4), got {self.sensor_pose.shape}"

    @property
    def num_points(self) -> int:
        """Number of points in this sweep."""
        return self.points.shape[0]

    def as_xyzi(self) -> np.ndarray:
        """Return (N, 4) float32 array [x, y, z, intensity] — ready for PointCloud2."""
        return np.column_stack([self.points, self.intensity]).astype(np.float32)
