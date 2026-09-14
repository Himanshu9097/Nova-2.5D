import os
import sys
import json
import numpy as np
import time

try:
    import carla
except ImportError:
    print("Error: carla module not found. Make sure you are using the correct virtual environment.")
    sys.exit(1)

OUTPUT_DIR = "data/carla_lidar"
LIDAR_DIR = os.path.join(OUTPUT_DIR, "lidar")
META_DIR = os.path.join(OUTPUT_DIR, "metadata")
MANIFEST_PATH = os.path.join(OUTPUT_DIR, "manifest.json")

os.makedirs(LIDAR_DIR, exist_ok=True)
os.makedirs(META_DIR, exist_ok=True)

# Configuration
HOST = '127.0.0.1'
PORT = 2000
MAX_FRAMES = 100

def get_transform_dict(transform):
    return {
        "location": {"x": transform.location.x, "y": transform.location.y, "z": transform.location.z},
        "rotation": {"pitch": transform.rotation.pitch, "yaw": transform.rotation.yaw, "roll": transform.rotation.roll}
    }

def main():
    actor_list = []
    frames_collected = 0
    client = None
    
    try:
        print(f"Connecting to CARLA on {HOST}:{PORT}...")
        client = carla.Client(HOST, PORT)
        client.set_timeout(10.0)
        
        world = client.get_world()
        print(f"Connected to CARLA {client.get_server_version()}")
        print(f"Map: {world.get_map().name}")

        blueprint_library = world.get_blueprint_library()
        
        # 1. Spawn Vehicle
        vehicle_bp = blueprint_library.find('vehicle.tesla.model3')
        if not vehicle_bp:
            vehicle_bp = blueprint_library.filter('vehicle.*')[0]
            
        spawn_points = world.get_map().get_spawn_points()
        if not spawn_points:
            print("Error: No spawn points found in this map.")
            return
            
        spawn_point = spawn_points[0]
        vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)
        if not vehicle:
            print("Error: Failed to spawn vehicle.")
            return
            
        actor_list.append(vehicle)
        print(f"Vehicle spawned: {vehicle.type_id} (ID: {vehicle.id})")
        
        vehicle.set_autopilot(True)

        # 2. Attach LiDAR
        lidar_bp = blueprint_library.find('sensor.lidar.ray_cast')
        lidar_bp.set_attribute('channels', '16')
        lidar_bp.set_attribute('points_per_second', '28000')
        lidar_bp.set_attribute('rotation_frequency', '10.0')
        lidar_bp.set_attribute('range', '50.0')
        
        # Position LiDAR on top of vehicle
        lidar_transform = carla.Transform(carla.Location(x=0.0, y=0.0, z=2.4))
        lidar = world.spawn_actor(lidar_bp, lidar_transform, attach_to=vehicle)
        actor_list.append(lidar)
        print(f"LiDAR spawned: {lidar.type_id} (ID: {lidar.id})")

        print("\nReceiving LiDAR data...")

        # 3. Callback
        def lidar_callback(image):
            nonlocal frames_collected
            if frames_collected >= MAX_FRAMES:
                return

            # Extract raw data
            # CARLA ray_cast lidar data is structured as 4 float32 per point (x, y, z, intensity)
            raw_data = np.frombuffer(image.raw_data, dtype=np.float32)
            
            # Reshape to (N, 4)
            points = np.reshape(raw_data, (-1, 4))
            
            # Validate
            if points.shape[0] == 0:
                print(f"Warning: Empty frame {image.frame}")
                return
            if not np.all(np.isfinite(points)):
                print(f"Warning: Non-finite points found in frame {image.frame}")
                return
                
            frame_id = image.frame
            # Format to 6 digits
            frame_str = f"{frame_id:06d}"
            
            # Save NPY
            npy_path = os.path.join(LIDAR_DIR, f"frame_{frame_str}.npy")
            np.save(npy_path, points)
            
            # Save Metadata
            meta = {
                "frame_id": frame_id,
                "timestamp": image.timestamp,
                "sensor_id": lidar.id,
                "vehicle_id": vehicle.id,
                "point_count": points.shape[0],
                "coordinate_frame": "sensor",
                "sensor_transform": get_transform_dict(image.transform),
                "vehicle_transform": get_transform_dict(vehicle.get_transform()),
                "lidar_configuration": {
                    "channels": 16,
                    "points_per_second": 28000,
                    "rotation_frequency": 10.0,
                    "range": 50.0
                }
            }
            
            meta_path = os.path.join(META_DIR, f"frame_{frame_str}.json")
            with open(meta_path, 'w') as f:
                json.dump(meta, f, indent=2)
                
            frames_collected += 1
            print(f"Frame: {frame_id} | Points: {points.shape[0]}")

        # Start listening
        lidar.listen(lidar_callback)
        
        # Wait until frames are collected
        while frames_collected < MAX_FRAMES:
            time.sleep(0.1)
            
        print(f"\nSaved {frames_collected} frames")
        print(f"Dataset location: {os.path.abspath(OUTPUT_DIR)}")
        
        # Save manifest
        with open(MANIFEST_PATH, 'w') as f:
            json.dump({
                "total_frames": frames_collected,
                "creation_time": time.time(),
                "map": world.get_map().name
            }, f, indent=2)

    except Exception as e:
        print(f"Connection or Runtime Error: {e}")
    finally:
        print("Cleaning up actors...")
        for actor in reversed(actor_list):
            if actor.is_alive:
                actor.destroy()
        print("Cleanup successful.")

if __name__ == '__main__':
    main()
