import numpy as np
from sklearn.cluster import DBSCAN

class SemanticEngine:
    def __init__(self, use_heuristic=True):
        print("Initializing Lightweight Heuristic Semantic Engine (Mocking SPVNAS)...")
        self.use_heuristic = use_heuristic

    def process_frame(self, lidar_points):
        """
        Takes raw [x, y, z, intensity] points.
        Returns semantic dictionaries for the points that matter.
        Road = 7
        Pedestrian = 4
        Vehicle = 10
        """
        # We assume the LiDAR is mounted at z=2.4 on the vehicle.
        # CARLA ground is around z=0. 
        # So points with z < 0.3 relative to ground are road.
        
        z_coords = lidar_points[:, 2]
        
        # 1. Road filtering (very simple heuristic)
        road_mask = z_coords < 0.3
        
        # 2. Obstacle filtering (everything else)
        obstacle_mask = ~road_mask
        obstacle_points = lidar_points[obstacle_mask]
        
        semantic_points = []
        
        # Assign road points
        road_indices = np.where(road_mask)[0]
        # To save bandwidth (like a real sparse CNN), we might not send ALL road points,
        # but for the C++ engine to know where the road is, we'll send a subset or all.
        for idx in road_indices[::10]: # Downsample road by 10x for performance
            semantic_points.append({
                "point_index": int(idx),
                "class_id": 7, # Road
                "confidence": 0.95
            })
            
        if len(obstacle_points) == 0:
            return semantic_points
            
        # 3. DBSCAN clustering on obstacles to separate Vehicles vs Pedestrians
        # We only cluster on X, Y to find objects
        xy_points = obstacle_points[:, :2]
        clustering = DBSCAN(eps=1.5, min_samples=5).fit(xy_points)
        
        labels = clustering.labels_
        unique_labels = set(labels)
        
        obstacle_indices = np.where(obstacle_mask)[0]
        
        for label in unique_labels:
            if label == -1:
                continue # Noise
                
            # Points belonging to this cluster
            cluster_mask = (labels == label)
            cluster_original_indices = obstacle_indices[cluster_mask]
            
            # Simple heuristic: if the cluster has many points, it's a vehicle. Few points = pedestrian.
            num_points_in_cluster = np.sum(cluster_mask)
            class_id = 10 if num_points_in_cluster > 50 else 4
            
            for idx in cluster_original_indices:
                semantic_points.append({
                    "point_index": int(idx),
                    "class_id": class_id,
                    "confidence": 0.85
                })
                
        return semantic_points
