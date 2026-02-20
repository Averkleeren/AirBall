from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import uuid

router = APIRouter(
    prefix="/videos",
    tags=["videos"],
)

UPLOAD_DIR = Path("uploads")

@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Only video files are supported.")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    extension = Path(file.filename or "").suffix or ".mp4"
    video_id = uuid.uuid4().hex
    filename = f"{video_id}{extension}"
    destination = UPLOAD_DIR / filename

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "id": video_id,
        "filename": filename,
        "status": "uploaded",
    }
