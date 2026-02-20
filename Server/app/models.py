from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    videos = relationship("Video", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    filename = Column(String)
    file_path = Column(String)
    
    status = Column(String, default="processing")
    total_frames = Column(Integer, nullable=True)
    fps = Column(Float, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    shots_detected = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User", back_populates="videos")
    shots = relationship("Shot", back_populates="video", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Video(id={self.id}, video_id={self.video_id}, status={self.status})>"


class Shot(Base):
    __tablename__ = "shots"

    id = Column(Integer, primary_key=True, index=True)
    shot_id = Column(String, unique=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), index=True)
    
    start_ts = Column(Float)
    end_ts = Column(Float)
    duration = Column(Float)
    
    shot_result = Column(String, nullable=True)
    result_confidence = Column(Float, default=0.0)
    ball_trajectory_length = Column(Integer, default=0)
    ball_analysis = Column(Text, nullable=True)
    
    form_data = Column(JSON, nullable=True)
    feedback = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    video = relationship("Video", back_populates="shots")

    def __repr__(self):
        return f"<Shot(id={self.id}, shot_id={self.shot_id}, result={self.shot_result})>"
