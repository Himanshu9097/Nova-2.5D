import numpy as np
import time

class TrackState:
    TENTATIVE = 0
    CONFIRMED = 1
    LOST = 2

class Track:
    def __init__(self, track_id, detection, timestamp):
        self.track_id = track_id
        self.class_id = detection['class_id']
        self.confidence = detection['confidence']
        
        # State: x, y, z, vx, vy, vz
        self.state = np.array([detection['x'], detection['y'], detection['z'], 0.0, 0.0, 0.0])
        
        self.length = detection['length']
        self.width = detection['width']
        self.height = detection['height']
        self.yaw = detection['yaw']
        
        self.state_status = TrackState.TENTATIVE
        self.hits = 1
        self.time_since_update = 0
        self.first_seen_ns = timestamp
        self.last_update_ns = timestamp

    def predict(self, dt):
        """ Basic constant velocity prediction """
        self.state[0] += self.state[3] * dt
        self.state[1] += self.state[4] * dt
        self.state[2] += self.state[5] * dt
        self.time_since_update += 1

    def update(self, detection, timestamp, dt):
        """ Basic update """
        if dt > 0:
            # Simple velocity estimation (dx/dt)
            self.state[3] = (detection['x'] - self.state[0]) / dt
            self.state[4] = (detection['y'] - self.state[1]) / dt
            self.state[5] = (detection['z'] - self.state[2]) / dt
            
        self.state[0] = detection['x']
        self.state[1] = detection['y']
        self.state[2] = detection['z']
        
        self.hits += 1
        self.time_since_update = 0
        self.last_update_ns = timestamp
        
        if self.hits >= 3:
            self.state_status = TrackState.CONFIRMED

    def get_dynamic_probability(self):
        speed = np.sqrt(self.state[3]**2 + self.state[4]**2)
        if speed > 0.5:
            return 0.95
        return 0.1

class KalmanTracker:
    def __init__(self):
        self.tracks = []
        self.next_id = 1
        self.last_timestamp = 0

    def update(self, detections, timestamp_ns):
        dt = (timestamp_ns - self.last_timestamp) * 1e-9 if self.last_timestamp > 0 else 0.1
        self.last_timestamp = timestamp_ns
        
        # Predict
        for track in self.tracks:
            track.predict(dt)
            
        # Match (mock matching by distance)
        unmatched_detections = []
        for det in detections:
            matched = False
            for track in self.tracks:
                dist = np.sqrt((track.state[0] - det['x'])**2 + (track.state[1] - det['y'])**2)
                if dist < 2.0: # 2m threshold
                    track.update(det, timestamp_ns, dt)
                    matched = True
                    break
            if not matched:
                unmatched_detections.append(det)
                
        # Create new tracks
        for det in unmatched_detections:
            self.tracks.append(Track(self.next_id, det, timestamp_ns))
            self.next_id += 1
            
        # Cleanup lost tracks
        self.tracks = [t for t in self.tracks if t.time_since_update < 5]
        
        return self.tracks
