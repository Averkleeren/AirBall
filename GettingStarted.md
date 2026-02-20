# AirBall - AI Basketball Shot Analysis Platform

**AirBall** is an AI-powered basketball training platform that analyzes your shooting form, detects made/missed shots, and provides personalized coaching feedback.

## Features

- **AI-Powered Shot Detection**: Automatically detects basketball shots from video
- **Form Analysis**: Tracks body position, elbow angle, release height, and more
- **Ball Tracking**: Monitors ball trajectory to classify shots as made or missed
- **Performance Analytics**: Compare successful shots vs missed ones to identify patterns
- **Coaching Insights**: Get automatic suggestions for improving your form
- **Session History**: Track progress over time with detailed shot-by-shot data

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Git

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd AirBall
```

### 2. Backend Setup (5 minutes)
```bash
cd Server
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

The backend will start on `http://localhost:8000`

### 3. Frontend Setup (5 minutes)
```bash
cd client
npm install
npm run dev
```

The frontend will start on `http://localhost:3000`

### 4. Upload and Analyze a Video

1. Open `http://localhost:3000` in your browser
2. Click "Upload video" and select a basketball shot video
3. Wait for processing to complete
4. View detailed analysis and improvement suggestions

---

## Full Documentation

- **[Backend Setup Guide](./Server/README.md)** - Detailed backend installation and configuration
- **[Frontend Setup Guide](./client/README.md)** - Frontend development and deployment
- **[API Reference](./docs/API.md)** - Complete API endpoint documentation
- **[Architecture](./docs/ARCHITECTURE.md)** - System design and component overview

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                       │
│              Video Upload & Results Dashboard                │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼──────────────────────────────────────┐
│                  Backend (FastAPI)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   Video      │  │   Shot       │  │   Analytics      │   │
│  │   Upload     │  │   Detection  │  │   Engine         │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   Ball       │  │   Form       │  │   LLM Feedback   │   │
│  │   Tracker    │  │   Analysis   │  │   Generation     │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│         Database (SQLite/PostgreSQL)                         │
│  - Users                                                     │
│  - Videos & Shots                                            │
│  - Form Metrics & Results                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## How It Works

### 1. Video Upload
User selects a basketball shot video and uploads it to the server.

### 2. Shot Detection
The backend processes the video using:
- **YOLO**: Detects people in the frame
- **MediaPipe**: Extracts body pose landmarks
- **Shot Detector**: Identifies shooting motion based on pose dynamics

### 3. Ball Tracking
- **YOLO Ball Detection**: Locates the basketball in each frame
- **Trajectory Analysis**: Tracks ball path to classify results (made/missed)

### 4. Form Analysis
For each detected shot, the system extracts:
- Elbow angle at release
- Release height and follow-through
- Knee bend and leg drive timing
- Head stability during release
- Wrist snap and forearm rotation

### 5. Analytics & Feedback
- **Makes vs Misses Comparison**: Identifies form differences between successful and failed shots
- **Consistency Scoring**: Measures shot-to-shot repeatability
- **Coaching Suggestions**: AI-generated recommendations based on detected patterns
- **LLM Feedback**: Detailed feedback from language model (using Ollama)

---

## Core Concepts

### Detection Window
The time period during which a shot is occurring (from initial load to release).

### Shot Metrics
Quantifiable measurements of shooting form:
- **Angles**: Elbow, knee, hip angles at key phases
- **Velocities**: Wrist vertical velocity, forearm angular velocity
- **Heights**: Release height relative to head/shoulders
- **Timing**: Relative timing of leg drive, arm extension, release

### Ball Trajectory
The path of the basketball from release to final position.
- **Made**: Ball goes through estimated hoop zone and continues downward
- **Missed**: Ball trajectories away from hoop or leaves frame
- **Unknown**: Insufficient trajectory data for classification

### Consistency Score
0-1 scale measuring how similar shots are to each other.
- `1.0` = All shots nearly identical
- `0.5` = Moderate variation
- `0.0` = High variation between shots

---

## Video Requirements

For best results:
- **Format**: MP4, MOV, AVI (any common video format)
- **Resolution**: 720p or higher recommended
- **FPS**: 30fps or higher
- **Duration**: 10-60 seconds of continuous shooting
- **Framing**: Full body visible from feet to head, basket visible if possible

---

## Database Schema

### Users
- `id`: Unique identifier
- `email`: User email (unique)
- `username`: Display name (unique)
- `hashed_password`: Bcrypt hashed password
- `created_at`: Account creation timestamp

### Videos
- `id`: Database ID
- `video_id`: Unique upload ID
- `user_id`: Owner's user ID
- `filename`: Original filename
- `file_path`: Storage location
- `status`: processing/completed/failed
- `total_frames`: Total video frames
- `fps`: Frames per second
- `duration_seconds`: Video length
- `shots_detected`: Number of shots found
- `created_at`: Upload timestamp
- `processed_at`: Completion timestamp

### Shots
- `id`: Database ID
- `shot_id`: Unique shot ID
- `video_id`: Parent video
- `start_ts` / `end_ts`: Shot timing
- `duration`: Shot length in seconds
- `shot_result`: made/missed/unknown
- `result_confidence`: 0-1 confidence score
- `ball_trajectory_length`: Number of ball detection frames
- `ball_analysis`: Analysis text
- `form_data`: Full JSON of form metrics
- `feedback`: LLM-generated feedback

---

## Common Tasks

### Start Development Servers
```bash
# Terminal 1: Backend
cd Server
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd client
npm run dev
```

### Check Backend Health
```bash
curl http://localhost:8000/health
```

### View API Documentation
Open `http://localhost:8000/docs` (Swagger UI)

### Access Database (SQLite)
```bash
sqlite3 Server/app.db
.tables  # List all tables
SELECT * FROM videos;  # Query videos
```

### Reset Database
```bash
rm Server/app.db
# Restart backend to reinitialize
```

### View Shot Analysis JSON
```bash
# After a video processes, check the shots directory:
ls Server/shots/
cat Server/shots/shot_<shot-id>.json
```

---

## Troubleshooting

### Backend won't start
```
Error: Port 8000 already in use
Solution: Kill process using port 8000 or specify different port:
uvicorn app.main:app --port 8001 --reload
```

### ModuleNotFoundError
```
Error: No module named 'ultralytics'
Solution: Install dependencies:
pip install -r requirements.txt
```

### CUDA/GPU errors
```
Error: CUDA out of memory
Solution: The system will fallback to CPU. For faster processing, ensure NVIDIA drivers are installed.
```

### Video upload fails
```
Error: 413 Request Entity Too Large
Solution: Increase FastAPI upload limit in app/main.py:
from fastapi import FastAPI
app = FastAPI()
```

### Processing takes too long
- Videos >60 seconds may take extended processing time
- Solution: Split video into smaller clips (10-20 seconds)

---

## API Quick Reference

### Upload Video
```bash
curl -X POST http://localhost:8000/videos/upload \
  -F "file=@basketball_shot.mp4"
```
Returns: `{"id": 1, "video_id": "abc123...", "status": "processing"}`

### Check Processing Status
```bash
curl http://localhost:8000/videos/status/abc123
```

### Get Shot Data
```bash
curl http://localhost:8000/videos/shots/abc123
```

### Get Analysis & Suggestions
```bash
curl http://localhost:8000/videos/analysis/abc123
```

See [API.md](./docs/API.md) for complete endpoint documentation.

---

## Development

### Project Structure
```
AirBall/
├── client/                  # Next.js frontend
│   ├── app/               # Pages and layouts
│   ├── lib/               # API utilities
│   └── package.json
├── Server/                 # FastAPI backend
│   ├── app/
│   │   ├── models.py      # Database models
│   │   ├── schemas.py     # Data validation
│   │   ├── routes/        # API endpoints
│   │   └── main.py        # App initialization
│   ├── ball_detector.py   # Ball tracking
│   ├── shot_detector.py   # Shot detection
│   ├── shot_analyzer.py   # Analytics
│   ├── video_processor.py # Video processing pipeline
│   └── requirements.txt
├── docs/                   # Documentation
└── README.md
```

### Adding New Features

**Backend**:
1. Create model in `app/models.py`
2. Create schema in `app/schemas.py`
3. Add route in `app/routes/`
4. Test with `pytest`

**Frontend**:
1. Create component in `app/`
2. Add API call in `lib/api.ts`
3. Test in browser

### Running Tests
```bash
cd Server
pytest tests/
```

---

## Performance Tips

- **Batch Processing**: Process multiple videos in sequence rather than parallel
- **Video Preprocessing**: Compress videos before upload for faster processing
- **Model Caching**: Models are cached after first load
- **Database Indexing**: Queries on `video_id` and `shot_id` are indexed

---

## Support & Troubleshooting

For issues:
1. Check [Troubleshooting](#troubleshooting) section above
2. Review backend logs: Check terminal where `uvicorn` is running
3. Check frontend console: Open DevTools (F12) in browser
4. Check database: Ensure tables exist with `sqlite3 Server/app.db .tables`

---

## Next Steps

1. **Download & Install**: Follow [Quick Start](#quick-start)
2. **Read Backend Guide**: [Server/README.md](./Server/README.md)
3. **Upload First Video**: Test with a 15-30 second basketball shot video
4. **Explore API**: Visit `http://localhost:8000/docs`
5. **Review Results**: Check `/analysis` endpoint for detailed insights

---

## License

[Your License Here]

## Contributors

[Your Name/Team]

---

**Version**: 1.0.0  
**Last Updated**: February 2026
