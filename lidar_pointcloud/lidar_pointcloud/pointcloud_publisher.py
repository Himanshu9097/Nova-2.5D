"""
pointcloud_publisher.py — ROS2 node that publishes LidarFrames as PointCloud2 messages.

This is the main entry point for the pipeline:
  File source (Yuvraj's exports) → LidarFrame → PointCloud2 → /carla/lidar/points

Usage (after colcon build + source install/setup.bash):
  ros2 run lidar_pointcloud pointcloud_publisher --ros-args -p data_dir:=/path/to/lidar_export

Or via launch file:
  ros2 launch lidar_pointcloud lidar_pipeline.launch.py data_dir:=/path/to/lidar_export
"""

import struct
import numpy as np

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header
from builtin_interfaces.msg import Time

from .file_source import FileSource
from .lidar_frame import LidarFrame


class PointCloudPublisher(Node):
    """ROS2 node that reads LidarFrames and publishes PointCloud2 messages."""

    def __init__(self):
        super().__init__('pointcloud_publisher')

        # Parameters
        self.declare_parameter('data_dir', '')
        self.declare_parameter('rate_hz', 10.0)
        self.declare_parameter('loop', True)
        self.declare_parameter('topic', '/carla/lidar/points')
        self.declare_parameter('frame_id', 'lidar_link')

        data_dir = self.get_parameter('data_dir').get_parameter_value().string_value
        rate_hz = self.get_parameter('rate_hz').get_parameter_value().double_value
        loop = self.get_parameter('loop').get_parameter_value().bool_value
        topic = self.get_parameter('topic').get_parameter_value().string_value
        frame_id = self.get_parameter('frame_id').get_parameter_value().string_value

        if not data_dir:
            self.get_logger().error(
                'data_dir parameter is required. '
                'Use: --ros-args -p data_dir:=/path/to/lidar_export'
            )
            raise SystemExit(1)

        # Publisher
        self.publisher_ = self.create_publisher(PointCloud2, topic, 10)
        self.get_logger().info(f'Publishing PointCloud2 on {topic}')
        self.get_logger().info(f'Frame ID: {frame_id}')

        # Data source
        self.source = FileSource(data_dir)
        self.frame_id = frame_id
        self.get_logger().info(f'Loaded {self.source.num_frames} frames from {data_dir}')

        # Playback via timer
        self.frame_iter = iter(self.source.play(rate_hz=rate_hz, loop=loop))
        timer_period = 1.0 / rate_hz
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self._pub_count = 0

    def timer_callback(self):
        """Publish the next LidarFrame as a PointCloud2 message."""
        try:
            frame = next(self.frame_iter)
        except StopIteration:
            self.get_logger().info('All frames published. Shutting down.')
            self.timer.cancel()
            return

        msg = self.lidar_frame_to_pointcloud2(frame)
        self.publisher_.publish(msg)

        self._pub_count += 1
        if self._pub_count % 50 == 0:
            self.get_logger().info(
                f'Published frame {frame.frame_id} '
                f'({frame.num_points} pts) '
                f'[total: {self._pub_count}]'
            )

    def lidar_frame_to_pointcloud2(self, frame: LidarFrame) -> PointCloud2:
        """Convert a LidarFrame to a sensor_msgs/PointCloud2 message.

        Uses a structured numpy array for efficient serialization — no per-point loops.
        """
        msg = PointCloud2()

        # Header
        msg.header = Header()
        msg.header.frame_id = self.frame_id
        sec = int(frame.timestamp)
        nanosec = int((frame.timestamp - sec) * 1e9)
        msg.header.stamp = Time(sec=sec, nanosec=nanosec)

        # Fields: x, y, z, intensity (all float32)
        msg.fields = [
            PointField(name='x', offset=0,  datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4,  datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8,  datatype=PointField.FLOAT32, count=1),
            PointField(name='intensity', offset=12, datatype=PointField.FLOAT32, count=1),
        ]

        # Layout
        point_step = 16  # 4 floats × 4 bytes
        n_points = frame.num_points
        msg.point_step = point_step
        msg.row_step = point_step * n_points
        msg.height = 1
        msg.width = n_points
        msg.is_bigendian = False
        msg.is_dense = True  # no NaN/Inf expected from CARLA

        # Data: pack as contiguous float32 XYZI array
        xyzi = frame.as_xyzi()  # (N, 4) float32
        msg.data = xyzi.tobytes()

        return msg


def main(args=None):
    """Entry point for the pointcloud_publisher node."""
    rclpy.init(args=args)
    node = PointCloudPublisher()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
