from setuptools import setup
import os
from glob import glob

package_name = 'lidar_pointcloud'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        # ament index
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        # package.xml
        ('share/' + package_name, ['package.xml']),
        # launch files
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        # config files (RViz2 config, etc.)
        (os.path.join('share', package_name, 'config'), glob('config/*')),
    ],
    install_requires=['setuptools', 'numpy'],
    zip_safe=True,
    maintainer='Sahil Kumar',
    maintainer_email='sahil@todo.com',
    description='CARLA LiDAR → LidarFrame → ROS2 PointCloud2 pipeline',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pointcloud_publisher = lidar_pointcloud.pointcloud_publisher:main',
        ],
    },
)
