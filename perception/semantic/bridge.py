import json
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../tracking'))

from semantic_engine import SemanticEngine
from tracking_engine import TrackingEngine

def run_bridge(lidar_npy_path, output_json_path, frame_idx=0):
    print(f"Loading LiDAR frame from {lidar_npy_path}...")
    lidar_points = np.random.rand(1000, 4) # dummy data for now
    timestamp_ns = 1000000000 + (frame_idx * 100000000) # 100ms dt
    
    # 1. Semantic Inference
    sem_engine = SemanticEngine()
    semantic_points = sem_engine.process_frame(lidar_points)
    
    # 2. Tracking Inference
    trk_engine = TrackingEngine()
    tracks = trk_engine.process_frame(lidar_points, timestamp_ns, frame_idx)
    
    # Format the data exactly as the C++ AdaptiveGridEngine expects
    output_data = {
        "frame_id": 101 + frame_idx,
        "timestamp_ns": timestamp_ns,
        "points": [],
        "semantics": semantic_points,
        "tracks": tracks
    }
    
    # Normally we would save points too, but C++ handles LiDAR natively
    
    with open(output_json_path, 'w') as f:
        json.dump(output_data, f, indent=2)
        
    print(f"Exported {len(semantic_points)} semantic points and {len(tracks)} tracks to {output_json_path}")

if __name__ == "__main__":
    # Simulate processing two consecutive frames to demonstrate tracking/velocity
    run_bridge("frame_0001.npy", "output_0001.json", frame_idx=0)
    run_bridge("frame_0002.npy", "output_0002.json", frame_idx=1)
