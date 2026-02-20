import cv2
import mediapipe as mp
import time
from pathlib import Path
import json

from shot_detector import ShotDetector
from ball_detector import BallTracker, ShotResultClassifier
from ultralytics import YOLO


class VideoProcessor:
    """Process uploaded basketball videos to detect shots and ball trajectory."""
    
    def __init__(self):
        self.person_detector = YOLO('yolov8n.pt')
        self.mp_pose = mp.solutions.pose
        self.pose_detector = self.mp_pose.Pose(
            static_image_mode=True, 
            min_detection_confidence=0.3, 
            model_complexity=0
        )
        self.shot_detector = ShotDetector()
        self.ball_tracker = BallTracker()
    
    def process_video(self, video_path, output_dir='shots'):
        """
        Process video file to detect shots and track balls.
        
        Args:
            video_path: Path to video file
            output_dir: Directory to save shot data
            
        Returns:
            Dictionary with processing results
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        frame_count = 0
        detected_shots = []
        
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            timestamp = start_time + (frame_count / fps)
            
            # Resize for processing speed
            scale = 0.25
            small_frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
            small_h, small_w = small_frame.shape[:2]
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Person detection
            results = self.person_detector(rgb_small_frame, conf=0.3, classes=[0])
            
            people_landmarks = []
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    person_crop = rgb_small_frame[y1:y2, x1:x2]
                    if person_crop.size == 0:
                        continue
                    
                    pose_results = self.pose_detector.process(person_crop)
                    if pose_results.pose_landmarks:
                        crop_h, crop_w = person_crop.shape[:2]
                        landmarks = pose_results.pose_landmarks.landmark
                        
                        for lm in landmarks:
                            lm.x = (x1 + lm.x * crop_w) / small_w
                            lm.y = (y1 + lm.y * crop_h) / small_h
                        
                        people_landmarks.append(landmarks)
                        break
            
            # Shot detection
            if people_landmarks:
                shot = self.shot_detector.update(
                    people_landmarks[0], 
                    frame.shape[1], 
                    frame.shape[0], 
                    timestamp
                )
                
                if shot is not None:
                    ball_trajectory = self.ball_tracker.get_trajectory()
                    result_analysis = ShotResultClassifier.analyze_trajectory(
                        ball_trajectory, 
                        frame.shape[0], 
                        frame.shape[1]
                    )
                    
                    shot['ball_tracking'] = {
                        'trajectory': ball_trajectory,
                        'result': result_analysis['result'],
                        'confidence': result_analysis['confidence'],
                        'analysis': result_analysis['analysis'],
                    }
                    
                    shot_file = output_dir / f"shot_{shot['id']}.json"
                    with open(shot_file, 'w') as f:
                        json.dump(shot, f, indent=2)
                    
                    detected_shots.append(shot)
                    self.ball_tracker.clear()
            
            # Track ball in every frame
            self.ball_tracker.update(frame, timestamp)
        
        cap.release()
        
        return {
            'total_frames': frame_count,
            'fps': fps,
            'duration_seconds': frame_count / fps,
            'shots_detected': len(detected_shots),
            'shots': detected_shots,
        }
