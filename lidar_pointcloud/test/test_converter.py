"""
test_converter.py — Unit tests for the CARLA → LidarFrame converter.

Tests:
  1. Y-axis flip (CARLA left-handed → ROS right-handed)
  2. Array shape preservation
  3. Intensity passthrough
  4. File-based loading (.npy + .json)
  5. Edge cases (single point, empty cloud)

Run:
  cd lidar_pointcloud && python -m pytest test/ -v
"""

import json
import tempfile
import os

import numpy as np
import pytest

# Adjust import path for running outside colcon workspace
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lidar_pointcloud.lidar_frame import LidarFrame
from lidar_pointcloud.converter import carla_buffer_to_lidar_frame, npy_to_lidar_frame


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_identity_pose():
    return np.eye(4, dtype=np.float64)


def make_sample_raw(n_points=100):
    """Generate a synthetic CARLA-like raw (N,4) array."""
    rng = np.random.default_rng(42)
    xyz = rng.standard_normal((n_points, 3)).astype(np.float32) * 10.0
    intensity = rng.uniform(0, 1, size=(n_points, 1)).astype(np.float32)
    return np.hstack([xyz, intensity])


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCoordinateConversion:
    """Verify CARLA→ROS coordinate flip."""

    def test_y_axis_flipped(self):
        raw = np.array([[1.0, 2.0, 3.0, 0.5]], dtype=np.float32)
        buffer = raw.tobytes()
        frame = carla_buffer_to_lidar_frame(buffer, 0, 0.0, make_identity_pose())

        # x and z unchanged, y flipped
        np.testing.assert_almost_equal(frame.points[0, 0], 1.0)
        np.testing.assert_almost_equal(frame.points[0, 1], -2.0)  # flipped!
        np.testing.assert_almost_equal(frame.points[0, 2], 3.0)

    def test_intensity_passthrough(self):
        raw = np.array([[0.0, 0.0, 0.0, 0.75]], dtype=np.float32)
        buffer = raw.tobytes()
        frame = carla_buffer_to_lidar_frame(buffer, 0, 0.0, make_identity_pose())
        np.testing.assert_almost_equal(frame.intensity[0], 0.75)

    def test_multiple_points_shape(self):
        raw = make_sample_raw(500)
        buffer = raw.tobytes()
        frame = carla_buffer_to_lidar_frame(buffer, 1, 1.0, make_identity_pose())

        assert frame.points.shape == (500, 3)
        assert frame.intensity.shape == (500,)
        assert frame.num_points == 500

    def test_y_flip_vectorized(self):
        """Verify y-flip is applied to all points, not just the first."""
        raw = make_sample_raw(1000)
        buffer = raw.tobytes()
        frame = carla_buffer_to_lidar_frame(buffer, 0, 0.0, make_identity_pose())

        # All y values should be negated
        np.testing.assert_array_almost_equal(frame.points[:, 1], -raw[:, 1])
        # x and z should be unchanged
        np.testing.assert_array_almost_equal(frame.points[:, 0], raw[:, 0])
        np.testing.assert_array_almost_equal(frame.points[:, 2], raw[:, 2])


class TestFileLoading:
    """Verify .npy + .json file loading."""

    def test_npy_json_roundtrip(self):
        raw = make_sample_raw(200)
        meta = {
            "frame_id": 42,
            "timestamp": 123.456,
            "sensor_transform": np.eye(4).tolist(),
            "channels": 64,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            npy_path = os.path.join(tmpdir, "frame_0042.npy")
            json_path = os.path.join(tmpdir, "frame_0042.json")

            np.save(npy_path, raw)
            with open(json_path, "w") as f:
                json.dump(meta, f)

            frame = npy_to_lidar_frame(npy_path, json_path)

            assert frame.frame_id == 42
            assert frame.timestamp == 123.456
            assert frame.num_points == 200
            assert frame.num_channels == 64
            # y should be flipped
            np.testing.assert_array_almost_equal(frame.points[:, 1], -raw[:, 1])


class TestLidarFrame:
    """Verify LidarFrame dataclass behavior."""

    def test_as_xyzi(self):
        pts = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)
        inten = np.array([0.1, 0.9], dtype=np.float32)
        frame = LidarFrame(0, 0.0, pts, inten, make_identity_pose())
        xyzi = frame.as_xyzi()

        assert xyzi.shape == (2, 4)
        assert xyzi.dtype == np.float32
        np.testing.assert_almost_equal(xyzi[0], [1, 2, 3, 0.1])
        np.testing.assert_almost_equal(xyzi[1], [4, 5, 6, 0.9])

    def test_shape_validation_bad_points(self):
        with pytest.raises(AssertionError):
            LidarFrame(0, 0.0, np.zeros((10, 4)), np.zeros(10), make_identity_pose())

    def test_shape_validation_mismatch(self):
        with pytest.raises(AssertionError):
            LidarFrame(0, 0.0, np.zeros((10, 3)), np.zeros(5), make_identity_pose())

    def test_single_point(self):
        frame = LidarFrame(0, 0.0,
                           np.array([[1, 2, 3]], dtype=np.float32),
                           np.array([0.5], dtype=np.float32),
                           make_identity_pose())
        assert frame.num_points == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
