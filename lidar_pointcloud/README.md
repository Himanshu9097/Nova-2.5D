# LiDAR Point-Cloud Pipeline

CARLA LiDAR → `LidarFrame` → ROS2 `PointCloud2` → RViz2 visualization.

Part of the **DRDO/IDEX SIH** foveated 2.5D elevation-map project.

## Quick Start (WSL2 Ubuntu 22.04)

```bash
# 1. Build the package
cd ~/ros2_ws/src
ln -s /mnt/c/Users/Sahil\ Kumar/OneDrive/Desktop/SIH/lidar_pointcloud .
cd ~/ros2_ws && colcon build --packages-select lidar_pointcloud
source install/setup.bash

# 2. Generate test data (no real CARLA data needed)
cd /mnt/c/Users/Sahil\ Kumar/OneDrive/Desktop/SIH/lidar_pointcloud
python3 test/generate_sample_data.py --output_dir /tmp/lidar_test --num_frames 50

# 3. Launch the pipeline
ros2 launch lidar_pointcloud lidar_pipeline.launch.py data_dir:=/tmp/lidar_test

# 4. Open RViz2 with saved config
rviz2 -d config/lidar.rviz
```

## Package Structure

```
lidar_pointcloud/
├── lidar_pointcloud/
│   ├── lidar_frame.py             # Core LidarFrame dataclass
│   ├── converter.py               # CARLA → ROS coordinate conversion
│   ├── file_source.py             # .npy/.json file reader
│   ├── carla_source.py            # Live CARLA stream (Phase 2)
│   └── pointcloud_publisher.py    # ROS2 node → PointCloud2
├── config/lidar.rviz              # RViz2 saved config
├── launch/lidar_pipeline.launch.py
└── test/
    ├── test_converter.py          # Unit tests
    └── generate_sample_data.py    # Synthetic data generator
```

## Data Format

See [`docs/DATA_FORMAT_FOR_YUVRAJ.md`](../docs/DATA_FORMAT_FOR_YUVRAJ.md) for the full spec.

**TL;DR:** Each frame = `frame_NNNN.npy` (N×4 float32: x,y,z,intensity in CARLA coords) + `frame_NNNN.json` (metadata).

## ROS2 Interface

| Topic | Type | Description |
|-------|------|-------------|
| `/carla/lidar/points` | `sensor_msgs/PointCloud2` | Raw point cloud (XYZI) |
| TF: `map` → `lidar_link` | Static | Sensor frame |

## Team Interfaces

- **← Yuvraj:** Provides `.npy` + `.json` frame exports (or live CARLA stream in Phase 2)
- **→ Vivek:** Subscribes to `/carla/lidar/points` for semantic segmentation
- **→ Riddhima:** Benchmarks FPS, latency, memory on the published topic
