import json
import random

# Standard CARLA Semantic Tags
CARLA_TAGS = {
    "Unlabeled": 0,
    "Building": 1,
    "Fence": 2,
    "Other": 3,
    "Pedestrian": 4,
    "Pole": 5,
    "RoadLine": 6,
    "Road": 7,
    "Sidewalk": 8,
    "Vegetation": 9,
    "Vehicles": 10,
    "Wall": 11,
    "TrafficSign": 12,
    "Sky": 13,
    "Ground": 14,
    "Bridge": 15,
    "RailTrack": 16,
    "GuardRail": 17,
    "TrafficLight": 18,
    "Static": 19,
    "Dynamic": 20,
    "Water": 21,
    "Terrain": 22
}

def generate_mock_carla_frame(frame_idx=0):
    """
    Simulates a callback from carla.Sensor.listen() for a Semantic LiDAR.
    Once CARLA is installed, you will replace this with:
    `data = np.frombuffer(carla_lidar_measurement.raw_data, dtype=np.dtype([('x', np.float32), ('y', np.float32), ('z', np.float32), ('CosAngle', np.float32), ('ObjIdx', np.uint32), ('ObjTag', np.uint32)]))`
    """
    timestamp_ns = 1000000000 + (frame_idx * 100000000) # 100ms dt
    
    semantics = []
    points = []
    
    # 1. Generate Road Points (Tag 7)
    for i in range(100):
        points.append([float(i % 10) * 2.0, float(i // 10) * 2.0, 0.0])
        semantics.append({
            "point_index": i,
            "class_id": CARLA_TAGS["Road"],
            "confidence": 1.0 # CARLA ground truth is always 100% confident
        })
        
    # 2. Generate Pedestrian Point (Tag 4) moving along x
    ped_idx = 100
    simulated_x = 20.0 + (frame_idx * 1.5)
    points.append([simulated_x, 2.0, 1.0])
    semantics.append({
        "point_index": ped_idx,
        "class_id": CARLA_TAGS["Pedestrian"],
        "confidence": 1.0
    })
    
    # 3. Generate Vehicle Point (Tag 10)
    veh_idx = 101
    points.append([10.0, -2.0, 0.5])
    semantics.append({
        "point_index": veh_idx,
        "class_id": CARLA_TAGS["Vehicles"],
        "confidence": 1.0
    })

    # Ground-truth Tracking (Extracting Actor bounding boxes from carla.World)
    tracks = []
    tracks.append({
        "track_id": 999, # CARLA actor.id
        "class_id": CARLA_TAGS["Pedestrian"],
        "confidence": 1.0,
        "x": simulated_x,
        "y": 2.0,
        "z": 1.0,
        "vx": 15.0, # 1.5m / 100ms
        "vy": 0.0,
        "vz": 0.0,
        "length": 0.5,
        "width": 0.5,
        "height": 1.8,
        "yaw": 0.0,
        "dynamic_probability": 1.0, # Ground truth knows it's moving
        "first_seen_ns": 1000000000,
        "last_update_ns": timestamp_ns,
        "state": 1 # CONFIRMED
    })

    # Export exactly like the C++ Engine expects
    output_data = {
        "frame_id": frame_idx,
        "timestamp_ns": timestamp_ns,
        "points": points,
        "semantics": semantics,
        "tracks": tracks
    }
    
    output_path = f"carla_frame_{frame_idx:04d}.json"
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
        
    print(f"Exported CARLA ground-truth simulation to {output_path}")

if __name__ == "__main__":
    print("Running Nova-CARLA Bridge Simulation...")
    generate_mock_carla_frame(0)
    generate_mock_carla_frame(1)
    generate_mock_carla_frame(2)
