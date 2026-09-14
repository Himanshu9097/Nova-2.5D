# Sample Data Directory

This directory contains sample LiDAR point cloud data for testing the semantic perception module.

## Supported Formats

- `.bin` - SemanticKITTI format (float32: x, y, z, intensity)
- `.pcd` - Point Cloud Data format
- `.ply` - Polygon File Format

## Generating Sample Data

To generate synthetic sample data for testing:

```python
from src.io_utils import create_sample_point_cloud, save_point_cloud
import numpy as np

# Generate synthetic point cloud
points = create_sample_point_cloud(num_points=10000, seed=42)

# Save in different formats
save_point_cloud(points, 'data/sample/sample_synthetic.bin')
save_point_cloud(points, 'data/sample/sample_synthetic.pcd')
save_point_cloud(points, 'data/sample/sample_synthetic.ply')
```

## Manual Data Placement

If you have real LiDAR data, place your files in this directory:

```
data/sample/
├── your_lidar_data.bin
├── your_lidar_data.pcd
└── your_lidar_data.ply
```

## SemanticKITTI Dataset

For real semantic segmentation data, you can download samples from the SemanticKITTI dataset:

1. Visit: http://www.semantic-kitti.org/dataset.html
2. Download a small sample (e.g., sequence 00)
3. Extract `.bin` files to this directory

### Downloading Single Sequence

```bash
# Example: Download sequence 00
wget http://www.semantic-kitti.org/data/dataset/sequences/00/velodyne/000000.bin -P data/sample/
```

## Data Requirements

- Point clouds should have x, y, z coordinates
- Intensity values are optional (will be added if missing)
- Recommended point count: 1,000 - 100,000 points for testing
- Coordinate ranges: typically -50m to +50m for x/y, -5m to +5m for z

## Current Contents

This directory is initially empty. Run the Streamlit app to generate synthetic data automatically, or manually add your own sample files.
