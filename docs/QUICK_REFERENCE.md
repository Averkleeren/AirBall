# Quick Reference Guide

Fast lookup for common commands, configurations, and code snippets.

## Commands

### Backend Setup
```bash
cd Server
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
# Backend running at http://localhost:8000
```

### Frontend Setup
```bash
cd client
npm install
npm run dev
# Frontend running at http://localhost:3000
```

### Database
```bash
# Reset database (deletes all data)
rm Server/app.db  # Or delete from file explorer

# View with SQLite CLI
sqlite3 Server/app.db
sqlite> .tables
sqlite> SELECT * FROM user;
sqlite> .exit
```

### Testing API
```bash
# Health check
curl http://localhost:8000/health

# Upload video
curl -X POST -F "video=@path/to/video.mp4" \
  http://localhost:8000/videos/upload

# Check status
curl http://localhost:8000/videos/status/video-id

# Get shots
curl http://localhost:8000/videos/shots/video-id

# Get analysis
curl http://localhost:8000/videos/analysis/video-id
```

---

## Environment Variables

### Backend (.env)
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./app.db
CORS_ORIGINS=http://localhost:3000
DEBUG=True
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## File Locations

| Purpose | Path |
|---------|------|
| Uploaded videos | Server/uploads/ |
| Shot JSON files | Server/shots/ |
| Database | Server/app.db |
| Frontend components | client/app/ |
| CSS styles | client/app/globals.css |
| API utilities | client/lib/api.ts |
| Backend models | Server/app/models.py |
| Video routes | Server/app/routes/videos.py |
| Ball detector | Server/ball_detector.py |
| Video processor | Server/video_processor.py |
| Shot analyzer | Server/shot_analyzer.py |

---

## API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /health | Check backend health |
| POST | /auth/signup | Create new user |
| POST | /auth/login | Authenticate user |
| GET | /auth/me | Get current user |
| POST | /videos/upload | Upload video |
| GET | /videos/status/{id} | Check processing status |
| GET | /videos/shots/{id} | Get shot results |
| GET | /videos/analysis/{id} | Get analysis & suggestions |

---

## Code Snippets

### Upload Video (Frontend)
```typescript
// client/lib/api.ts
export async function uploadVideo(file: File) {
  const formData = new FormData();
  formData.append('video', file);
  
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_BASE_URL}/videos/upload`,
    { method: 'POST', body: formData }
  );
  
  return response.json();
}
```

### Call Upload (React)
```typescript
const handleUpload = async (file: File) => {
  const response = await uploadVideo(file);
  const videoId = response.video_id;
  // Poll /videos/status/{videoId} for completion
};
```

### Ball Detection (Backend)
```python
# Server/ball_detector.py
from ball_detector import BallTracker

tracker = BallTracker()
for frame in frames:
    detections = tracker.detect_ball(frame)
    tracker.update(detections, frame_idx)
    
results = {
    'made': tracker.shot_result == 'made',
    'trajectory_length': tracker.trajectory_length,
    'confidence': tracker.result_confidence
}
```

### Shot Analysis (Backend)
```python
# Server/shot_analyzer.py
from shot_analyzer import ShotAnalyzer

analyzer = ShotAnalyzer(shots)
stats = analyzer.get_shot_stats()
print(f"Make %: {stats.make_percentage:.1f}%")
print(f"Total: {stats.total_shots}")

suggestions = analyzer.get_improvement_suggestions()
for suggestion in suggestions:
    print(f"- {suggestion}")
```

### Database Query (Backend)
```python
# Server/app/models.py
from sqlalchemy import select
from app.models import Video, Shot

# Get video with all shots
video = session.query(Video).filter(Video.video_id == 'abc123').first()

# Get all shots for video
shots = session.query(Shot).filter(Shot.video_id == video.id).all()

# Add new shot
new_shot = Shot(
    shot_id='shot-123',
    video_id=video.id,
    shot_result='made',
    result_confidence=0.95
)
session.add(new_shot)
session.commit()
```

---

## Configuration

### YOLO Model
```python
# Server/ball_detector.py
model = YOLO('yolov8n.pt')  # nano model (fastest)
# model = YOLO('yolov8s.pt')  # small model
# model = YOLO('yolov8m.pt')  # medium model (most accurate)

results = model.predict(frame, conf=0.5)
```

### MediaPipe Pose
```python
# Server/shot_detector.py
with mp_pose.Pose(
    static_image_mode=False,
    model_complexity=0,  # 0=light, 1=full
    smooth_landmarks=True
) as pose:
    results = pose.process(rgb_frame)
```

### Video Processor Settings
```python
# Server/video_processor.py
FRAME_SKIP = 1  # Process every Nth frame
SCALE_FACTOR = 0.25  # Resize frame to this scale
MIN_SHOT_CONFIDENCE = 0.5  # Minimum confidence for shot
```

---

## Common Issues & Solutions

### Issue: CUDA out of memory
```
Solution: 
1. Use smaller YOLO model (nano instead of large)
2. Set inference device to CPU:
   model = YOLO('yolov8n.pt').to('cpu')
3. Reduce frame size in video_processor.py
4. Upgrade GPU memory or use cloud GPU
```

### Issue: Ball not detected
```
Solution:
1. Check video lighting (YOLO prefers well-lit scenes)
2. Ensure full shot is visible (not cut off)
3. Lower confidence threshold in ball_detector.py
4. Use larger YOLO model (medium or large)
```

### Issue: Slow processing
```
Solution:
1. Use GPU instead of CPU (install CUDA)
2. Increase FRAME_SKIP to skip more frames
3. Reduce SCALE_FACTOR to make frames smaller
4. Use smaller YOLO model (nano)
```

### Issue: Database locked
```
Solution:
1. Ensure only one server instance running
2. Stop server: Ctrl+C
3. Delete app.db to reset
4. Restart server
```

### Issue: CORS errors
```
Solution:
1. Check frontend URL in CORS_ORIGINS
2. For development: CORS_ORIGINS=http://localhost:3000
3. For production: Set to your domain
4. Restart backend server
```

---

## Testing Checklist

Before deployment:

- [ ] Backend starts without errors
- [ ] Frontend loads at http://localhost:3000
- [ ] Can upload video from UI
- [ ] Processing starts (watch console logs)
- [ ] Processing completes and status updates
- [ ] Can view shots from API
- [ ] Can view analysis from API
- [ ] Database records saved correctly
- [ ] API returns proper error messages
- [ ] No console errors in browser

---

## Performance Benchmarks

**Test Environment**: Intel i7, 16GB RAM, RTX 3070

| Video Length | Resolution | Processing Time |
|--------------|------------|-----------------|
| 10 seconds | 1080p | 30-45 seconds |
| 30 seconds | 1080p | 2-3 minutes |
| 60 seconds | 1080p | 4-6 minutes |
| 10 seconds | 480p | 10-15 seconds |
| 30 seconds | 480p | 45-60 seconds |

*With GPU acceleration. CPU-only is 3-5x slower.*

---

## Dependency Versions

### Backend (requirements.txt)
```
fastapi>=0.104.0
uvicorn>=0.24.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
opencv-python>=4.8.0
ultralytics>=8.0.0
mediapipe>=0.10.0
numpy>=1.24.0
python-jose>=3.3.0
bcrypt>=4.1.0
python-multipart>=0.0.6
```

### Frontend (package.json)
```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "typescript": "^5.0.0"
  },
  "devDependencies": {
    "tailwindcss": "^3.0.0",
    "postcss": "^8.0.0"
  }
}
```

---

## Useful Commands

### View Logs
```bash
# Backend logs (if running in foreground)
uvicorn app.main:app --reload
# Shows real-time processing logs

# Frontend logs
# Open browser DevTools: F12 → Console
```

### Restart Services
```bash
# Backend: Press Ctrl+C, then run again
uvicorn app.main:app --reload

# Frontend: Press Ctrl+C, then run again
npm run dev
```

### Clean Up
```bash
# Remove all uploaded videos
rmdir /s Server/uploads
mkdir Server/uploads

# Remove all shot JSON files
rmdir /s Server/shots
mkdir Server/shots

# Reset database
del Server/app.db
```

### Debug Mode
```python
# Add to any Python file to print debug info
import json
print(json.dumps(data, indent=2))

# Set logging level in backend
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Git Workflow

```bash
# Clone repository
git clone <repo-url>
cd AirBall

# Create feature branch
git checkout -b feature/my-feature

# Before committing
git status  # Check changes
git diff    # Review changes

# Commit changes
git add .
git commit -m "Add descriptive message"

# Push to GitHub
git push origin feature/my-feature

# Create Pull Request on GitHub
```

---

## System Requirements

### Minimum
- Python 3.9+
- Node.js 16+
- 8GB RAM
- 2GB disk space
- Modern browser (Chrome, Firefox, Safari)

### Recommended
- Python 3.11+
- Node.js 18+
- 16GB RAM
- NVIDIA GPU (RTX 3070 or better)
- 5GB disk space for models
- NVIDIA CUDA 11.8+

### For GPU Support
```bash
# Install CUDA (follow NVIDIA guide)
# Install cuDNN

# Install Python packages with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## Further Reading

- [Backend Setup](Server/README.md) - Detailed backend installation
- [Getting Started](GettingStarted.md) - Quick start guide
- [API Reference](API.md) - Complete API documentation
- [Architecture](ARCHITECTURE.md) - System design deep dive

---

**Last Updated**: February 2026  
**Version**: 1.0.0
