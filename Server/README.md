# AirBall Backend Setup Guide

Complete setup and configuration guide for the AirBall FastAPI backend.

## Table of Contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Running the Server](#running-the-server)
4. [Project Structure](#project-structure)
5. [API Endpoints](#api-endpoints)
6. [Database](#database)
7. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Virtual environment tool (venv)

### Step 1: Create Virtual Environment

```bash
cd Server
python -m venv venv
```

### Step 2: Activate Virtual Environment

**On Windows:**
```bash
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **FastAPI**: Modern Python web framework
- **Uvicorn**: ASGI server
- **SQLAlchemy**: ORM for database
- **Pydantic**: Data validation
- **Ollama**: Local LLM for feedback
- **MediaPipe**: Pose detection
- **YOLO**: Object detection
- **OpenCV**: Video processing

### Step 4: Verify Installation

```bash
python -c "import fastapi; import cv2; import mediapipe; print('✓ All dependencies installed')"
```

---

## Configuration

### Environment Variables

Create a `.env` file in the `Server/` directory:

```env
# Database
DATABASE_URL=sqlite:///./app.db

# FastAPI
API_TITLE=AirBall API
API_VERSION=1.0.0

# CORS (allow frontend)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Authentication
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Video Processing
MAX_UPLOAD_SIZE_MB=500
VIDEO_UPLOAD_DIR=./uploads
SHOTS_OUTPUT_DIR=./shots

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### Database Setup

The database initializes automatically on first run. To reset:

```bash
# Remove the database file
rm app.db

# Backend will recreate tables on startup
python -m uvicorn app.main:app --reload
```

---

## Running the Server

### Development Mode

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- `--reload`: Auto-restart on code changes
- `--host 0.0.0.0`: Accept connections from any IP
- `--port 8000`: Run on port 8000

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

- `--workers 4`: Run with 4 worker processes
- Remove `--reload` for production

### Verify Server is Running

```bash
# Should return {"status": "ok"}
curl http://localhost:8000/health
```

Open API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Project Structure

```
Server/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── database.py          # Database configuration
│   ├── auth.py              # Authentication utilities
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   └── routes/
│       ├── __init__.py
│       ├── auth.py          # Authentication endpoints
│       └── videos.py        # Video upload & analysis endpoints
│
├── ball_detector.py         # Ball tracking module
├── shot_detector.py         # Shot detection module
├── shot_analyzer.py         # Shot analysis & insights
├── video_processor.py       # Video processing pipeline
├── camera.py                # Camera capture (for live streaming)
├── Detection.py             # Live detection stream
│
├── llm_test.py              # LLM feedback testing
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## API Endpoints

### Authentication

#### Sign Up
```
POST /auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "basketball_player",
  "password": "secure_password"
}

Response: 201 Created
{
  "id": 1,
  "email": "user@example.com",
  "username": "basketball_player",
  "created_at": "2026-02-20T10:00:00"
}
```

#### Login
```
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {...}
}
```

#### Get Current User
```
GET /auth/me
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "email": "user@example.com",
  "username": "basketball_player"
}
```

### Video Processing

#### Upload Video
```
POST /videos/upload
Content-Type: multipart/form-data

file: <video.mp4>

Response: 202 Accepted
{
  "id": 1,
  "video_id": "a1b2c3d4e5f6...",
  "filename": "a1b2c3d4e5f6.mp4",
  "status": "processing"
}
```

#### Check Processing Status
```
GET /videos/status/{video_id}

Response: 200 OK
{
  "video_id": "a1b2c3d4e5f6...",
  "status": "completed",
  "shots_detected": 5,
  "duration_seconds": 45.2
}
```

#### Get Shot List
```
GET /videos/shots/{video_id}

Response: 200 OK
{
  "video_id": "a1b2c3d4e5f6...",
  "status": "completed",
  "shots_detected": 5,
  "shots": [
    {
      "shot_id": "shot_uuid...",
      "result": "made",
      "confidence": 0.92,
      "duration": 0.8,
      "ball_trajectory_length": 24,
      "analysis": "Parabolic motion: yes, Distance to hoop: 45px..."
    },
    ...
  ]
}
```

#### Get Detailed Analysis
```
GET /videos/analysis/{video_id}

Response: 200 OK
{
  "video_id": "a1b2c3d4e5f6...",
  "total_shots": 5,
  "makes": 3,
  "misses": 2,
  "make_percentage": 60.0,
  "consistency_score": 0.78,
  "form_metrics": {
    "avg_elbow_angle_at_release": 72.5,
    "avg_confidence": 0.85
  },
  "makes_vs_misses": {
    "makes_count": 3,
    "misses_count": 2,
    "makes_metrics": {...},
    "misses_metrics": {...},
    "differences": {
      "elbow_angle_difference": 8.5
    }
  },
  "improvement_suggestions": [
    "Your shot timing is inconsistent. Practice with the same release point...",
    "Current make rate is 60.0%. Focus on form consistency..."
  ]
}
```

---

## Database

### Models

#### User
- `id`: Primary key
- `email`: Unique email
- `username`: Unique username
- `hashed_password`: Bcrypt hash
- `created_at`: Timestamp
- `updated_at`: Timestamp

#### Video
- `id`: Primary key
- `video_id`: Unique UUID
- `user_id`: Foreign key to User
- `filename`: Original filename
- `file_path`: Storage path
- `status`: processing/completed/failed
- `total_frames`: Frame count
- `fps`: Frames per second
- `duration_seconds`: Video length
- `shots_detected`: Number of shots
- `created_at`: Upload timestamp
- `processed_at`: Completion timestamp

#### Shot
- `id`: Primary key
- `shot_id`: Unique UUID
- `video_id`: Foreign key to Video
- `start_ts`: Start timestamp
- `end_ts`: End timestamp
- `duration`: Shot duration
- `shot_result`: made/missed/unknown
- `result_confidence`: 0-1 confidence
- `ball_trajectory_length`: Frames tracked
- `ball_analysis`: Analysis text
- `form_data`: Full metrics JSON
- `feedback`: LLM feedback
- `created_at`: Timestamp

### Access Database

Using SQLite CLI:
```bash
# Open database
sqlite3 app.db

# List tables
.tables

# View schema
.schema users
.schema videos
.schema shots

# Query data
SELECT COUNT(*) FROM videos;
SELECT * FROM videos LIMIT 5;

# Exit
.quit
```

---

## Video Processing Pipeline

### Process Flow
```
1. User uploads video
   ↓
2. Video saved to uploads/ directory
   ↓
3. Background task starts processing
   ↓
4. For each frame:
   - Person detection (YOLO)
   - Pose extraction (MediaPipe)
   - Shot detection (ShotDetector)
   - Ball tracking (BallTracker)
   ↓
5. For each detected shot:
   - Extract form metrics
   - Analyze ball trajectory
   - Classify result (made/missed/unknown)
   ↓
6. Generate coaching suggestions
   ↓
7. Save to database
```

### Processing Time
- **10-second video**: ~30-60 seconds
- **30-second video**: ~2-3 minutes
- **60-second video**: ~4-6 minutes

Factors affecting speed:
- CPU/GPU availability
- Video resolution
- Number of detected shots
- Server load

---

## Troubleshooting

### Port Already in Use
```
Error: Address already in use
Solution:
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or use different port
uvicorn app.main:app --port 8001
```

### Import Errors
```
Error: ModuleNotFoundError: No module named 'fastapi'
Solution:
pip install -r requirements.txt
source venv/bin/activate
```

### YOLO Model Download
```
Error: Model weights not downloaded on first run
Solution:
# Pre-download models
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
python -c "import mediapipe as mp; mp.solutions.pose"
```

### Database Errors
```
Error: sqlite3.OperationalError: table already exists
Solution:
rm app.db
# Restart server to recreate tables
```

### Processing Hangs
```
Error: Video processing never completes
Solution:
1. Check server logs for errors
2. Try with a shorter test video
3. Ensure sufficient disk space (at least 1GB free)
4. Check system resources (RAM, CPU)
```

### CORS Issues (Frontend can't call API)
```
Error: CORS error in browser console
Solution:
Update CORS_ORIGINS in .env:
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
Restart backend server
```

---

## Performance Optimization

### Models & Caching
Models are cached after first load:
- YOLO (person detection): ~356 MB
- MediaPipe (pose): ~100 MB
- Models stay in memory between requests

### Database Optimization
```python
# Add indexes for faster queries
# Already configured in models.py:
# - video_id is indexed
# - shot_id is indexed
# - user_id is indexed
```

### Video Preprocessing
For faster processing, preprocess videos:
```bash
# Reduce resolution to 720p
ffmpeg -i input.mp4 -vf scale=1280:720 -crf 23 output.mp4

# Reduce framerate to 30fps
ffmpeg -i input.mp4 -r 30 output.mp4
```

---

## Security Notes

### Authentication
- Passwords are hashed with bcrypt
- JWT tokens expire after 30 minutes (configurable)
- Use HTTPS in production

### File Uploads
- Maximum file size: 500 MB (configurable)
- Files validated as video format
- Stored in isolated `uploads/` directory

### CORS
- Default: Only allow localhost:3000
- Update CORS_ORIGINS in .env for production

### Database
- Use SQLite for development only
- Use PostgreSQL for production
- Enable WAL mode for concurrent access

---

## Next Steps

1. **Start the server**: `python -m uvicorn app.main:app --reload`
2. **View API docs**: http://localhost:8000/docs
3. **Test upload**: Use curl or frontend
4. **Monitor logs**: Watch terminal for processing progress
5. **Check results**: Query `/analysis` endpoint for insights

---

## Support

For detailed API documentation, visit `/docs` endpoint when server is running.

For issues:
1. Check logs in terminal
2. Review database with SQLite CLI
3. Test endpoints with curl
4. Check CORS settings if frontend fails

---

**Version**: 1.0.0  
**Python**: 3.9+  
**Last Updated**: February 2026
