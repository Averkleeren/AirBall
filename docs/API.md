# AirBall API Reference

Complete documentation of all API endpoints for the AirBall backend.

## Base URL

```
http://localhost:8000
```

## Authentication

Most endpoints require a JWT token. Include in the header:

```
Authorization: Bearer <your_jwt_token>
```

## Response Format

All responses are in JSON format:

**Success Response (2xx)**:
```json
{
  "data": {...},
  "status": "success"
}
```

**Error Response (4xx, 5xx)**:
```json
{
  "detail": "Error message"
}
```

---

## Authentication Endpoints

### POST /auth/signup

Create a new user account.

**Request**:
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "basketball_pro",
    "password": "SecurePassword123!"
  }'
```

**Request Body**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | ✓ | User email (must be valid email format) |
| username | string | ✓ | Unique username (3-50 chars) |
| password | string | ✓ | Password (min 8 chars, recommended: uppercase + numbers) |

**Response** (201 Created):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "basketball_pro",
  "created_at": "2026-02-20T10:30:45.123456"
}
```

**Errors**:
- `400`: Email or username already registered
- `422`: Validation error (invalid email format, password too short, etc.)

---

### POST /auth/login

Authenticate user and get JWT token.

**Request**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

**Request Body**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | ✓ | User email |
| password | string | ✓ | User password |

**Response** (200 OK):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "basketball_pro",
    "created_at": "2026-02-20T10:30:45.123456"
  }
}
```

**Errors**:
- `401`: Invalid email or password
- `404`: User not found

---

### GET /auth/me

Get current authenticated user information.

**Request**:
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "basketball_pro",
  "created_at": "2026-02-20T10:30:45.123456"
}
```

**Errors**:
- `401`: Invalid or expired token
- `404`: User not found

---

## Video Endpoints

### POST /videos/upload

Upload a basketball video for processing.

**Request**:
```bash
curl -X POST http://localhost:8000/videos/upload \
  -F "file=@basketball_shot.mp4"
```

Note: No authentication required for this endpoint (can be made public or secured as needed)

**Request Body**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | file | ✓ | Video file (MP4, MOV, AVI, etc.) |

**Response** (202 Accepted):
```json
{
  "id": 1,
  "video_id": "a1b2c3d4e5f6g7h8i9j0",
  "filename": "a1b2c3d4e5f6g7h8i9j0.mp4",
  "status": "processing"
}
```

**Errors**:
- `400`: File is not a video format
- `413`: File too large (max 500MB)
- `422`: Invalid file

---

### GET /videos/status/{video_id}

Check the processing status of a video.

**Request**:
```bash
curl -X GET http://localhost:8000/videos/status/a1b2c3d4e5f6g7h8i9j0
```

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| video_id | string | ✓ | The unique video ID from upload response |

**Response** (200 OK):
```json
{
  "video_id": "a1b2c3d4e5f6g7h8i9j0",
  "status": "completed",
  "shots_detected": 5,
  "duration_seconds": 45.2
}
```

Possible statuses:
- `processing`: Video is being analyzed
- `completed`: Processing finished successfully
- `failed`: Processing failed (check logs)

**Errors**:
- `404`: Video not found

---

### GET /videos/shots/{video_id}

Get all detected shots for a video.

**Request**:
```bash
curl -X GET http://localhost:8000/videos/shots/a1b2c3d4e5f6g7h8i9j0
```

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| video_id | string | ✓ | The unique video ID |

**Response** (200 OK):
```json
{
  "video_id": "a1b2c3d4e5f6g7h8i9j0",
  "status": "completed",
  "shots_detected": 5,
  "shots": [
    {
      "shot_id": "shot_uuid_1",
      "result": "made",
      "confidence": 0.92,
      "duration": 0.8,
      "ball_trajectory_length": 24,
      "analysis": "Parabolic motion: yes, Distance to hoop: 45px, Final Y: 600px"
    },
    {
      "shot_id": "shot_uuid_2",
      "result": "missed",
      "confidence": 0.78,
      "duration": 0.75,
      "ball_trajectory_length": 18,
      "analysis": "Parabolic motion: yes, Distance to hoop: 120px, Final Y: 650px"
    }
  ]
}
```

**Shot Result Values**:
- `made`: Ball successfully went through hoop (high confidence)
- `missed`: Ball did not go through hoop
- `unknown`: Insufficient data to determine result

**Errors**:
- `404`: Video not found
- `202`: Video still processing (try again in a few seconds)

---

### GET /videos/analysis/{video_id}

Get detailed analysis and coaching insights for a video.

**Request**:
```bash
curl -X GET http://localhost:8000/videos/analysis/a1b2c3d4e5f6g7h8i9j0
```

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| video_id | string | ✓ | The unique video ID |

**Response** (200 OK):
```json
{
  "video_id": "a1b2c3d4e5f6g7h8i9j0",
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
    "makes_metrics": {
      "count": 3,
      "avg_elbow_angle_at_release": 70.2,
      "avg_duration": 0.82,
      "avg_confidence": 0.88
    },
    "misses_metrics": {
      "count": 2,
      "avg_elbow_angle_at_release": 75.8,
      "avg_duration": 0.71,
      "avg_confidence": 0.78
    },
    "differences": {
      "elbow_angle_difference": 5.6
    }
  },
  "improvement_suggestions": [
    "Your shot timing is inconsistent. Practice with the same release point each time.",
    "Elbow angle varies 5.6° between makes and misses. Keep it consistent.",
    "Continue practicing! Keep mechanics consistent."
  ]
}
```

**Metrics Explained**:
- `make_percentage`: Percentage of shots that went in (0-100)
- `consistency_score`: How similar shots are to each other (0-1, higher = more consistent)
- `avg_elbow_angle_at_release`: Average angle of elbow when shooting (degrees)
- `avg_confidence`: Confidence score of ball detection and classification (0-1)
- `elbow_angle_difference`: Difference in elbow angle between makes and misses

**Errors**:
- `404`: Video not found
- `202`: Video still processing
- `204`: No shots detected in video

---

## Health Check

### GET /health

Check if the API is running.

**Request**:
```bash
curl http://localhost:8000/health
```

**Response** (200 OK):
```json
{
  "status": "ok"
}
```

---

## Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Successful GET request |
| 201 | Created | Successful user creation |
| 202 | Accepted | Video upload accepted, processing started |
| 204 | No Content | No shots found in video |
| 400 | Bad Request | Invalid file format |
| 401 | Unauthorized | Invalid or missing token |
| 404 | Not Found | Video or user not found |
| 413 | Request Entity Too Large | File exceeds 500MB |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error (check logs) |

---

## Rate Limiting

No rate limiting currently implemented. For production, consider:
- 100 requests per minute per IP
- 10 video uploads per user per day (adjust as needed)

---

## Examples

### Complete Workflow

1. **Sign Up**:
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "username": "shot_master",
    "password": "SecurePass123"
  }'
```

2. **Upload Video**:
```bash
curl -X POST http://localhost:8000/videos/upload \
  -F "file=@practice_session.mp4"
```

Response: `{"id": 1, "video_id": "abc123", "status": "processing"}`

3. **Check Status** (repeat every 5 seconds):
```bash
curl http://localhost:8000/videos/status/abc123
```

4. **Get Shots** (when status = "completed"):
```bash
curl http://localhost:8000/videos/shots/abc123
```

5. **Get Analysis**:
```bash
curl http://localhost:8000/videos/analysis/abc123
```

---

## SDK / Client Examples

### Python
```python
import requests

BASE_URL = "http://localhost:8000"

# Upload video
with open("shot.mp4", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/videos/upload",
        files={"file": f}
    )
    video_id = response.json()["video_id"]

# Get analysis
analysis = requests.get(f"{BASE_URL}/videos/analysis/{video_id}").json()
print(f"Make %: {analysis['make_percentage']}")
```

### JavaScript/TypeScript
```typescript
const BASE_URL = "http://localhost:8000";

// Upload video
async function uploadVideo(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  
  const response = await fetch(`${BASE_URL}/videos/upload`, {
    method: "POST",
    body: formData,
  });
  
  return response.json();
}

// Get analysis
async function getAnalysis(videoId: string) {
  const response = await fetch(`${BASE_URL}/videos/analysis/${videoId}`);
  return response.json();
}
```

### cURL
See examples above for cURL commands.

---

## WebSocket (Future)

For real-time processing updates:
```
ws://localhost:8000/ws/videos/{video_id}
```

Currently not implemented. Planned for v2.0.

---

## Changelog

### v1.0.0 (Current)
- Initial API release
- Video upload and processing
- Shot detection and analysis
- Ball tracking
- Form metrics extraction

### v1.1.0 (Planned)
- User authentication endpoints
- Video history
- Performance trends
- WebSocket for real-time updates

---

**Version**: 1.0.0  
**Last Updated**: February 2026
