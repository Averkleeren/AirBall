import cv2
import mediapipe as mp
import numpy as np
import os
import time
from flask import Flask, Response
from ultralytics import YOLO

from shot_detector import ShotDetector
from ball_tracker import BallColorTracker
from camera import picam2

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Model / detector singletons
# ---------------------------------------------------------------------------
person_detector = YOLO('yolov8n.pt')  # YOLOv8 nano – fast enough for Pi

mp_pose = mp.solutions.pose
pose_detector = mp_pose.Pose(
    static_image_mode=True,
    min_detection_confidence=0.3,
    model_complexity=0,
)

shot_detector = ShotDetector()
ball_tracker = BallColorTracker()

SCALE = 0.25  # downsample factor for inference speed


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _detect_people(rgb_small_frame, small_w, small_h):
    """Run YOLO person detection + MediaPipe pose on *rgb_small_frame*.

    Returns a list of adjusted landmark objects (one per detected person).
    Landmarks are already re-scaled to be relative to the small frame
    (normalised 0-1 within the small_w x small_h space).
    """
    results = person_detector(rgb_small_frame, conf=0.3, classes=[0])
    people_landmarks = []

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = (int(v) for v in box.xyxy[0].cpu().numpy())
            person_crop = rgb_small_frame[y1:y2, x1:x2]
            if person_crop.size == 0:
                continue

            pose_results = pose_detector.process(person_crop)
            if not pose_results.pose_landmarks:
                continue

            crop_h, crop_w = person_crop.shape[:2]
            landmarks = pose_results.pose_landmarks.landmark

            # Remap landmark coords back into small-frame space
            for lm in landmarks:
                lm.x = (x1 + lm.x * crop_w) / small_w
                lm.y = (y1 + lm.y * crop_h) / small_h

            people_landmarks.append((landmarks, (x1, y1, x2, y2)))
            break  # one person per frame is enough for shot detection

    return people_landmarks


def _draw_skeleton(frame, landmarks, scale):
    """Draw the MediaPipe skeleton onto *frame* (full-resolution)."""
    h, w = frame.shape[:2]
    coords = [
        (int(lm.x * w), int(lm.y * h))
        for lm in landmarks
    ]
    for start_idx, end_idx in mp_pose.POSE_CONNECTIONS:
        if start_idx < len(coords) and end_idx < len(coords):
            cv2.line(frame, coords[start_idx], coords[end_idx], (0, 200, 255), 2)
    for (x, y) in coords:
        cv2.circle(frame, (x, y), 3, (0, 165, 255), -1)


# ---------------------------------------------------------------------------
# Video-file processing (used by the /detect API route)
# ---------------------------------------------------------------------------

def run_detection(video_path):
    """Process a video file frame-by-frame and return detected shots."""
    shots = []
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Unable to open video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        ts = frame_idx / fps
        frame_idx += 1

        small_frame = cv2.resize(frame, (0, 0), fx=SCALE, fy=SCALE)
        small_h, small_w = small_frame.shape[:2]
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        people = _detect_people(rgb_small, small_w, small_h)
        if people:
            landmarks, _ = people[0]
            shot = shot_detector.update(landmarks, frame.shape[1], frame.shape[0], ts)
            if shot is not None:
                shots.append(shot)

    cap.release()
    return {"video_path": video_path, "shots": shots}


# ---------------------------------------------------------------------------
# Live-camera stream
# ---------------------------------------------------------------------------

def generate_frames():
    """Yield MJPEG frames from the Pi camera with skeleton + ball overlay."""
    while True:
        raw_frame = picam2.capture_array()
        frame = cv2.cvtColor(raw_frame, cv2.COLOR_RGBA2BGR)

        small_frame = cv2.resize(frame, (0, 0), fx=SCALE, fy=SCALE)
        small_h, small_w = small_frame.shape[:2]
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # --- Person detection & skeleton ---
        people = _detect_people(rgb_small, small_w, small_h)
        if people:
            landmarks, (x1, y1, x2, y2) = people[0]

            # Draw bounding box (scale coords back to full frame)
            inv = 1.0 / SCALE
            cv2.rectangle(
                frame,
                (int(x1 * inv), int(y1 * inv)),
                (int(x2 * inv), int(y2 * inv)),
                (0, 255, 0), 2,
            )
            cv2.putText(
                frame, "Person",
                (int(x1 * inv), int(y1 * inv) - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2,
            )
            _draw_skeleton(frame, landmarks, SCALE)

            ts = time.time()
            shot = shot_detector.update(landmarks, frame.shape[1], frame.shape[0], ts)
            if shot is not None:
                txt = (
                    f"Shot! id={shot['id'][:8]} "
                    f"dur={shot['detection_window']['duration']:.2f}s"
                )
                cv2.putText(
                    frame, txt, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2,
                )

        # --- Ball tracking overlay ---
        ball_pos = ball_tracker.update(frame)
        if ball_pos is not None:
            bx, by, br = ball_pos
            cv2.circle(frame, (bx, by), br, (0, 140, 255), 3)
            cv2.circle(frame, (bx, by), 4, (0, 255, 255), -1)

        # Draw ball trail
        trail = ball_tracker.get_trail()
        for i in range(1, len(trail)):
            if trail[i - 1] and trail[i]:
                alpha = i / len(trail)
                color = (0, int(140 * alpha), int(255 * alpha))
                cv2.line(frame, trail[i - 1], trail[i], color, 2)

        # Encode and yield
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n'
            + buffer.tobytes()
            + b'\r\n'
        )


# ---------------------------------------------------------------------------
# Flask routes
# ---------------------------------------------------------------------------

@app.route('/video_feed')
def video_feed():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame',
    )


@app.route('/')
def index():
    return "<h1>AirBall Live Feed</h1><img src='/video_feed' width='640'>"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
