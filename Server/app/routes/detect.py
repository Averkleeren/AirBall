from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import shutil
import os
from Server.Detection import run_detection  # Adjust import if needed
from Server.llm_test import generate_feedback

router = APIRouter()

UPLOAD_DIR = "uploaded_videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/detect")
async def detect_video(video: UploadFile = File(...)):
    video_path = os.path.join(UPLOAD_DIR, video.filename)
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)
    try:
        result = run_detection(video_path)  # Your detection function
        feedback = None
        try:
            feedback = generate_feedback(result)
        except Exception as fb_err:
            feedback = f"feedback generation failed: {fb_err}"
        return JSONResponse(content={"analysis": result, "feedback": feedback})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)