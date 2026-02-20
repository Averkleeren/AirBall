# AirBall System Architecture

Technical documentation of AirBall's system design, components, and data flow.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Browser                              │
│                  (User Interface)                             │
├─────────────────────────────────────────────────────────────┤
│         Frontend (Next.js + React + TailwindCSS)             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Components:                                         │    │
│  │  - Video Upload Form                                │    │
│  │  - Results Dashboard                                │    │
│  │  - Analysis Display                                 │    │
│  └─────────────────────────────────────────────────────┘    │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTP/REST API
┌────────────────────────▼─────────────────────────────────────┐
│              Backend (FastAPI + Python)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  API Layer (Routes)                                  │   │
│  │  - /auth/* (Authentication)                         │   │
│  │  - /videos/upload (Video Upload)                    │   │
│  │  - /videos/status (Processing Status)               │   │
│  │  - /videos/shots (Shot Results)                     │   │
│  │  - /videos/analysis (Analysis & Insights)          │   │
│  └──────────────────────────────────────────────────────┘   │
│                         │                                     │
│  ┌──────────────────────┴──────────────────────────────┐   │
│  │          Processing Pipeline                         │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │  Video Processor (video_processor.py)      │   │   │
│  │  │ - Load video  frames                       │   │   │
│  │  │ - Person detection (YOLO)                 │   │   │
│  │  │ - Pose estimation (MediaPipe)             │   │   │
│  │  │ - Shot detection (ShotDetector)           │   │   │
│  │  │ - Ball tracking (BallTracker)             │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  │                                                      │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │  Analytics Engine (shot_analyzer.py)       │   │   │
│  │  │ - Form metric extraction                   │   │   │
│  │  │ - Make/miss classification                 │   │   │
│  │  │ - Makes vs misses comparison               │   │   │
│  │  │ - Coaching suggestion generation           │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  │                                                      │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │  AI/LLM Integration (Ollama)               │   │   │
│  │  │ - Custom feedback generation               │   │   │
│  │  │ - Coaching tips                            │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └───────────────────────┬──────────────────────────────┘   │
│                          │                                    │
│  ┌───────────────────────▼──────────────────────────────┐   │
│  │        Data Persistence Layer                         │   │
│  │  ┌───────────────┐  ┌────────────────────────────┐  │   │
│  │  │  SQLAlchemy   │  │  Database Models           │  │   │
│  │  │  ORM          │  │  - User                    │  │   │
│  │  └───────────────┘  │  - Video                   │  │   │
│  │                     │  - Shot                    │  │   │
│  │                     └────────────────────────────┘  │   │
│  └───────────────────────┬──────────────────────────────┘   │
│                          │                                    │
└──────────────────────────┼────────────────────────────────────┘
                           │
┌──────────────────────────▼────────────────────────────────────┐
│           File System & Database                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  /uploads/     - Raw uploaded videos                │   │
│  │  /shots/       - Processed shot JSON files          │   │
│  │  app.db        - SQLite database (development)      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Frontend (Next.js)

**Location**: `/client`

**Responsibilities**:
- User interface for video upload
- Authentication forms (login/signup)
- Results display and visualization
- API communication

**Key Files**:
- `app/page.tsx` - Video upload page
- `app/login/page.tsx` - Login page
- `app/signup/page.tsx` - Sign up page
- `lib/api.ts` - API client functions

**Technologies**:
- Next.js 14 (React framework)
- React 18 (UI library)
- TypeScript (type safety)
- TailwindCSS (styling)
- Fetch API (HTTP requests)

---

### 2. Backend API (FastAPI)

**Location**: `/Server/app/`

**Responsibilities**:
- Handle HTTP requests
- Coordinate video processing
- Manage database operations
- Provide REST API endpoints

**Key Files**:
- `main.py` - FastAPI app setup and routing
- `routes/auth.py` - Authentication endpoints
- `routes/videos.py` - Video processing endpoints
- `models.py` - Database models
- `schemas.py` - Request/response validation
- `database.py` - Database configuration

**Technologies**:
- FastAPI (modern web framework)
- Pydantic (data validation)
- SQLAlchemy (ORM)
- Python 3.9+

---

### 3. Video Processing Pipeline

**Location**: `/Server/video_processor.py`

**Process**:
1. Load video file
2. For each frame:
   - Resize for performance
   - Detect persons with YOLO
   - Extract pose with MediaPipe landmarks
   - Detect shots using motion analysis
   - Track basketball trajectory
3. For detected shots:
   - Extract form metrics
   - Classify result (made/missed)
   - Save to database

**Performance**:
- 10s video: ~30-60s processing
- 30s video: ~2-3 minutes
- 60s video: ~4-6 minutes

Factors:
- CPU/GPU availability
- Video resolution
- Number of detected shots
- Server load

---

### 4. Detection Module

**Location**: `/Server/shot_detector.py`

**Detects**: Basketball shot motion

**Input**: MediaPipe pose landmarks + frame dimensions

**Algorithm**:
1. Track wrist vertical velocity
2. Detect upward wrist motion + elbow extension
3. Monitor knee bend and hip drive
4. Detect apex (lowest wrist point)
5. Detect release (when velocity drops) 
6. Finalize shot data

**Output**: Shot JSON with:
- Timing (start, apex, release)
- Form metrics (angles, velocities)
- Phase durations
- Key frame indices

---

### 5. Ball Tracking Module

**Location**: `/Server/ball_detector.py`

**Detects**: Basketball in video

**Classes**:
- `BallTracker` - Tracks ball across frames
- `ShotResultClassifier` - Classifies results

**Algorithm**:
1. YOLO detects objects
2. Filter for circular objects (basketball)
3. Associate current detection with last position
4. Build trajectory history
5. Analyze final trajectory to classify result

**Trajectory Analysis**:
- Parabolic motion: Yes/No (indicates shot)
- Distance to hoop: pixels
- Final Y position: pixels
- Trajectory length: frames tracked

**Classification**:
- **Made**: Ball through hoop zone, continues down
- **Missed**: Ball trajectory away from hoop
- **Unknown**: Insufficient data

---

### 6. Analytics Engine

**Location**: `/Server/shot_analyzer.py`

**Functions**:
- `ShotAnalyzer`: Analyzes individual video
- `PerformanceTrendAnalyzer`: Analyzes trends over sessions

**Metrics Calculated**:
- Make percentage
- Consistency score
- Average form metrics
- Makes vs misses comparison
- Coaching suggestions

**Suggestions Generated**:
- Low make rate warning
- Inconsistency detection
- Form discrepancies
- Detection confidence warnings

---

## Data Models

### User
```
id: int (primary key)
email: str (unique)
username: str (unique)
hashed_password: str
created_at: datetime
updated_at: datetime
videos: List[Video] (relationship)
```

### Video
```
id: int (primary key)
video_id: str (unique UUID)
user_id: int (foreign key) [nullable]
filename: str
file_path: str
status: str (processing/completed/failed)
total_frames: int [nullable]
fps: float [nullable]
duration_seconds: float [nullable]
shots_detected: int
created_at: datetime
processed_at: datetime [nullable]
shots: List[Shot] (relationship)
```

### Shot
```
id: int (primary key)
shot_id: str (unique UUID)
video_id: int (foreign key)
start_ts: float (timestamp)
end_ts: float (timestamp)
duration: float (seconds)
shot_result: str (made/missed/unknown)
result_confidence: float (0-1)
ball_trajectory_length: int (frames)
ball_analysis: str (text analysis)
form_data: JSON (full metrics)
feedback: str [nullable] (LLM feedback)
created_at: datetime
video: Video (relationship)
```

---

## Data Flow

### Video Upload Flow
```
1. User selects video in UI
2. Frontend sends multipart/form-data to API
3. Backend stores video in /uploads/
4. Video record created in database
5. Background task started
6. Return video_id immediately to user

Response: 202 Accepted
{
  "id": 1,
  "video_id": "abc123...",
  "status": "processing"
}
```

### Processing Flow
```
1. VideoProcessor loads video
2. For each frame:
   a. Detect person (YOLO)
   b. Extract pose (MediaPipe)
   c. Update shot detector
   d. Track ball
3. For each detected shot:
   a. Extract form metrics
   b. Analyze ball trajectory
   c. Classify result
   d. Create Shot record in DB
4. Generate coaching suggestions
5. Update Video status to "completed"
```

### Analysis Flow
```
1. User requests GET /videos/analysis/{video_id}
2. Backend fetches video + all shots
3. ShotAnalyzer calculates metrics
4. Compares makes vs misses
5. Generates suggestions
6. Returns JSON response
```

---

## Technology Stack

### Frontend
- **Framework**: Next.js 14
- **Language**: TypeScript
- **UI Library**: React 18
- **Styling**: TailwindCSS
- **HTTP**: Fetch API
- **Package Manager**: npm

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.9+
- **ORM**: SQLAlchemy
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Computer Vision**: OpenCV, YOLOv8, MediaPipe
- **Async**: Uvicorn, Python asyncio
- **Authentication**: JWT (python-jose)
- **Hashing**: bcrypt
- **Package Manager**: pip

### Infrastructure
- **Deployment**: Docker (optional)
- **Server**: Uvicorn (backend), Vercel (frontend)
- **Database**: SQLite/PostgreSQL
- **File Storage**: Local filesystem (can migrate to S3)

---

## Performance Considerations

### Optimization
- YOLO runs at 0.25 scale (faster)
- MediaPipe static mode (faster than video mode)
- Shot detector uses efficient deque
- Ball tracker caches trajectory in memory

### Bottlenecks
- YOLO model inference (GPU helps significantly)
- MediaPipe pose estimation (CPU intensive)
- Video I/O (faster with SSD)
- Database queries (indexed on video_id, shot_id)

### Scaling
- Use GPU (NVIDIA CUDA for YOLO)
- Process videos in queue (Celery/RabbitMQ)
- Use PostgreSQL instead of SQLite
- Cache models in production
- Use CDN for video distribution

---

## Security

### Authentication
- Passwords hashed with bcrypt
- JWT tokens (30-minute expiry)
- CORS enabled (localhost:3000 only)

### File Uploads
- Validate file type
- Maximum size: 500MB
- Store outside web root
- Scan for malware (optional)

### Database
- SQL injection protected (SQLAlchemy)
- Parameterized queries
- Index sensitive columns

### Deployment
- Use HTTPS in production
- Validate JSON input
- Rate limit API
- Add request/response logging

---

## Deployment Checklist

### Backend
- [ ] Set `DEBUG = False`
- [ ] Use PostgreSQL in production
- [ ] Configure `SECRET_KEY` environment variable
- [ ] Set `CORS_ORIGINS` to production domain
- [ ] Enable HTTPS
- [ ] Add database backups
- [ ] Configure Redis for caching (optional)
- [ ] Set up monitoring/logging
- [ ] Use Gunicorn + Nginx
- [ ] Configure SSL certificates

### Frontend
- [ ] Update `NEXT_PUBLIC_API_BASE_URL`
- [ ] Run `npm run build` (production build)
- [ ] Test production build locally
- [ ] Deploy to Vercel or similar
- [ ] Configure domain
- [ ] Enable CORS headers
- [ ] Set up CDN (optional)

---

## Future Enhancements

### Short Term (v1.1)
- User profiles and history
- Performance trends over time
- Heatmaps of make/miss locations
- Video playback with skeleton overlay

### Medium Term (v2.0)
- Real-time webcam processing
- Multi-person tracking
- Peer comparison
- Mobile app (React Native)
- WebSocket for live updates
- Workout plan generation

### Long Term (v3.0)
- Court detection and calibration
- 3D pose analysis
- Comparison to professional players
- AI-generated drill recommendations
- Integration with fitness trackers
- Multi-sport support

---

## Troubleshooting Guide

### Processing Hangs
```
Cause: Model loading, insufficient GPU memory
Solution: Check logs, restart service, try CPU-only mode
```

### Low Accuracy
```
Cause: Poor video quality, lighting, framing
Solution: Improve video setup, frame full body, good lighting
```

### Database Errors
```
Cause: Concurrent access, corrupted DB
Solution: Use WAL mode, upgrade to PostgreSQL
```

### Memory Issues
```
Cause: Large video files, model memory
Solution: Reduce video resolution, process in chunks, upgrade RAM
```

---

## Contributing

To add new features:

1. **Backend**: Add endpoint in `routes/`, update `models.py`, add `schemas.py`
2. **Frontend**: Add page in `app/`, update `lib/api.ts`
3. **Processing**: Add analysis in `shot_analyzer.py` or new module
4. **Tests**: Add unit tests for new functionality
5. **Docs**: Update this architecture doc

---

**Version**: 1.0.0  
**Last Updated**: February 2026
