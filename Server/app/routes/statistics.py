from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Optional

from ..database import get_db
from ..models import User, Video, Shot
from ..schemas import UserStatistics, VideoHistory
from ..auth import decode_token, extract_token_from_header

router = APIRouter(prefix="/statistics", tags=["statistics"])

_COMPLETED = "completed"
_MAKE = "make"
_MISS = "miss"


def _require_user(authorization: Optional[str], db: Session) -> User:
    """Extract and validate user from Authorization header."""
    token = extract_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token_data = decode_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == token_data["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _shot_aggregates():
    """Return reusable column expressions for shot make/miss counts."""
    return (
        func.count(Shot.id).label("total"),
        func.sum(case((Shot.shot_result == _MAKE, 1), else_=0)).label("makes"),
        func.sum(case((Shot.shot_result == _MISS, 1), else_=0)).label("misses"),
    )


@router.get("/me", response_model=UserStatistics)
def get_user_statistics(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Get comprehensive statistics for the current user."""
    current_user = _require_user(authorization, db)
    user_filter = (Video.user_id == current_user.id, Video.status == _COMPLETED)

    # Aggregate shots in one query
    total_col, makes_col, misses_col = _shot_aggregates()
    shots_row = db.query(total_col, makes_col, misses_col).join(Video).filter(*user_filter).first()
    total_shots = shots_row.total or 0
    makes = int(shots_row.makes or 0)
    misses = int(shots_row.misses or 0)
    shooting_percentage = (makes / total_shots * 100) if total_shots else 0.0

    # Video-level aggregates (count + total duration)
    vid_row = db.query(
        func.count(Video.id).label("cnt"),
        func.coalesce(func.sum(Video.duration_seconds), 0.0).label("dur"),
    ).filter(*user_filter).first()
    total_videos = vid_row.cnt or 0
    total_practice_time = float(vid_row.dur)
    average_shots_per_session = total_shots / total_videos if total_videos else 0.0

    # Best session percentage
    total_col2, makes_col2, _ = _shot_aggregates()
    per_video = (
        db.query(total_col2, makes_col2)
        .join(Video)
        .filter(*user_filter)
        .group_by(Video.id)
        .all()
    )
    best_session_percentage = max(
        ((r.makes / r.total * 100) for r in per_video if r.total),
        default=0.0,
    )

    # Recent trend (last 5 vs previous 5)
    recent_ids = [
        v.id for v in db.query(Video.id)
        .filter(*user_filter)
        .order_by(Video.created_at.desc())
        .limit(10)
        .all()
    ]
    recent_trend = "stable"
    if len(recent_ids) >= 6:
        def _pct(ids):
            r = db.query(
                func.count(Shot.id).label("t"),
                func.sum(case((Shot.shot_result == _MAKE, 1), else_=0)).label("m"),
            ).filter(Shot.video_id.in_(ids)).first()
            return (r.m / r.t * 100) if r.t else 0

        diff = _pct(recent_ids[:5]) - _pct(recent_ids[5:])
        if diff > 5:
            recent_trend = "improving"
        elif diff < -5:
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
        recent_trend=recent_trend,
    )


@router.get("/history", response_model=List[VideoHistory])
def get_user_history(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    """Get the user's video history with shot statistics (single query)."""
    current_user = _require_user(authorization, db)
    total_col, makes_col, misses_col = _shot_aggregates()

    rows = (
        db.query(Video, total_col, makes_col, misses_col)
        .outerjoin(Shot, Shot.video_id == Video.id)
        .filter(Video.user_id == current_user.id, Video.status == _COMPLETED)
        .group_by(Video.id)
        .order_by(Video.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    history = []
    for video, total, makes, misses in rows:
        total = total or 0
        makes = int(makes or 0)
        misses = int(misses or 0)
        history.append(VideoHistory(
            id=video.id,
            video_id=video.video_id,
            filename=video.filename,
            created_at=video.created_at,
            processed_at=video.processed_at,
            shots_detected=total,
            makes=makes,
            misses=misses,
            shooting_percentage=round((makes / total * 100) if total else 0.0, 2),
            duration_seconds=video.duration_seconds,
        ))
    return history
