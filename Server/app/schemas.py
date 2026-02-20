from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None


class ShotResponse(BaseModel):
    id: int
    shot_id: str
    shot_result: Optional[str]
    result_confidence: float
    ball_trajectory_length: int
    ball_analysis: Optional[str]
    start_ts: float
    end_ts: float
    duration: float
    feedback: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class VideoResponse(BaseModel):
    id: int
    video_id: str
    filename: str
    status: str
    total_frames: Optional[int]
    fps: Optional[float]
    duration_seconds: Optional[float]
    shots_detected: int
    created_at: datetime
    processed_at: Optional[datetime]
    shots: List[ShotResponse] = []

    class Config:
        from_attributes = True


class VideoSummary(BaseModel):
    video_id: str
    status: str
    shots_detected: int
    duration_seconds: Optional[float]
    fps: Optional[float]

