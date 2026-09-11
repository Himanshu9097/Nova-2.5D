# Interface Doc — LiDAR PointCloud2 for Vivek (Segmentation)

> **From:** Sahil (LiDAR pipeline)  
> **To:** Vivek (Semantic segmentation — PointNet++ / Sparse CNN)  
> **What you get:** Raw 3D point clouds on a ROS2 topic, ready to feed into your model.

---

## The short version

Subscribe to this ROS2 topic and you get LiDAR point clouds:

```
Topic:   /carla/lidar/points
Type:    sensor_msgs/msg/PointCloud2
Rate:    10 Hz
Frame:   lidar_link
Fields:  x (float32), y (float32), z (float32), intensity (float32)
Points:  ~6,500 per frame (synthetic) / up to 100k+ with real CARLA data
Coords:  ROS REP-103 (x=forward, y=left, z=up, meters)
```

---

## How to subscribe (Python — copy-paste ready)

### Option A: Simple numpy subscriber (recommended to start)

```python
"""
vivek_subscriber.py — Minimal subscriber that receives point clouds as numpy arrays.

Run alongside Sahil's publisher:
  Terminal 1: ros2 launch lidar_pointcloud lidar_pipeline.launch.py data_dir:=/tmp/lidar_test
  Terminal 2: python3 vivek_subscriber.py
"""

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2


class PointCloudSubscriber(Node):
    def __init__(self):
        super().__init__('segmentation_subscriber')
        self.subscription = self.create_subscription(
            PointCloud2,
            '/carla/lidar/points',
            self.callback,
            10
        )
        self.get_logger().info('Subscribed to /carla/lidar/points — waiting for data...')

    def callback(self, msg: PointCloud2):
        # Convert PointCloud2 bytes → numpy (N, 4) array [x, y, z, intensity]
        points = np.frombuffer(msg.data, dtype=np.float32).reshape(-1, 4)

        xyz = points[:, :3]          # (N, 3) — feed this to your model
        intensity = points[:, 3]     # (N,)   — optional feature channel

        self.get_logger().info(
            f'Frame received: {xyz.shape[0]} points, '
            f'x=[{xyz[:,0].min():.1f}, {xyz[:,0].max():.1f}], '
            f'z=[{xyz[:,2].min():.1f}, {xyz[:,2].max():.1f}]'
        )

        # ─── YOUR SEGMENTATION CODE GOES HERE ───
        # labels = your_model.predict(xyz)          # (N,) int — class per point
        # publish_segmented_cloud(xyz, labels)      # publish back for viz
        # ─────────────────────────────────────────


def main():
    rclpy.init()
    node = PointCloudSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Option B: Using sensor_msgs_py (official helper)

```python
from sensor_msgs_py import point_cloud2
import numpy as np

def callback(msg):
    # Returns a structured numpy array with named fields
    pc_array = point_cloud2.read_points_numpy(msg, field_names=('x', 'y', 'z', 'intensity'))
    xyz = pc_array[:, :3]
    intensity = pc_array[:, 3]
    # ... your model here
```

---

## What the data looks like

```
Coordinate system: ROS REP-103 (right-handed)
  x = forward (vehicle heading)
  y = left
  z = up
  units = meters

Typical frame:
  Points:     6,500 (synthetic) / 50,000–120,000 (real CARLA 64-ch)
  x range:    -50m to +50m
  y range:    -50m to +50m
  z range:    -2m to +5m (ground ~ 0, obstacles above)
  intensity:  0.0 – 1.0 (ground ≈ 0.2–0.5, obstacles ≈ 0.6–1.0)
```

---

## How to run my pipeline (so you can test your subscriber)

### Step 1: Setup (one time)

You need WSL2 Ubuntu 22.04 + ROS2 Humble (same setup I have). Then:

```bash
# Clone/copy the lidar_pointcloud package into your ROS2 workspace
mkdir -p ~/ros2_ws/src
cp -r /path/to/lidar_pointcloud ~/ros2_ws/src/
cd ~/ros2_ws && colcon build --packages-select lidar_pointcloud
source install/setup.bash
```

### Step 2: Generate test data + launch

```bash
# Generate synthetic frames
python3 ~/ros2_ws/src/lidar_pointcloud/test/generate_sample_data.py --output_dir /tmp/lidar_test --num_frames 50

# Launch publisher (keeps running)
ros2 launch lidar_pointcloud lidar_pipeline.launch.py data_dir:=/tmp/lidar_test
```

### Step 3: Run your subscriber in another terminal

```bash
source /opt/ros/humble/setup.bash
python3 vivek_subscriber.py
```

---

## What you publish back (suggested)

After segmentation, publish a **labeled** point cloud so we can visualize it:

```
Topic:   /carla/lidar/segmented
Type:    sensor_msgs/msg/PointCloud2
Fields:  x, y, z, intensity, label (uint32)
```

Where `label` maps to:
| Label | Class | Color (RViz) |
|-------|-------|-------------|
| 0 | Ground / drivable | Green |
| 1 | Static obstacle (wall, pole) | Red |
| 2 | Dynamic object (vehicle, pedestrian) | Blue |
| 3 | Unknown | Gray |

---

## Quick verification commands

```bash
# Check topic is publishing
ros2 topic list | grep lidar

# See message rate
ros2 topic hz /carla/lidar/points

# Peek at one message
ros2 topic echo /carla/lidar/points --once
```

---

## Questions for Vivek

1. Do you need **semantic labels in the input** for training? (CARLA can provide ground-truth labels via `sensor.lidar.ray_cast_semantic` — we'd add an extra field)
2. What **point count** does your model expect? Do you need downsampling/voxelization, or do you handle that?
3. Do you want the raw `LidarFrame` Python object directly (import from my package), or is the ROS2 topic enough?
