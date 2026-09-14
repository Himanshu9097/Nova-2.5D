import numpy as np

class CenterPointDetector:
    """
    Mock implementation of a 3D object detector (like CenterPoint or PointPillars).
    """
    def __init__(self, confidence_threshold=0.5):
        self.confidence_threshold = confidence_threshold

    def detect(self, lidar_points, frame_idx=0):
        """
        Inputs: lidar_points (N, 4)
        Returns: list of dicts representing 3D bounding boxes.
        """
        # For demonstration, we'll return a simulated moving pedestrian.
        # It starts at x=60, y=2 and moves along the x-axis.
        
        simulated_x = 60.0 + (frame_idx * 1.5) # moving 1.5m per frame
        
        detections = []
        detections.append({
            "class_id": 10, # Pedestrian
            "confidence": 0.95,
            "x": simulated_x,
            "y": 2.0,
            "z": 1.0,
            "length": 0.5,
            "width": 0.5,
            "height": 1.8,
            "yaw": 0.0
        })
        
        return detections
