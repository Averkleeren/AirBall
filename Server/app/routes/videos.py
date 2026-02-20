from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from pathlib import Path
from sqlalchemy.orm import Session
import shutil
import uuid
import json
from datetime import datetime

from ..database import get_db
from ..models import Video, Shot
from ..schemas import VideoResponse, ShotResponse

router = APIRouter(
    prefix="/videos",
    tags=["videos"],
)

UPLOAD_DIR = Path("uploads")
SHOTS_DIR = Path("shots")


async def process_video_in_background(
    video_path: str, 
    video_id: str, 
    db_video_id: int,
    db: Session
):
    """Process video asynchronously to detect shots."""
    try:
        from video_processor import VideoProcessor
        
        processor = VideoProcessor()
        result = processor.process_video(video_path, output_dir=str(SHOTS_DIR))
        
        db_video = db.query(Video).filter(Video.id == db_video_id).first()
        if db_video:
            db_video.status = "completed"
            db_video.total_frames = result['total_frames']
            db_video.fps = result['fps']
            db_video.duration_seconds = result['duration_seconds']
            db_video.shots_detected = result['shots_detected']
            db_video.processed_at = datetime.utcnow()
            
            for shot_data in result['shots']:
                shot = Shot(
                    shot_id=shot_data['id'],
                    video_id=db_video_id,
                    start_ts=shot_data['detection_window']['start'],
                    end_ts=shot_data['detection_window']['end'],
                    duration=shot_data['detection_window']['duration'],
                    shot_result=shot_data.get('ball_tracking', {}).get('result'),
                    result_confidence=shot_data.get('ball_tracking', {}).get('confidence', 0.0),
                    ball_trajectory_length=len(shot_data.get('ball_tracking', {}).get('trajectory', [])),
                    ball_analysis=shot_data.get('ball_tracking', {}).get('analysis'),
                    form_data=shot_data,
                )
                db.add(shot)
            
            db.commit()
        
    except Exception as e:
        print(f"Error processing video {video_id}: {e}")
        db_video = db.query(Video).filter(Video.id == db_video_id).first()
        if db_video:
            db_video.status = "failed"
            db.commit()


@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...), 
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Only video files are supported.")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    SHOTS_DIR.mkdir(parents=True, exist_ok=True)

    extension = Path(file.filename or "").suffix or ".mp4"
    video_id = uuid.uuid4().hex
    filename = f"{video_id}{extension}"
    destination = UPLOAD_DIR / filename

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_video = Video(
        video_id=video_id,
        user_id=None,
        filename=filename,
        file_path=str(destination),
        status="processing",
    )
    db.add(db_video)
    db.commit()
    db.refresh(db_video)

    if background_tasks:
        background_tasks.add_task(
            process_video_in_background, 
            str(destination), 
            video_id,
            db_video.id,
            db
        )

    return {
        "id": db_video.id,
        "video_id": video_id,
        "filename": filename,
        "status": "processing",
    }


@router.get("/status/{video_id}")
async def get_video_status(video_id: str, db: Session = Depends(get_db)):
    """Get video processing status."""
    video = db.query(Video).filter(Video.video_id == video_id).first()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return {
        "video_id": video.video_id,
        "status": video.status,
        "shots_detected": video.shots_detected,
        "duration_seconds": video.duration_seconds,
    }


@router.get("/shots/{video_id}")
async def get_video_shots(video_id: str, db: Session = Depends(get_db)):
    """Retrieve detected shots for a video."""
    video = db.query(Video).filter(Video.video_id == video_id).first()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    shots = db.query(Shot).filter(Shot.video_id == video.id).all()
    
    return {
        "video_id": video.video_id,
        "status": video.status,
        "shots_detected": len(shots),
        "shots": [
            {
                "shot_id": shot.shot_id,
                "result": shot.shot_result,
                "confidence": shot.result_confidence,
                "duration": shot.duration,
                "ball_trajectory_length": shot.ball_trajectory_length,
                "analysis": shot.ball_analysis,
            }
            for shot in shots
        ],
    }


@router.get("/analysis/{video_id}")
async def get_video_analysis(video_id: str, db: Session = Depends(get_db)):
    """Get detailed analysis and coaching insights for a video."""
    from shot_analyzer import ShotAnalyzer
    
    video = db.query(Video).filter(Video.video_id == video_id).first()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    shots = db.query(Shot).filter(Shot.video_id == video.id).all()
    
    if not shots:
        return {
            "video_id": video.video_id,
            "message": "No shots detected in this video",
        }
    
    shots_data = [
        json.loads(shot.form_data) if isinstance(shot.form_data, str) else shot.form_data
        for shot in shots
    ]
    
    analyzer = ShotAnalyzer(shots_data)
    stats = analyzer.get_shot_stats()
    comparison = analyzer.get_makes_vs_misses_analysis()
    suggestions = analyzer.get_improvement_suggestions()
    
    return {
        "video_id": video.video_id,
        "total_shots": stats.total_shots,
        "makes": stats.makes,
        "misses": stats.misses,
        "make_percentage": round(stats.make_percentage, 1),
        "consistency_score": round(stats.consistency_score, 2),
        "form_metrics": {
            "avg_elbow_angle_at_release": round(stats.avg_elbow_angle_at_release, 1) if hasattr(stats, 'avg_elbow_angle_at_release') else 0.0,
            "avg_confidence": round(stats.avg_confidence, 2),
        },
        "makes_vs_misses": {
            "makes_count": comparison.get('makes_count'),
            "misses_count": comparison.get('misses_count'),
            "makes_metrics": comparison.get('makes'),
            "misses_metrics": comparison.get('misses'),
            "differences": comparison.get('differences'),
        },
        "improvement_suggestions": suggestions,
    }

