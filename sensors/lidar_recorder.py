import os
import json
import numpy as np


class LidarRecorder:

    def __init__(self, output_dir="data/lidar_export", metadata=None):
        self.output_dir = output_dir
        self.metadata = metadata or {}

        os.makedirs(
            self.output_dir,
            exist_ok=True
        )

        self.frame_count = 0

    def callback(self, point_cloud):

        points = np.frombuffer(
            point_cloud.raw_data,
            dtype=np.float32
        )

        points = np.reshape(
            points,
            (-1, 4)
        )

        frame_id = point_cloud.frame
        filename = os.path.join(
            self.output_dir,
            f"frame_{frame_id:04d}.npy"
        )

        np.save(filename, points)

        metadata = {
            "frame_id": frame_id,
            "timestamp": float(point_cloud.timestamp),
            "sensor_transform": point_cloud.transform.get_matrix(),
            **self.metadata,
        }
        metadata_filename = os.path.join(
            self.output_dir,
            f"frame_{frame_id:04d}.json"
        )
        with open(metadata_filename, "w", encoding="utf-8") as metadata_file:
            json.dump(metadata, metadata_file, indent=2)

        self.frame_count += 1

        print(
            f"[LiDAR] Frame: "
            f"{point_cloud.frame} | "
            f"Points: {len(points)}"
        )