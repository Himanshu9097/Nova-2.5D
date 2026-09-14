import os
import sys
import json
import numpy as np
import time
import requests
import subprocess
import glob

# Ensure we can import the perception modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from perception.semantic.semantic_engine import SemanticEngine
from perception.tracking.tracking_engine import TrackingEngine

DATA_DIR = "data/carla_lidar"
LIDAR_DIR = os.path.join(DATA_DIR, "lidar")
META_DIR = os.path.join(DATA_DIR, "metadata")
CPP_ENGINE = r"build\Debug\simulation_runner.exe"

def run_pipeline():
    print("🚀 Starting Nova-2.5D End-to-End Pipeline...")
    
    # 1. Initialize Python Modules
    semantic_engine = SemanticEngine(use_heuristic=True)
    tracking_engine = TrackingEngine()
    
    # 2. Find dataset frames
    lidar_files = sorted(glob.glob(os.path.join(LIDAR_DIR, "*.npy")))
    if not lidar_files:
        print("Error: No LiDAR data found in", LIDAR_DIR)
        return
        
    print(f"Found {len(lidar_files)} frames. Beginning streaming...")
    
    for idx, lidar_file in enumerate(lidar_files):
        try:
            filename = os.path.basename(lidar_file)
            frame_id_str = filename.split('_')[1].split('.')[0]
            
            # Load Data
            points = np.load(lidar_file)
            
            # Extract timestamp from metadata (mocking timestamp for now based on loop)
            timestamp_ns = int(time.time() * 1e9)
            
            # --- PHASE 1: VIVEK (SEMANTIC) ---
            semantic_start = time.time()
            semantic_points = semantic_engine.process_frame(points)
            
            # --- PHASE 2: KASHIKA (TRACKING) ---
            tracking_start = time.time()
            tracks = tracking_engine.process_frame(semantic_points, points, timestamp_ns, idx)
            
            # --- DATA PREP FOR C++ ---
            # Create the JSON payload
            frame_data = {
                "frame_id": int(frame_id_str),
                "timestamp_ns": timestamp_ns,
                "ego_transform": {
                    "location": {"x": 0, "y": 0, "z": 0},
                    "rotation": {"pitch": 0, "yaw": 0, "roll": 0}
                },
                "num_points": len(points),
                "points": [], # We omit raw points from JSON to save I/O overhead for demo
                "semantic_points": semantic_points,
                "tracks": tracks
            }
            
            json_path = f"carla_frame_{frame_id_str}.json"
            with open(json_path, 'w') as f:
                json.dump(frame_data, f)
                
            # --- PHASE 3: ADITYA (C++ MAPPING ENGINE) ---
            cpp_start = time.time()
            # Run the C++ engine
            result = subprocess.run([CPP_ENGINE, json_path], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"C++ Engine Error on frame {frame_id_str}:\n{result.stderr}")
                continue
                
            # --- PHASE 4: RIDDHIMA (DASHBOARD) ---
            # Parse memory stats from C++ output
            # C++ output contains: 
            # Active Cells: X
            # Map memory bytes: Y
            active_cells = 0
            map_memory_bytes = 0
            
            for line in result.stdout.split('\n'):
                if "Active Cells:" in line:
                    active_cells = int(line.split(":")[-1].strip())
                elif "Map memory bytes:" in line:
                    map_memory_bytes = int(line.split(":")[-1].strip())
                    
            raw_memory_bytes = len(points) * 16 # x,y,z,intensity = 16 bytes
            
            # POST to dashboard
            dashboard_payload = {
                "frame": idx,
                "points": len(points),
                "cells": active_cells,
                "raw_memory_kb": raw_memory_bytes / 1024.0,
                "nova_memory_kb": map_memory_bytes / 1024.0
            }
            
            try:
                requests.post("http://127.0.0.1:5000/update", json=dashboard_payload, timeout=1)
            except requests.exceptions.RequestException:
                pass # Dashboard might not be running
                
            # Print status
            reduction = 100 * (1 - (map_memory_bytes / raw_memory_bytes)) if raw_memory_bytes > 0 else 0
            print(f"Frame {idx:04d} | Points: {len(points)} -> Cells: {active_cells} | Memory Reduction: {reduction:.1f}%")
            
            # Cleanup JSON
            try:
                os.remove(json_path)
            except:
                pass
                
            time.sleep(0.1) # Pace the demo
            
        except Exception as e:
            print(f"Error processing {lidar_file}: {e}")

if __name__ == "__main__":
    run_pipeline()
