import os
import numpy as np


class LidarRecorder:

    def __init__(self, output_dir="data/raw"):
        self.output_dir = output_dir

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

        filename = os.path.join(
            self.output_dir,
            f"{point_cloud.frame:06d}.bin"
        )

        points.tofile(filename)

        self.frame_count += 1

        print(
            f"[LiDAR] Frame: "
            f"{point_cloud.frame} | "
            f"Points: {len(points)}"
        )