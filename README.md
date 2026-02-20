# AirBall 🏀

Computer vision + AI basketball coach. Analyze basketball shots with AI-powered pose detection, ball tracking, and personalized coaching insights.

## 🎯 What is AirBall?

AirBall is a full-stack web application that analyzes basketball videos to:
- **Detect basketball shots** from video frames
- **Track ball trajectory** in real-time
- **Classify shot results** (made/missed)
- **Analyze shooting form** using pose estimation
- **Generate coaching insights** with personalized improvement suggestions

Perfect for basketball players, coaches, and fitness enthusiasts who want data-driven feedback on their shooting technique.

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- **Python 3.9+** and **Node.js 16+**
- Git
- 2GB free disk space
- 8GB RAM minimum (16GB recommended)

### 1. Clone & Setup Backend
```bash
# Clone repository
git clone <repo-url>
cd AirBall/Server

# Create Python virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --reload
# Backend runs at http://localhost:8000
```

### 2. Setup Frontend
```bash
# In a new terminal
cd AirBall/client
npm install
npm run dev
# Frontend runs at http://localhost:3000
```

### 3. Use the Application
1. Open http://localhost:3000 in your browser
2. Click "Upload Video"
3. Select a basketball video (MP4, WebM, etc.)
4. Wait for processing (30 seconds - 5 minutes depending on video length)
5. View results and coaching insights

---

## 📚 Documentation

### For New Users
**[📖 Getting Started Guide](GettingStarted.md)** (5-10 min read)
- Quick start walkthrough
- System architecture overview
- Core concepts and terminology
- Video requirements and tips
- Database schema basics

### For Backend Developers
**[🔧 Backend Setup Guide](Server/README.md)** (10-15 min read)
- Detailed installation steps
- Environment configuration
- Database operations
- Video processing pipeline
- Troubleshooting

### For API Consumers
**[🔌 API Reference](docs/API.md)** (15-20 min read)
- Complete endpoint documentation
- Request/response examples
- Error codes and handling
- SDK examples (Python, JavaScript)
- Workflow examples

### For System Architects
**[🏗️ Architecture Documentation](docs/ARCHITECTURE.md)** (20-30 min read)
- High-level system design
- Component details
- Data models and flows
- Technology stack breakdown
- Performance considerations
- Security architecture
- Deployment checklist

### For Production Deployment
**[🚀 Deployment Guide](docs/DEPLOYMENT.md)** (30-45 min read)
- Pre-deployment checklist
- Backend deployment (Heroku, AWS, Docker)
- Frontend deployment (Vercel, Netlify)
- Database setup
- SSL/HTTPS configuration
- Monitoring and maintenance
- Troubleshooting and rollback

### Quick Reference
**[⚡ Quick Reference Guide](docs/QUICK_REFERENCE.md)** (5 min lookup)
- Common commands
- Environment variables
- File locations
- API endpoints summary
- Code snippets
- Troubleshooting solutions
- Performance benchmarks

---

## 🎬 System Overview

```
User Uploads Video
        ↓
Frontend Upload Form
        ↓
Backend: Process Video
  ├─ Person Detection (YOLO)
  ├─ Pose Estimation (MediaPipe)
  ├─ Shot Detection
  ├─ Ball Tracking
  └─ Result Classification
        ↓
Store Results in Database
        ↓
Analyze Performance & Generate Insights
        ↓
User Views Dashboard with Coaching Tips
```

---

## ⚙️ Technology Stack

### Frontend
- **Framework**: Next.js 14 (React)
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **HTTP**: Fetch API, custom axios client

### Backend
- **Framework**: FastAPI (Python)
- **Language**: Python 3.9+
- **Database**: SQLAlchemy ORM + SQLite/PostgreSQL
- **Computer Vision**: YOLOv8, MediaPipe, OpenCV
- **Async**: Python asyncio + FastAPI BackgroundTasks

### ML/AI
- **Object Detection**: YOLOv8n (nano model) for persons and balls
- **Pose Estimation**: MediaPipe Pose for body landmarks
- **LLM**: Ollama (optional, local LLM)
- **Libraries**: ultralytics, opencv-python, mediapipe, numpy

---

## 📊 Key Features

### Video Analysis
✅ Upload basketball videos (MP4, WebM, AVI, MOV)  
✅ Automatic shot detection  
✅ Ball tracking and trajectory analysis  
✅ Shot result classification (made/missed)  
✅ Frame-by-frame analysis  

### Performance Analytics
✅ Make percentage calculation  
✅ Form consistency scoring  
✅ Makes vs misses comparison  
✅ Comprehensive statistics  

### Coaching Insights
✅ AI-powered coaching suggestions  
✅ Form issue detection  
✅ Consistency analysis  
✅ Performance trends  

### Extensibility
✅ REST API for integration  
✅ Type-safe schemas (Pydantic)  
✅ Modular architecture  
✅ Easy to add new models/analyzers  

---

## 🎓 Example Video Requirements

**Optimal Video Setup**:
- **Resolution**: 1080p or higher (480p minimum)
- **Codec**: H.264, VP9, or similar
- **Frame Rate**: 30fps or 60fps
- **Lighting**: Well-lit background
- **Framing**: Full body visible for all shots
- **Length**: 30 seconds - 5 minutes

**Example Videos**:
- Shooting practice drills
- Game footage
- One-on-one scenarios
- Free throw practice
- Three-point shooting

**What Works Best**:
- Bright, consistent lighting
- Clear basketball and court
- Minimal camera movement (tripod)
- Full body in frame
- Clear shot arc visible

---

## 📁 Project Structure

```
AirBall/
├── client/                 # Frontend (Next.js)
│   ├── app/               # Pages and components
│   ├── lib/               # Utilities and API client
│   ├── public/            # Static assets
│   └── package.json       # npm dependencies
│
├── Server/                # Backend (FastAPI)
│   ├── app/
│   │   ├── main.py       # FastAPI app
│   │   ├── models.py     # Database models
│   │   ├── schemas.py    # Request/response schemas
│   │   ├── database.py   # Database config
│   │   └── routes/       # API endpoints
│   │
│   ├── ball_detector.py  # Ball tracking
│   ├── shot_detector.py  # Shot detection
│   ├── video_processor.py # Video pipeline
│   ├── shot_analyzer.py  # Analytics & insights
│   ├── Detection.py      # Live processing
│   ├── requirements.txt  # Python dependencies
│   └── app.db           # SQLite database
│
├── docs/                  # Documentation
│   ├── API.md            # API reference
│   ├── ARCHITECTURE.md   # System design
│   ├── DEPLOYMENT.md     # Production deployment
│   └── QUICK_REFERENCE.md # Quick commands
│
├── GettingStarted.md     # Getting started guide
└── README.md             # This file
```

---

## 🔧 Common Tasks

### Upload and Analyze Video
1. Open http://localhost:3000
2. Click "Upload Video"
3. Select your basketball video
4. Wait for processing
5. View results and insights

### Check Processing Status
```bash
curl http://localhost:8000/videos/status/{video_id}
```

### View API Documentation
```bash
# Open browser
http://localhost:8000/docs  # Swagger UI
http://localhost:8000/redoc # ReDoc
```

### Reset Database
```bash
# Delete database file
rm Server/app.db

# Server will recreate on next start
```

### View Logs
```bash
# Backend: watch console output
# Frontend: open browser Developer Tools (F12)
```

---

## 🐛 Troubleshooting

### Issue: "Port 8000 already in use"
```bash
# Find process using port
netstat -ano | findstr :8000  # Windows
lsof -i :8000               # macOS/Linux

# Kill process
taskkill /PID <PID> /F      # Windows
kill -9 <PID>               # macOS/Linux
```

### Issue: "Ball not detected in video"
- Ensure video lighting is good
- Check that full shot is visible
- Try shorter, focused videos first

### Issue: "CUDA out of memory"
```bash
# Force CPU mode in ball_detector.py
model = YOLO('yolov8n.pt').to('cpu')
```

### Issue: "Database locked"
```bash
# Restart backend
# Ctrl+C to stop
# Run again: uvicorn app.main:app --reload
```

See [QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) for more troubleshooting.

---

## 📖 Documentation Index

| Document | Purpose | Time |
|----------|---------|------|
| [Getting Started](GettingStarted.md) | Quick start & overview | 5-10 min |
| [Backend README](Server/README.md) | Installation & config | 10-15 min |
| [API Reference](docs/API.md) | Endpoints & examples | 15-20 min |
| [Architecture](docs/ARCHITECTURE.md) | System design | 20-30 min |
| [Deployment](docs/DEPLOYMENT.md) | Production setup | 30-45 min |
| [Quick Reference](docs/QUICK_REFERENCE.md) | Commands & snippets | 5 min |

---

## 🚀 Deployment

For production deployment, see [DEPLOYMENT.md](docs/DEPLOYMENT.md).

Quick summary:
- **Backend**: Heroku, AWS EC2, or Docker
- **Frontend**: Vercel, Netlify, or manual server
- **Database**: PostgreSQL (production)
- **SSL**: Let's Encrypt (free)

---

## 🤝 Contributing

To contribute:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🆘 Need Help?

1. **Quick Questions**: Check [QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)
2. **API Questions**: See [API.md](docs/API.md)
3. **Setup Issues**: Follow [GettingStarted.md](GettingStarted.md) or [Server/README.md](Server/README.md)
4. **Architecture Questions**: Read [ARCHITECTURE.md](docs/ARCHITECTURE.md)
5. **Deployment Issues**: See [DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## 📞 Support

- **Issues**: GitHub Issues (if using GitHub)
- **Discussions**: GitHub Discussions
- **Email**: support@airball.app (if applicable)

---

**Get Started**: [👉 GettingStarted.md](GettingStarted.md)

**Version**: 1.0.0  
**Last Updated**: February 2026


