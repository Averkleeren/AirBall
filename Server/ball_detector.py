import numpy as np
from ultralytics import YOLO
from collections import deque
import math


class BallTracker:
    """Track basketball trajectory across frames."""
    
    def __init__(self, max_history=30, distance_threshold=50):
        """
        Initialize ball tracker.
        
        Args:
            max_history: Maximum frames to keep in trajectory history
            distance_threshold: Max pixel distance to associate ball across frames
        """
        self.model = YOLO('yolov8n.pt')
        self.trajectory = deque(maxlen=max_history)
        self.distance_threshold = distance_threshold
        self.ball_lost_frames = 0
        self.max_lost_frames = 10
    
    def detect_ball(self, frame):
        """
        Detect basketball in frame.
        
        Args:
            frame: BGR image frame
            
        Returns:
            List of detected ball positions [(x, y, radius), ...]
        """
        results = self.model(frame, conf=0.4)
        
        ball_detections = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                width = x2 - x1
                height = y2 - y1
                
                # Basketball is roughly circular
                if 0.5 < width / max(height, 1) < 2.0:
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    radius = max(width, height) // 2
                    
                    if radius > 5:
                        ball_detections.append((center_x, center_y, radius))
        
        return ball_detections
    
    def _distance(self, p1, p2):
        """Euclidean distance between two points."""
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def _associate_detection(self, current_ball):
        """Associate current detection with last known position."""
        if not self.trajectory:
            return True
        
        last_pos = self.trajectory[-1][:2]
        distance = self._distance((current_ball[0], current_ball[1]), last_pos)
        
        return distance < self.distance_threshold
    
    def update(self, frame, timestamp):
        """
        Update ball position in frame.
        
        Args:
            frame: BGR image frame
            timestamp: Frame timestamp
            
        Returns:
            Dict with trajectory info
        """
        detections = self.detect_ball(frame)
        
        best_detection = None
        if detections:
            if self.trajectory:
                last_pos = self.trajectory[-1][:2]
                best_detection = min(
                    detections,
                    key=lambda d: self._distance((d[0], d[1]), last_pos)
                )
            else:
                best_detection = detections[0]
            
            if self._associate_detection(best_detection):
                self.trajectory.append((best_detection[0], best_detection[1], best_detection[2], timestamp))
                self.ball_lost_frames = 0
                detected = True
            else:
                self.ball_lost_frames += 1
                detected = False
        else:
            self.ball_lost_frames += 1
            detected = False
        
        if self.ball_lost_frames > self.max_lost_frames:
            self.trajectory.clear()
        
        return {
            'positions': list(self.trajectory),
            'detected': detected,
            'current_pos': (best_detection[0], best_detection[1]) if best_detection else None,
            'trajectory_length': len(self.trajectory),
        }
    
    def get_trajectory(self):
        """Return current trajectory as list of (x, y, radius, ts) tuples."""
        return list(self.trajectory)
    
    def clear(self):
        """Clear trajectory history."""
        self.trajectory.clear()
        self.ball_lost_frames = 0


class ShotResultClassifier:
    """Classify if a shot was made or missed based on ball trajectory."""
    
    @staticmethod
    def analyze_trajectory(trajectory_data, frame_height, frame_width):
        """
        Analyze ball trajectory to determine shot result.
        
        Args:
            trajectory_data: List of (x, y, radius, ts) positions
            frame_height: Frame height in pixels
            frame_width: Frame width in pixels
            
        Returns:
            Dict with classification
        """
        if not trajectory_data or len(trajectory_data) < 5:
            return {
                'result': 'unknown',
                'confidence': 0.0,
                'analysis': 'Insufficient trajectory data'
            }
        
        positions = [(p[0], p[1]) for p in trajectory_data]
        
        start_pos = positions[0]
        end_pos = positions[-1]
        
        vertical_displacement = start_pos[1] - end_pos[1]
        horizontal_displacement = abs(end_pos[0] - start_pos[0])
        
        y_coords = [p[1] for p in positions]
        apex_idx = np.argmin(y_coords)
        
        has_parabolic_motion = apex_idx > 0 and apex_idx < len(y_coords) - 1
        
        final_x, final_y = end_pos
        
        hoop_x = frame_width // 2
        hoop_y = frame_height // 3
        
        distance_to_hoop = math.sqrt((final_x - hoop_x)**2 + (final_y - hoop_y)**2)
        
        made_score = 0
        confidence = 0
        
        if has_parabolic_motion:
            made_score += 3
        
        if distance_to_hoop < 80:
            made_score += 2
        
        if end_pos[1] > frame_height * 0.7 and apex_idx > len(positions) // 2:
            made_score += 2
        
        if final_x > frame_width * 0.1 and final_x < frame_width * 0.9:
            made_score += 1
        
        if len(positions) > 15:
            confidence = min(0.9, made_score / 8.0)
        elif len(positions) > 8:
            confidence = min(0.7, made_score / 8.0)
        else:
            confidence = min(0.5, made_score / 8.0)
        
        if made_score >= 5:
            result = 'made'
        elif made_score >= 3:
            result = 'made'
        elif made_score >= 1:
            result = 'unknown'
        else:
            result = 'missed'
        
        analysis = (
            f"Parabolic motion: {'yes' if has_parabolic_motion else 'no'}, "
            f"Distance to hoop: {distance_to_hoop:.0f}px, "
            f"Final Y: {final_y:.0f}px"
        )
        
        return {
            'result': result,
            'confidence': float(confidence),
            'analysis': analysis,
            'trajectory_length': len(positions),
        }
