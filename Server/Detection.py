import cv2
import mediapipe as mp
import numpy as np
import os
import time
from flask import Flask, Response
from ultralytics import YOLO

from shot_detector import ShotDetector
from camera import picam2

app = Flask(__name__)

# Initialize person detection with YOLO
person_detector = YOLO('yolov8n.pt')  # Load YOLOv8 nano model

# Initialize body detection
mp_pose = mp.solutions.pose
pose_detector = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.3, model_complexity=0)

# Shot detection and camera setup moved to modules
detector = ShotDetector()


def generate_frames():
    while True:
        raw_frame = picam2.capture_array()
        frame = cv2.cvtColor(raw_frame, cv2.COLOR_RGBA2BGR)
        # Resize for speed
        scale = 0.25
        small_frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
        small_h, small_w = small_frame.shape[:2]
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Person detection with YOLO
        results = person_detector(rgb_small_frame, conf=0.3, classes=[0])  # class 0 is person

        people_landmarks = []
        processed = False
        for result in results:
            if processed:
                break
            for box in result.boxes:
                if processed:
                    break
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # Crop the person
                person_crop = rgb_small_frame[y1:y2, x1:x2]
                if person_crop.size == 0:
                    continue

                # Pose detection on crop
                pose_results = pose_detector.process(person_crop)
                if pose_results.pose_landmarks:
                    crop_h, crop_w = person_crop.shape[:2]
                    landmarks = pose_results.pose_landmarks.landmark

                    # Adjust landmarks to be relative to small_frame
                    for lm in landmarks:
                        lm.x = (x1 + lm.x * crop_w) / small_w
                        lm.y = (y1 + lm.y * crop_h) / small_h

                    # Compute coords for drawing (full frame)
                    coords = []
                    for lm in landmarks:
                        x = int(lm.x * frame.shape[1])
                        y = int(lm.y * frame.shape[0])
                        coords.append((x, y))

                    people_landmarks.append(landmarks)  # Store adjusted landmarks

                    # Draw bounding box
                    cv2.rectangle(frame, (int(x1/scale), int(y1/scale)), (int(x2/scale), int(y2/scale)), (0, 255, 0), 2)
                    cv2.putText(frame, "Person Detected", (int(x1/scale), int(y1/scale) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    # Draw skeleton
                    for connection in mp_pose.POSE_CONNECTIONS:
                        start_idx, end_idx = connection
                        if start_idx < len(coords) and end_idx < len(coords):
                            cv2.line(frame, coords[start_idx], coords[end_idx], (0, 200, 255), 2)

                    # Draw keypoints
                    for (x, y) in coords:
                        cv2.circle(frame, (x, y), 3, (0, 165, 255), -1)

                    processed = True
                    break

        # For shot detection, use the first person's landmarks if any
        if people_landmarks:
            ts = time.time()
            shot = detector.update(people_landmarks[0], frame.shape[1], frame.shape[0], ts)  # Assuming landmarks is list of tuples, but detector expects mediapipe landmarks?
            if shot is not None:
                # overlay a small notification
                txt = f"Shot detected: {shot['id'][:8]} dur={shot['detection_window']['duration']:.2f}s"
                cv2.putText(frame, txt, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # Web Stream
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return "<h1>Security Feed (Body Tracking Only)</h1><img src='/video_feed' width='640'>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
