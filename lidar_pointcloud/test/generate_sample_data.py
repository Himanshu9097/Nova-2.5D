"""
generate_sample_data.py — Create synthetic LiDAR frames for testing.

Generates fake point clouds that mimic CARLA LiDAR output (a ground plane + some
objects) so you can test the full pipeline without waiting for Yuvraj's real data.

Usage:
  python generate_sample_data.py [--output_dir ./sample_data] [--num_frames 10]
"""

import json
import os
import argparse
import numpy as np


def generate_ground_plane(n_points=5000, extent=50.0, z_noise=0.05):
    """Generate points on a flat ground plane at z=0."""
    rng = np.random.default_rng(42)
    x = rng.uniform(-extent, extent, n_points)
    y = rng.uniform(-extent, extent, n_points)
    z = rng.normal(0, z_noise, n_points)  # slight noise around z=0
    intensity = rng.uniform(0.2, 0.5, n_points)  # low intensity for ground
    return np.column_stack([x, y, z, intensity]).astype(np.float32)


def generate_box_obstacle(center, size, n_points=500):
    """Generate points on the surface of a box obstacle."""
    rng = np.random.default_rng(hash(tuple(center)) % (2**31))
    cx, cy, cz = center
    sx, sy, sz = size

    # Points on box faces
    points = []
    for _ in range(n_points):
        face = rng.integers(6)
        if face == 0:   p = [cx + sx/2, cy + rng.uniform(-sy/2, sy/2), cz + rng.uniform(0, sz)]
        elif face == 1: p = [cx - sx/2, cy + rng.uniform(-sy/2, sy/2), cz + rng.uniform(0, sz)]
        elif face == 2: p = [cx + rng.uniform(-sx/2, sx/2), cy + sy/2, cz + rng.uniform(0, sz)]
        elif face == 3: p = [cx + rng.uniform(-sx/2, sx/2), cy - sy/2, cz + rng.uniform(0, sz)]
        elif face == 4: p = [cx + rng.uniform(-sx/2, sx/2), cy + rng.uniform(-sy/2, sy/2), cz + sz]
        else:           p = [cx + rng.uniform(-sx/2, sx/2), cy + rng.uniform(-sy/2, sy/2), cz]
        points.append(p)

    pts = np.array(points, dtype=np.float32)
    intensity = rng.uniform(0.6, 1.0, n_points).astype(np.float32)  # high intensity for obstacles
    return np.column_stack([pts, intensity])


def generate_frame(frame_id, timestamp):
    """Generate a single synthetic LiDAR frame in CARLA coordinates (left-handed)."""
    parts = [generate_ground_plane()]

    # A few box obstacles at various positions
    obstacles = [
        ([10, 5, 0], [2, 4, 2]),     # car-sized
        ([20, -3, 0], [1, 1, 3]),    # pole
        ([-5, 8, 0], [3, 3, 1.5]),   # low wall
        ([15, -10, 0], [2, 5, 2]),   # vehicle
        ([30, 0, 0], [1, 1, 1.8]),   # pedestrian
    ]
    for center, size in obstacles:
        parts.append(generate_box_obstacle(center, size, n_points=300))

    raw = np.vstack(parts)

    # Metadata (CARLA-style)
    meta = {
        "frame_id": frame_id,
        "timestamp": timestamp,
        "sensor_transform": np.eye(4).tolist(),
        "channels": 64,
        "range_m": 100.0,
        "points_per_second": 1200000,
        "rotation_frequency_hz": 20.0,
        "carla_map": "SyntheticTest",
        "ego_vehicle": "vehicle.synthetic.test",
    }

    return raw, meta


def main():
    parser = argparse.ArgumentParser(description='Generate synthetic LiDAR sample data')
    parser.add_argument('--output_dir', default='sample_data', help='Output directory')
    parser.add_argument('--num_frames', type=int, default=10, help='Number of frames')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    for i in range(args.num_frames):
        timestamp = i * 0.1  # 10 Hz
        raw, meta = generate_frame(i, timestamp)

        npy_path = os.path.join(args.output_dir, f"frame_{i:04d}.npy")
        json_path = os.path.join(args.output_dir, f"frame_{i:04d}.json")

        np.save(npy_path, raw)
        with open(json_path, "w") as f:
            json.dump(meta, f, indent=2)

        print(f"Frame {i:04d}: {raw.shape[0]} points → {npy_path}")

    print(f"\nDone! {args.num_frames} frames saved to {args.output_dir}/")
    print(f"Test with: ros2 launch lidar_pointcloud lidar_pipeline.launch.py data_dir:={os.path.abspath(args.output_dir)}")


if __name__ == '__main__':
    main()
