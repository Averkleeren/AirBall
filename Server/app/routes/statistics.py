from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Optional

from ..database import get_db
from ..models import User, Video, Shot
from ..schemas import UserStatistics, VideoHistory
from ..auth import decode_token

router = APIRouter(
    prefix="/statistics",
    tags=["statistics"]
)


def get_current_user_from_token(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    """Extract and validate user from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = authorization.replace("Bearer ", "")
    token_data = decode_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = db.query(User).filter(User.email == token_data["email"]).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("/me", response_model=UserStatistics)
def get_user_statistics(
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Get comprehensive statistics for the current user."""
    
    # Get total videos
    total_videos = db.query(func.count(Video.id)).filter(
        Video.user_id == current_user.id,
        Video.status == "completed"
    ).scalar() or 0
    
    # Get all shots for user's videos
    shots_query = db.query(
        func.count(Shot.id).label('total_shots'),
        func.sum(case((Shot.shot_result == 'make', 1), else_=0)).label('makes'),
        func.sum(case((Shot.shot_result == 'miss', 1), else_=0)).label('misses')
    ).join(Video).filter(
        Video.user_id == current_user.id,
        Video.status == "completed"
    ).first()
    
    total_shots = shots_query.total_shots or 0
    makes = int(shots_query.makes or 0)
    misses = int(shots_query.misses or 0)
    
    # Calculate shooting percentage
    shooting_percentage = (makes / total_shots * 100) if total_shots > 0 else 0.0
    
    # Get total practice time (sum of all video durations)
    total_practice_time = db.query(func.sum(Video.duration_seconds)).filter(
        Video.user_id == current_user.id,
        Video.status == "completed"
    ).scalar() or 0.0
    
    # Average shots per session
    average_shots_per_session = total_shots / total_videos if total_videos > 0 else 0.0
    
    # Get best session percentage
    video_stats = db.query(
        Video.id,
        func.count(Shot.id).label('total'),
        func.sum(case((Shot.shot_result == 'make', 1), else_=0)).label('makes')
    ).join(Shot).filter(
        Video.user_id == current_user.id,
        Video.status == "completed"
    ).group_by(Video.id).all()
    
    best_session_percentage = 0.0
    for video_stat in video_stats:
        if video_stat.total > 0:
            session_pct = (video_stat.makes / video_stat.total * 100)
            best_session_percentage = max(best_session_percentage, session_pct)
    
    # Calculate recent trend (last 5 vs previous 5 sessions)
    recent_videos = db.query(Video).filter(
        Video.user_id == current_user.id,
        Video.status == "completed"
    ).order_by(Video.created_at.desc()).limit(10).all()
    
    recent_trend = "stable"
    if len(recent_videos) >= 6:
        # Calculate shooting percentage for last 5 videos
        recent_5_ids = [v.id for v in recent_videos[:5]]
        recent_shots = db.query(
            func.count(Shot.id).label('total'),
            func.sum(case((Shot.shot_result == 'make', 1), else_=0)).label('makes')
        ).filter(Shot.video_id.in_(recent_5_ids)).first()
        
        recent_pct = (recent_shots.makes / recent_shots.total * 100) if recent_shots.total > 0 else 0
        
        # Calculate shooting percentage for previous 5 videos
        prev_5_ids = [v.id for v in recent_videos[5:10]]
        prev_shots = db.query(
            func.count(Shot.id).label('total'),
            func.sum(case((Shot.shot_result == 'make', 1), else_=0)).label('makes')
        ).filter(Shot.video_id.in_(prev_5_ids)).first()
        
        prev_pct = (prev_shots.makes / prev_shots.total * 100) if prev_shots.total > 0 else 0
        
        if recent_pct > prev_pct + 5:
            recent_trend = "improving"
        elif recent_pct < prev_pct - 5:
            recent_trend = "declining"
    
    return UserStatistics(
        total_videos=total_videos,
        total_shots=total_shots,
        makes=makes,
        misses=misses,
        shooting_percentage=round(shooting_percentage, 2),
        total_practice_time=round(total_practice_time, 2),
        average_shots_per_session=round(average_shots_per_session, 2),
        best_session_percentage=round(best_session_percentage, 2),
        recent_trend=recent_trend
    )


@router.get("/history", response_model=List[VideoHistory])
def get_user_history(
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Get the user's video history with shot statistics."""
    
    # Get all user videos with shot statistics
    videos = db.query(Video).filter(
        Video.user_id == current_user.id,
        Video.status == "completed"
    ).order_by(Video.created_at.desc()).offset(offset).limit(limit).all()
    
    history = []
    for video in videos:
        # Get shot statistics for this video
        shot_stats = db.query(
            func.count(Shot.id).label('total'),
            func.sum(case((Shot.shot_result == 'make', 1), else_=0)).label('makes'),
            func.sum(case((Shot.shot_result == 'miss', 1), else_=0)).label('misses')
        ).filter(Shot.video_id == video.id).first()
        
        total = shot_stats.total or 0
        makes = int(shot_stats.makes or 0)
        misses = int(shot_stats.misses or 0)
        shooting_pct = (makes / total * 100) if total > 0 else 0.0
        
        history.append(VideoHistory(
            id=video.id,
            video_id=video.video_id,
            filename=video.filename,
            created_at=video.created_at,
            processed_at=video.processed_at,
            shots_detected=total,
            makes=makes,
            misses=misses,
            shooting_percentage=round(shooting_pct, 2),
            duration_seconds=video.duration_seconds
        ))
    
    return history
