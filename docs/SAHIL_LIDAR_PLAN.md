# Sahil — LiDAR Point-Cloud Ingestion & ROS2 Pipeline

> **SIH Problem:** DRDO/IDEX — Foveated 2.5D Elevation Map from LiDAR  
> **My deliverable:** CARLA LiDAR → `LidarFrame` → ROS2 `PointCloud2` → RViz2 (raw points)  
> **Status:** Environment setup in progress · Waiting on data from Yuvraj

---

## Where I sit in the pipeline

```
Yuvraj (CARLA + LiDAR sensor)  →  ME (Sahil)  →  Vivek (Semantic AI / PointNet++)
                                     │
        raw CARLA buffer ──► LidarFrame ──► ROS2 PointCloud2 ──► RViz2 (raw points)
                                                                      │
                                                     Riddhima (benchmarks: FPS, latency, memory)
                                                                      │
                                                     Variable-Resolution 2.5D Grid Engine
```

My output (`PointCloud2` on `/carla/lidar/points`) is the **single data source** for:
- Vivek's semantic segmentation (PointNet++ / Sparse CNN)
- The variable-resolution grid engine (5cm→50cm cells)
- Riddhima's performance benchmarks (FPS, latency)
- The real-time visualization dashboard

---

## Environment: WSL2 + Ubuntu 22.04 + ROS2 Humble

### Why this stack

| Option | Verdict |
|--------|---------|
| Native Windows ROS2 | ❌ RViz2/rclpy fragile, constant fights |
| WSL2 + Ubuntu 22.04 | ✅ `apt install ros-humble-desktop`, RViz2 GUI via WSLg (Win11 built-in) |
| Dual-boot Ubuntu | Overkill — I don't run CARLA locally |
| Docker | Unnecessary overhead for a consumer-only node |

### Setup commands (Step 0 — independent of data)

```bash
# 1. Install WSL2 Ubuntu 22.04
wsl --install -d Ubuntu-22.04

# 2. Inside Ubuntu — ROS2 Humble desktop (includes RViz2)
sudo apt update && sudo apt install -y ros-humble-desktop python3-colcon-common-extensions
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc && source ~/.bashrc

# 3. Point-cloud dependencies
sudo apt install -y python3-numpy python3-pip
pip install open3d

# 4. Verify RViz2 GUI works (proves WSLg is functional)
rviz2
```

---

## Step 1 — Data contract with Yuvraj ⭐

> See `docs/DATA_FORMAT_FOR_YUVRAJ.md` for the copy-pasteable spec to hand Yuvraj.

**Summary:** Each LiDAR sweep = one `.npy` file `(N,4) float32` `[x, y, z, intensity]` + one `.json` sidecar with metadata. Raw CARLA coordinates (left-handed). I handle the coordinate conversion.

### Coordinate convention gotcha

| Axis | CARLA (left-handed) | ROS REP-103 (right-handed) |
|------|---------------------|---------------------------|
| X | Forward | Forward |
| Y | **Right** | **Left** |
| Z | Up | Up |
| Fix | — | `y_ros = -y_carla` |

**Decision:** Yuvraj sends raw CARLA coords → I convert. The fix lives in my module.

---

## Step 2 — `LidarFrame` dataclass (core abstraction)

```python
from dataclasses import dataclass, field
import numpy as np

@dataclass
class LidarFrame:
    """Single LiDAR sweep in ROS coordinate convention."""
    frame_id: int                             # sequential frame number
    timestamp: float                          # seconds (epoch or sim-time)
    points: np.ndarray                        # (N, 3) float32 — xyz in ROS coords (meters)
    intensity: np.ndarray                     # (N,) float32 — per-point intensity
    sensor_pose: np.ndarray                   # (4, 4) float64 — sensor-to-world transform
    frame_ref: str = "lidar_link"             # ROS TF frame ID
    num_channels: int = 0                     # CARLA lidar channel count (metadata)
```

This is the object the rest of the team's pipeline hangs off of. Vivek consumes it for segmentation; the grid engine projects from it.

---

## Step 3 — Converter (raw CARLA → LidarFrame)

Fully vectorized with numpy — no per-point Python loops (critical for Riddhima's FPS benchmarks):

```python
def carla_to_lidar_frame(buffer: bytes, frame_id: int, timestamp: float,
                         sensor_pose: np.ndarray) -> LidarFrame:
    raw = np.frombuffer(buffer, dtype=np.float32).reshape(-1, 4)
    xyz = raw[:, :3].copy()
    xyz[:, 1] *= -1.0  # CARLA left-handed → ROS right-handed y-flip
    return LidarFrame(
        frame_id=frame_id,
        timestamp=timestamp,
        points=xyz,
        intensity=raw[:, 3],
        sensor_pose=sensor_pose,
    )
```

For file-based input (`.npy` from Yuvraj):

```python
def npy_to_lidar_frame(npy_path: str, meta_path: str) -> LidarFrame:
    raw = np.load(npy_path)            # (N, 4) float32
    meta = json.load(open(meta_path))
    xyz = raw[:, :3].copy()
    xyz[:, 1] *= -1.0
    return LidarFrame(
        frame_id=meta["frame_id"],
        timestamp=meta["timestamp"],
        points=xyz,
        intensity=raw[:, 3],
        sensor_pose=np.array(meta["sensor_transform"]),
        num_channels=meta.get("channels", 0),
    )
```

---

## Step 4 — ROS2 Publisher Node

An `rclpy` node publishing `sensor_msgs/PointCloud2` on `/carla/lidar/points`:

- Uses `sensor_msgs_py.point_cloud2.create_cloud()` with XYZI fields
- `header.frame_id = "lidar_link"`
- `header.stamp` from `LidarFrame.timestamp`
- Companion `static_transform_publisher` for the TF tree so RViz resolves the frame

---

## Step 5 — RViz2 Visualization

- Add **PointCloud2** display → topic `/carla/lidar/points`
- Fixed Frame = `lidar_link`
- Color by `intensity` (or `z` for height-based coloring)
- Save config as `config/lidar.rviz` → whole team uses same view
- **Screenshot of raw points = my first visible deliverable**

---

## Module layout (ROS2 `ament_python` package)

```
lidar_pointcloud/
├── package.xml
├── setup.py
├── setup.cfg
├── resource/lidar_pointcloud          # ament index marker
├── lidar_pointcloud/
│   ├── __init__.py
│   ├── lidar_frame.py                 # LidarFrame dataclass
│   ├── converter.py                   # raw CARLA → LidarFrame (coord fix)
│   ├── file_source.py                 # reads .npy/.json from Yuvraj's exports
│   ├── carla_source.py                # live CARLA stream (Phase 2)
│   └── pointcloud_publisher.py        # rclpy node: LidarFrame → PointCloud2
├── config/
│   └── lidar.rviz                     # saved RViz2 config
├── launch/
│   └── lidar_pipeline.launch.py       # launches publisher + static TF
├── test/
│   ├── test_converter.py              # unit-test converter on sample frame
│   └── sample_data/                   # one .npy + .json for testing
└── docs/                              # → symlink or copy from top-level docs/
```

---

## Milestones

| # | Milestone | Depends on | Status |
|---|-----------|-----------|--------|
| 1 | WSL2 + ROS2 Humble + RViz2 working | Nothing | ✅ Done (2026-09-08) |
| 2 | Lock data contract with Yuvraj | Yuvraj's agreement | ⏳ Pending — send him `DATA_FORMAT_FOR_YUVRAJ.md` |
| 3 | `LidarFrame` + converter + unit test | Sample `.npy` from Yuvraj | ✅ Done — 9/9 tests pass, synthetic data works |
| 4 | Publisher node → `PointCloud2` on ROS2 topic | Milestone 3 | ✅ Done — publishing at 10 Hz, 6500 pts/frame |
| 5 | **RViz2 shows raw points** (first visible win) | Milestone 4 | ✅ Done — 31 FPS, synthetic ground + obstacles visible |
| 6 | Live-stream mode via `carla` client | Phase 2, needs CARLA bridge | ⏳ Future |
| 7 | Document topic/LidarFrame interface for Vivek | Milestone 5 | ⏳ Future |

---

## Gotchas

1. **`carla-ros-bridge` exists** — don't use it as a black box. Building the custom converter *is* the deliverable and gives us the `LidarFrame` abstraction. Use the bridge as a sanity-check reference only.

2. **Performance is non-negotiable** — keep everything vectorized (numpy structured arrays for PointCloud2 serialization). Python per-point loops will tank the FPS that Riddhima measures. The problem statement explicitly requires "low latency (high FPS)".

3. **CARLA Python client version mismatch** — CARLA's client wants Python 3.7/3.8, Ubuntu 22.04 ships 3.10. Since I consume *files/rosbag* (not live CARLA), this doesn't affect me. Phase 2 live-stream will need a venv or conda to handle this.

4. **Point density** — CARLA LiDAR can generate 100k+ points per sweep at high settings. The converter and publisher must handle this at 10–20 Hz without dropping frames.
