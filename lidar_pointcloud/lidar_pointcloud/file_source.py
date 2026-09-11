"""
file_source.py — File-based LiDAR data source.

Reads .npy/.json frame pairs from Yuvraj's CARLA exports and yields LidarFrame objects.
Supports both single-frame loading and sequential playback of a directory.

This is the Phase 1 data source (file-based).
Phase 2 will add carla_source.py for live CARLA streaming.
"""

import time
from pathlib import Path
from typing import Generator, Optional

from .converter import npy_to_lidar_frame, load_sequence
from .lidar_frame import LidarFrame


class FileSource:
    """Iterate over exported LiDAR frames from a directory.

    Usage:
        source = FileSource("path/to/lidar_export")
        for frame in source.play(rate_hz=10.0):
            publisher.publish(frame)
    """

    def __init__(self, directory: str):
        """Initialize with a directory containing frame_NNNN.npy/json pairs.

        Args:
            directory: Path to the export directory.
        """
        self.directory = Path(directory)
        self._frames: Optional[list] = None

    @property
    def frames(self) -> list:
        """Lazy-load all frames from disk."""
        if self._frames is None:
            self._frames = load_sequence(str(self.directory))
            print(f"[FileSource] Loaded {len(self._frames)} frames from {self.directory}")
        return self._frames

    @property
    def num_frames(self) -> int:
        return len(self.frames)

    def get_frame(self, index: int) -> LidarFrame:
        """Get a single frame by index."""
        return self.frames[index]

    def play(self, rate_hz: float = 10.0, loop: bool = False) -> Generator[LidarFrame, None, None]:
        """Yield frames at a fixed rate, simulating real-time playback.

        Args:
            rate_hz: Playback rate in Hz (frames per second). Default 10 Hz.
            loop:    If True, loop back to start after the last frame.

        Yields:
            LidarFrame objects at the specified rate.
        """
        period = 1.0 / rate_hz

        while True:
            for frame in self.frames:
                t_start = time.monotonic()
                yield frame
                elapsed = time.monotonic() - t_start
                sleep_time = period - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)

            if not loop:
                break
