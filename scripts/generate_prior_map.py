"""
Nova-2.5D Offline CARLA Town Static Prior Map Generator
Extracts and synthesizes the full static 2.5D elevation map for CARLA towns (e.g., Town10HD_Opt).
Supports both:
  1. Live CARLA OpenDRIVE / LiDAR survey via remote client connection
  2. Dataset synthesis from recorded CARLA LiDAR frames and map_export.json cells
Saves the compiled map to data/maps/<map_name>_prior_2.5d.npz.
"""

import os
import sys
import argparse
import json
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def parse_args():
    parser = argparse.ArgumentParser(description="Generate Nova-2.5D Static Prior Map")
    parser.add_argument('--carla-host', default=None, help='IP of CARLA server for online extraction')
    parser.add_argument('--carla-port', type=int, default=2000, help='CARLA server port')
    parser.add_argument('--output-dir', default=os.path.join(PROJECT_ROOT, 'data', 'maps'), help='Output folder')
    parser.add_argument('--map-name', default='Town10HD_Opt', help='Map name to generate')
    return parser.parse_args()

def extract_from_carla(host, port, map_name):
    """Surveys CARLA map directly via OpenDRIVE waypoints and world topology."""
    try:
        import carla
    except ImportError:
        print("[!] carla module not installed. Falling back to offline synthesis.")
        return None

    print(f"[*] Attempting online connection to CARLA at {host}:{port}...")
    try:
        client = carla.Client(host, port)
        client.set_timeout(5.0)
        world = client.get_world()
        carla_map = world.get_map()
        actual_name = carla_map.name.split('/')[-1]
        print(f"[+] Connected to CARLA! Active Map: {actual_name}")
        
        print("[*] Generating dense OpenDRIVE waypoints (0.3m spacing)...")
        waypoints = carla_map.generate_waypoints(0.3)
        print(f"[+] Extracted {len(waypoints):,} road network waypoints.")
        
        pts_xy = []
        elev_z = []
        classes = []
        
        for wp in waypoints:
            loc = wp.transform.location
            pts_xy.append([loc.x, loc.y])
            elev_z.append(loc.z)
            
            # Semantic class mapping
            lane_type = wp.lane_type
            if lane_type == carla.LaneType.Driving:
                classes.append(7) # Road
            elif lane_type == carla.LaneType.Sidewalk:
                classes.append(8) # Sidewalk
            elif lane_type == carla.LaneType.Shoulder:
                classes.append(6) # RoadLine/Shoulder
            else:
                classes.append(7)
                
        return {
            "points_xy": np.array(pts_xy, dtype=np.float32),
            "elevation_z": np.array(elev_z, dtype=np.float32),
            "classes": np.array(classes, dtype=np.uint8),
            "map_name": actual_name
        }
    except Exception as e:
        print(f"[!] Could not extract from CARLA online: {e}")
        return None

def synthesize_from_dataset(map_name):
    """Synthesizes high-resolution static prior map from recorded CARLA frames & map_export.json."""
    print(f"[*] Synthesizing static prior map from local dataset for '{map_name}'...")
    
    all_xy = []
    all_z = []
    all_cls = []
    
    # 1. Load map_export.json if available
    map_export_path = os.path.join(PROJECT_ROOT, "map_export.json")
    if os.path.exists(map_export_path):
        print(f"[*] Ingesting surveyed 2.5D cells from {map_export_path}...")
        with open(map_export_path, 'r') as f:
            data = json.load(f)
            cells = data.get('cells', [])
            for c in cells:
                all_xy.append([c['center_x'], c['center_y']])
                all_z.append(c['elevation'])
                all_cls.append(c.get('class_id', 7))
        print(f"[+] Loaded {len(cells):,} baseline cells from map_export.json")

    # 2. Ingest recorded CARLA LiDAR frames with world transformations
    lidar_dir = os.path.join(PROJECT_ROOT, "data", "carla_lidar", "lidar")
    meta_dir = os.path.join(PROJECT_ROOT, "data", "carla_lidar", "metadata")
    
    if os.path.exists(lidar_dir) and os.path.exists(meta_dir):
        bin_files = sorted([f for f in os.listdir(lidar_dir) if f.endswith('.bin')])
        print(f"[*] Processing {len(bin_files)} recorded LiDAR scans with 6-DOF ground truth transforms...")
        
        def euler_to_rot_matrix(pitch, yaw, roll):
            p, y, r = np.radians([pitch, yaw, roll])
            # CARLA coordinates: X-Forward, Y-Right, Z-Up
            Rx = np.array([[1, 0, 0], [0, np.cos(r), -np.sin(r)], [0, np.sin(r), np.cos(r)]])
            Ry = np.array([[np.cos(p), 0, np.sin(p)], [0, 1, 0], [-np.sin(p), 0, np.cos(p)]])
            Rz = np.array([[np.cos(y), -np.sin(y), 0], [np.sin(y), np.cos(y), 0], [0, 0, 1]])
            return Rz @ Ry @ Rx

        for f in bin_files[:50]: # Sample 50 scans to build comprehensive coverage
            base = os.path.splitext(f)[0]
            meta_path = os.path.join(meta_dir, f"{base}.json")
            bin_path = os.path.join(lidar_dir, f)
            
            if not os.path.exists(meta_path):
                continue
                
            with open(meta_path, 'r') as mf:
                meta = json.load(mf)
                
            sensor_tf = meta.get('sensor_transform', {})
            loc = sensor_tf.get('location', {})
            rot = sensor_tf.get('rotation', {})
            
            tx, ty, tz = loc.get('x', 0), loc.get('y', 0), loc.get('z', 0)
            R = euler_to_rot_matrix(rot.get('pitch', 0), rot.get('yaw', 0), rot.get('roll', 0))
            
            raw_pts = np.fromfile(bin_path, dtype=np.float32).reshape(-1, 4)
            # Transform local sensor coordinates to world coordinates
            local_xyz = raw_pts[:, :3]
            world_xyz = (R @ local_xyz.T).T + np.array([tx, ty, tz])
            
            # Filter ground/road points (z within realistic road terrain band)
            ground_mask = (world_xyz[:, 2] >= -5.0) & (world_xyz[:, 2] <= 5.0)
            ground_pts = world_xyz[ground_mask]
            
            # Subsample to 0.5m grid to avoid redundancy
            if len(ground_pts) > 0:
                grid_indices = np.floor(ground_pts[:, :2] / 0.5).astype(np.int32)
                _, unique_idx = np.unique(grid_indices, axis=0, return_index=True)
                sample = ground_pts[unique_idx]
                
                all_xy.extend(sample[:, :2].tolist())
                all_z.extend(sample[:, 2].tolist())
                all_cls.extend([7] * len(sample))

    if len(all_xy) == 0:
        raise RuntimeError("No survey data available to synthesize prior map!")

    xy_arr = np.array(all_xy, dtype=np.float32)
    z_arr = np.array(all_z, dtype=np.float32)
    cls_arr = np.array(all_cls, dtype=np.uint8)

    # Clean duplicates: discretize to 0.25m resolution and take median elevation per cell
    cell_keys = np.floor(xy_arr / 0.25).astype(np.int32)
    _, inv_idx = np.unique(cell_keys, axis=0, return_inverse=True)
    
    unique_cells = len(np.unique(inv_idx))
    final_xy = np.zeros((unique_cells, 2), dtype=np.float32)
    final_z = np.zeros(unique_cells, dtype=np.float32)
    final_cls = np.zeros(unique_cells, dtype=np.uint8)
    
    # Fast vectorized aggregation
    for u in range(unique_cells):
        mask = (inv_idx == u)
        final_xy[u] = np.mean(xy_arr[mask], axis=0)
        final_z[u] = np.median(z_arr[mask])
        final_cls[u] = cls_arr[mask][0]

    return {
        "points_xy": final_xy,
        "elevation_z": final_z,
        "classes": final_cls,
        "map_name": map_name
    }

def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    
    result = None
    if args.carla_host:
        result = extract_from_carla(args.carla_host, args.carla_port, args.map_name)
        
    if result is None:
        result = synthesize_from_dataset(args.map_name)

    output_file = os.path.join(args.output_dir, f"{args.map_name}_prior_2.5d.npz")
    np.savez_compressed(
        output_file,
        points_xy=result["points_xy"],
        elevation_z=result["elevation_z"],
        classes=result["classes"],
        map_name=result["map_name"]
    )
    
    print(f"\n[SUCCESS] Compiled static prior map saved to: {output_file}")
    print(f"  - Map Name     : {result['map_name']}")
    print(f"  - Total Cells  : {len(result['elevation_z']):,}")
    print(f"  - File Size    : {os.path.getsize(output_file) / 1024:.1f} KB")
    print(f"  - Spatial Span : X [{result['points_xy'][:,0].min():.1f}, {result['points_xy'][:,0].max():.1f}], "
          f"Y [{result['points_xy'][:,1].min():.1f}, {result['points_xy'][:,1].max():.1f}], "
          f"Z [{result['elevation_z'].min():.1f}, {result['elevation_z'].max():.1f}]")

if __name__ == '__main__':
    main()
