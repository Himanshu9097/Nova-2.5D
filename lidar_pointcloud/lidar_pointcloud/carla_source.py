"""
carla_source.py — Live CARLA LiDAR data source (Phase 2).

This module will connect to a running CARLA server and subscribe to the
LiDAR sensor, converting measurements to LidarFrame objects in real-time.

STATUS: Placeholder — not implemented yet.
DEPENDS ON: carla Python client (requires Python 3.7/3.8 venv or conda env)
"""

# TODO (Phase 2): Implement live CARLA streaming
#
# Plan:
# 1. Connect to CARLA server via carla.Client(host, port)
# 2. Get/attach LiDAR sensor (sensor.lidar.ray_cast)
# 3. Register callback with sensor.listen(callback)
# 4. In callback: use carla_buffer_to_lidar_frame() from converter.py
# 5. Push LidarFrame to a thread-safe queue
# 6. Publisher node pulls from queue
#
# Note: carla Python client wants Python 3.7/3.8, but Ubuntu 22.04
# ships Python 3.10. Will need a conda env or pyenv to handle this.
# Since Phase 1 (file-based) works on system Python, this is deferred.

raise NotImplementedError(
    "carla_source.py is a Phase 2 placeholder. "
    "Use file_source.py for Phase 1 (file-based data from Yuvraj)."
)
