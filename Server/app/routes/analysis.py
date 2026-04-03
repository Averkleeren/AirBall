import json
import os
import sys
import tempfile
import time

import cv2
import numpy as np
import ollama
from fastapi import APIRouter, HTTPException, UploadFile, File, status
from mediapipe.python.solutions import pose as mp_pose

# Allow importing shot_detector from the Server root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from shot_detector import ShotDetector

router = APIRouter(prefix="/analyze", tags=["analysis"])

LLM_MODEL = "gemma3:1b"


def _process_video(file_path: str) -> list[dict]:
    """Run MediaPipe pose detection + ShotDetector on every frame of a video file."""
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not open video file",
        )

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    detector = ShotDetector()
    pose = mp_pose.Pose(
        static_image_mode=False,
        min_detection_confidence=0.3,
        model_complexity=0,
    )

    shots: list[dict] = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        ts = frame_idx / fps
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            shot = detector.update(landmarks, frame_w, frame_h, ts)
            if shot is not None:
                shots.append(shot)

        frame_idx += 1

    cap.release()
    pose.close()
    return shots


def _derive_scores(shot: dict) -> dict:
    """Derive the four summary stats from real shot data."""
    confidence = shot.get("data_quality", {}).get("confidence", "low")
    base = {"high": 80, "medium": 70, "low": 60}.get(confidence, 65)

    if shot.get("timing", {}).get("leg_drive_before_arm_extension"):
        base += 10
    hold = shot.get("metrics", {}).get("follow_through", {}).get("hold_duration_s") or 0
    if hold > 0.1:
        base += 5
    shot_score = min(100, base)

    elbow = shot.get("metrics", {}).get("angles", {}).get("elbow", {})
    arc_angle = round(elbow.get("at_release_deg") or 0) or None

    peak_vel = shot.get("metrics", {}).get("velocities", {}).get("peak_wrist_vertical_px_s") or 0
    release_speed = round(abs(peak_vel) / 100, 1) if peak_vel else None

    ft_score = 70
    if hold > 0.05:
        ft_score += min(30, int(hold * 100))
    follow_through_score = min(100, ft_score)

    return {
        "shot_score": shot_score,
        "arc_angle": arc_angle,
        "release_speed": release_speed,
        "follow_through_score": follow_through_score,
    }


def _generate_feedback(shot_data: dict) -> str:
    """Call local Ollama LLM to generate coaching feedback from shot data."""
    try:
        response = ollama.chat(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful sports performance coach assistant. "
                        "Provide clear, concise, and actionable shooting feedback."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "I collected basketball shot form data. Provide feedback in four sections: "
                        "overall assessment, strengths, areas for improvement, and top 3 prioritized recommendations. "
                        "Avoid raw timestamps and precise floating-point values. Keep the tone encouraging and practical. "
                        f"Data: {json.dumps(shot_data, indent=2)}"
                    ),
                },
            ],
        )
        return response.get("message", {}).get("content", "").strip()
    except Exception as exc:
        return f"LLM feedback unavailable: {exc}"


@router.post("/video")
async def analyze_video(file: UploadFile = File(...)):
    """Accept a video upload, run pose analysis + LLM feedback, return results."""
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a video",
        )

    # Save uploaded file to a temp path so OpenCV can read it
    suffix = os.path.splitext(file.filename or "video.mp4")[1] or ".mp4"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        contents = await file.read()
        tmp.write(contents)
        tmp.close()

        shots = _process_video(tmp.name)

        if not shots:
            return {
                "status": "no_shots_detected",
                "shots": [],
                "message": "No basketball shots were detected in the video. Try a clearer angle showing your full body.",
            }

        results = []
        for shot in shots:
            scores = _derive_scores(shot)
            feedback = _generate_feedback(shot)
            results.append({
                "shot_id": shot.get("id"),
                "scores": scores,
                "feedback": feedback,
                "shot_data": shot,
            })

        # Use the first (or best) shot as the primary result
        primary = results[0]

        return {
            "status": "analyzed",
            "shot_score": primary["scores"]["shot_score"],
            "arc_angle": primary["scores"]["arc_angle"],
            "release_speed": primary["scores"]["release_speed"],
            "follow_through_score": primary["scores"]["follow_through_score"],
            "llm_feedback": primary["feedback"],
            "shot_data": primary["shot_data"],
            "total_shots_detected": len(results),
            "all_shots": results,
        }
    finally:
        os.unlink(tmp.name)
