import os
import json
import numpy as np
import glob

def validate_dataset():
    OUTPUT_DIR = "data/carla_lidar"
    LIDAR_DIR = os.path.join(OUTPUT_DIR, "lidar")
    META_DIR = os.path.join(OUTPUT_DIR, "metadata")
    
    npy_files = sorted(glob.glob(os.path.join(LIDAR_DIR, "*.npy")))
    json_files = sorted(glob.glob(os.path.join(META_DIR, "*.json")))
    
    if not npy_files:
        print("Error: No .npy files found in dataset.")
        return
        
    if len(npy_files) != len(json_files):
        print(f"Warning: Number of .npy files ({len(npy_files)}) does not match .json files ({len(json_files)})")
        
    total_frames = len(npy_files)
    total_points = 0
    min_points = float('inf')
    max_points = 0
    
    nan_count = 0
    inf_count = 0
    
    timestamps = []
    frame_ids = []
    
    sample_shape = None
    sample_dtype = None
    
    print(f"Validating {total_frames} frames...")
    
    for npy_path, json_path in zip(npy_files, json_files):
        # Load NPY
        points = np.load(npy_path)
        
        num_points = points.shape[0]
        total_points += num_points
        min_points = min(min_points, num_points)
        max_points = max(max_points, num_points)
        
        nan_count += np.isnan(points).sum()
        inf_count += np.isinf(points).sum()
        
        if sample_shape is None:
            sample_shape = f"(N, {points.shape[1]})"
            sample_dtype = str(points.dtype)
            
        # Load JSON
        with open(json_path, 'r') as f:
            meta = json.load(f)
            
        timestamps.append(meta["timestamp"])
        frame_ids.append(meta["frame_id"])
        
    avg_points = total_points / total_frames if total_frames > 0 else 0
    
    print("\n==================================================")
    print("DATASET VALIDATION RESULTS")
    print("==================================================")
    print(f"Number of frames:       {total_frames}")
    print(f"Total points:           {total_points}")
    print(f"Minimum point count:    {min_points}")
    print(f"Maximum point count:    {max_points}")
    print(f"Average point count:    {avg_points:.1f}")
    print(f"Point-cloud shape:      {sample_shape}")
    print(f"Data type:              {sample_dtype}")
    print(f"NaN count:              {nan_count}")
    print(f"Infinity count:         {inf_count}")
    
    if timestamps:
        print(f"Timestamp range:        {min(timestamps):.4f} -> {max(timestamps):.4f} (Duration: {max(timestamps)-min(timestamps):.4f}s)")
        print(f"Frame ID range:         {min(frame_ids)} -> {max(frame_ids)}")
        
    print("==================================================")
    
if __name__ == '__main__':
    validate_dataset()
