"""
Launch file for the LiDAR point-cloud pipeline.

Launches:
  1. pointcloud_publisher — reads frames and publishes PointCloud2
  2. static_transform_publisher — provides the lidar_link TF frame for RViz2

Usage:
  ros2 launch lidar_pointcloud lidar_pipeline.launch.py data_dir:=/path/to/lidar_export
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        # --- Arguments ---
        DeclareLaunchArgument(
            'data_dir',
            description='Path to directory containing frame_NNNN.npy/json pairs'
        ),
        DeclareLaunchArgument(
            'rate_hz',
            default_value='10.0',
            description='Playback rate in Hz'
        ),
        DeclareLaunchArgument(
            'loop',
            default_value='true',
            description='Loop playback when all frames are consumed'
        ),

        # --- PointCloud2 Publisher ---
        Node(
            package='lidar_pointcloud',
            executable='pointcloud_publisher',
            name='pointcloud_publisher',
            output='screen',
            parameters=[{
                'data_dir': LaunchConfiguration('data_dir'),
                'rate_hz': LaunchConfiguration('rate_hz'),
                'loop': LaunchConfiguration('loop'),
                'topic': '/carla/lidar/points',
                'frame_id': 'lidar_link',
            }],
        ),

        # --- Static TF: map → lidar_link ---
        # Provides the TF frame so RViz2 can resolve lidar_link.
        # Identity transform (sensor at origin) — update if Yuvraj provides
        # a fixed mounting position relative to the vehicle.
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='lidar_tf',
            arguments=[
                '--x', '0.0',
                '--y', '0.0',
                '--z', '2.5',   # typical roof-mount height
                '--roll', '0.0',
                '--pitch', '0.0',
                '--yaw', '0.0',
                '--frame-id', 'map',
                '--child-frame-id', 'lidar_link',
            ],
        ),
    ])
