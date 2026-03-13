import os
import shutil

from fastapi import APIRouter, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse

# Detection & LLM modules live one level up (Server/)
from Detection import run_detection
from llm_test import generate_feedback

router = APIRouter(tags=["detection"])

UPLOAD_DIR = "uploaded_videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

_ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


@router.post("/detect")
async def detect_video(video: UploadFile = File(...)):
    """Accept a video upload, run shot detection, and return analysis + LLM feedback."""
    filename = video.filename or ""
    ext = os.path.splitext(filename)[1].lower()

    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided.",
        )
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed: {sorted(_ALLOWED_EXTENSIONS)}",
        )

    video_path = os.path.join(UPLOAD_DIR, filename)
    try:
        # Save upload to disk
        with open(video_path, "wb") as buf:
            shutil.copyfileobj(video.file, buf)

        # Run CV pipeline
        result = run_detection(video_path)

        # Generate LLM coaching feedback
        feedback: str | None = None
        feedback_warning: str | None = None
        try:
            feedback = generate_feedback(result)
        except Exception as fb_err:
            feedback_warning = f"Feedback generation failed: {fb_err}"

        response: dict = {"analysis": result}
        if feedback is not None:
            response["feedback"] = feedback
        if feedback_warning is not None:
            response["feedback_warning"] = feedback_warning

        return JSONResponse(content=response)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    finally:
        # Always clean up the uploaded file to avoid disk buildup
        if os.path.exists(video_path):
            os.remove(video_path)
