"""
converter.py — Raw CARLA LiDAR data → LidarFrame.

Handles the CARLA (left-handed) → ROS REP-103 (right-handed) coordinate conversion.
All operations are vectorized with numpy — no per-point Python loops.

Coordinate fix:
  CARLA:  x=forward, y=RIGHT, z=up   (left-handed)
  ROS:    x=forward, y=LEFT,  z=up   (right-handed)
  → y_ros = -y_carla
"""

import json
from pathlib import Path

import numpy as np

from .lidar_frame import LidarFrame


def carla_buffer_to_lidar_frame(
    buffer: bytes,
    frame_id: int,
    timestamp: float,
    sensor_pose: np.ndarray,
    num_channels: int = 0,
) -> LidarFrame:
    """Convert raw CARLA LiDAR byte buffer to a LidarFrame.

    Args:
        buffer:       Raw bytes from carla.LidarMeasurement.raw_data
        frame_id:     Frame sequence number
        timestamp:    Simulation timestamp (seconds)
        sensor_pose:  (4,4) sensor-to-world transform (CARLA coords — will be kept as-is)
        num_channels: Number of LiDAR channels (metadata)

    Returns:
        LidarFrame with points in ROS coordinate convention.
    """
    raw = np.frombuffer(buffer, dtype=np.float32).reshape(-1, 4)
    return _raw_array_to_frame(raw, frame_id, timestamp, sensor_pose, num_channels)


def npy_to_lidar_frame(npy_path: str, meta_path: str) -> LidarFrame:
    """Load a LidarFrame from Yuvraj's exported .npy + .json files.

    Args:
        npy_path:  Path to the (N,4) float32 .npy file [x, y, z, intensity] in CARLA coords.
        meta_path: Path to the companion .json metadata file.

    Returns:
        LidarFrame with points in ROS coordinate convention.
    """
    raw = np.load(npy_path).astype(np.float32)
    assert raw.ndim == 2 and raw.shape[1] == 4, \
        f"Expected (N,4) array, got {raw.shape} from {npy_path}"

    with open(meta_path, "r") as f:
        meta = json.load(f)

    sensor_pose = np.array(meta["sensor_transform"], dtype=np.float64)
    return _raw_array_to_frame(
        raw,
        frame_id=meta["frame_id"],
        timestamp=meta["timestamp"],
        sensor_pose=sensor_pose,
        num_channels=meta.get("channels", 0),
    )


def load_sequence(directory: str) -> list:
    """Load all frames from a directory of .npy/.json pairs, sorted by frame_id.

    Args:
        directory: Path to directory containing frame_NNNN.npy / frame_NNNN.json pairs.

    Returns:
        List of LidarFrame objects, sorted by frame_id.
    """
    dirpath = Path(directory)
    npy_files = sorted(dirpath.glob("frame_*.npy"))

    frames = []
    for npy_file in npy_files:
        json_file = npy_file.with_suffix(".json")
        if not json_file.exists():
            print(f"[WARN] Missing metadata for {npy_file.name}, skipping")
            continue
        frames.append(npy_to_lidar_frame(str(npy_file), str(json_file)))

    return frames


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _raw_array_to_frame(
    raw: np.ndarray,
    frame_id: int,
    timestamp: float,
    sensor_pose: np.ndarray,
    num_channels: int,
) -> LidarFrame:
    """Shared conversion: raw (N,4) CARLA array → LidarFrame (ROS coords).

    This is the single place where the CARLA→ROS y-flip happens.
    """
    xyz = raw[:, :3].copy()
    xyz[:, 1] *= -1.0  # CARLA left-handed → ROS right-handed

    return LidarFrame(
        frame_id=frame_id,
        timestamp=timestamp,
        points=xyz,
        intensity=raw[:, 3].copy(),
        sensor_pose=sensor_pose,
        num_channels=num_channels,
    )
