import numpy as np
from .kalman_tracker import KalmanTracker

class TrackingEngine:
    def __init__(self):
        print("Initializing Lightweight Dynamic Tracking Engine...")
        self.tracker = KalmanTracker()

    def process_frame(self, semantic_points, raw_points, timestamp_ns, frame_idx=0):
        # We need to group the semantic_points into "detections" (bounding boxes) for the tracker.
        
        # 1. Group points by class_id and compute centroids
        # In our heuristic semantic engine, all points were assigned 7, 4, or 10.
        # But wait, the semantic_points output from heuristic are just lists of points.
        # Since we ran DBSCAN in semantic_engine, it would be much better if semantic_engine gave us 
        # the cluster ID, but it doesn't. 
        # For this demo, let's just do a quick re-cluster or assume one large centroid.
        # ACTUALLY: Let's extract only Pedestrians (4) and Vehicles (10) and cluster them again quickly.
        
        detections = []
        
        vehicles = [p for p in semantic_points if p['class_id'] == 10]
        pedestrians = [p for p in semantic_points if p['class_id'] == 4]
        
        def create_detection(points_list, cls_id):
            if not points_list:
                return []
            
            # Extract actual coordinates
            coords = []
            for p in points_list:
                idx = p['point_index']
                coords.append(raw_points[idx][:3])
            
            coords = np.array(coords)
            
            # Extremely simple mock: just take the mean of all points of that class as one object
            # In a real pipeline, we'd use the DBSCAN labels directly.
            centroid = np.mean(coords, axis=0)
            
            return [{
                'class_id': cls_id,
                'confidence': 0.9,
                'x': centroid[0],
                'y': centroid[1],
                'z': centroid[2],
                'length': 4.0 if cls_id == 10 else 0.5,
                'width': 2.0 if cls_id == 10 else 0.5,
                'height': 1.5 if cls_id == 10 else 1.8,
                'yaw': 0.0
            }]
            
        detections.extend(create_detection(vehicles, 10))
        detections.extend(create_detection(pedestrians, 4))
        
        # 2. Track
        tracks = self.tracker.update(detections, timestamp_ns)
        
        # 3. Format output
        output_tracks = []
        for t in tracks:
            output_tracks.append({
                "track_id": int(t.track_id),
                "class_id": int(t.class_id),
                "confidence": float(t.confidence),
                "x": float(t.state[0]),
                "y": float(t.state[1]),
                "z": float(t.state[2]),
                "vx": float(t.state[3]),
                "vy": float(t.state[4]),
                "vz": float(t.state[5]),
                "length": float(t.length),
                "width": float(t.width),
                "height": float(t.height),
                "yaw": float(t.yaw),
                "dynamic_probability": float(t.get_dynamic_probability()),
                "first_seen_ns": float(t.first_seen_ns),
                "last_update_ns": float(t.last_update_ns),
                "state": int(t.state_status)
            })
            
        return output_tracks
