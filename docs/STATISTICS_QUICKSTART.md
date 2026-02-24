# Quick Start Guide - User Statistics & History

## Setup Instructions

### 1. Backend Setup

#### Start the FastAPI server:
```bash
cd Server
python -m uvicorn app.main:app --reload
```

The backend will be available at `http://localhost:8000`

#### Verify new endpoints:
- Visit `http://localhost:8000/docs` to see the API documentation
- New endpoints should be visible under "statistics" tag

### 2. Frontend Setup

#### Install dependencies (if not already done):
```bash
cd client
npm install
```

#### Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 3. Using the New Features

#### First Time User Flow:

1. **Sign Up**
   - Navigate to `http://localhost:3000/signup`
   - Create an account with email and password
   - You'll be automatically logged in

2. **Upload Your First Video**
   - Go to home page (`/`)
   - Select a basketball shooting video
   - Click "Upload video"
   - The system will process it and detect shots

3. **View Your Statistics**
   - Click "Dashboard" in the navigation bar
   - See your overall shooting statistics
   - View performance metrics and trends

4. **Check Your History**
   - Click "History" in the navigation bar
   - Review all your practice sessions
   - See detailed stats for each video

## API Authentication

All statistics endpoints require authentication. The token is automatically handled by the frontend after login.

### Manual API Testing:

1. **Login and get token:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "yourpassword"}'
```

2. **Use token to fetch statistics:**
```bash
curl -X GET "http://localhost:8000/statistics/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Troubleshooting

### No statistics showing up?
- Make sure you're logged in
- Ensure you've uploaded at least one video
- Wait for video processing to complete (status: "completed")

### Videos not associated with your account?
- Make sure you were logged in when uploading
- Check that the token is being sent in the upload request
- Re-upload videos while authenticated

### Database issues?
- The database is automatically created when the server starts
- If you have old data, delete the database file and restart the server
- All tables will be recreated automatically

## Features Summary

| Feature | Endpoint | Page | Description |
|---------|----------|------|-------------|
| User Statistics | `GET /statistics/me` | `/dashboard` | Overall performance metrics |
| Video History | `GET /statistics/history` | `/history` | All practice sessions |
| Upload (Auth) | `POST /videos/upload` | `/` | Upload with user association |

## Next Steps

After setting up, you can:
- Upload multiple videos to see trends
- Track your improvement over time
- Review individual session performance
- Monitor your shooting percentage
- See your best session records

## Development Notes

### Adding New Statistics:
1. Update the `UserStatistics` schema in `schemas.py`
2. Add calculation logic in `routes/statistics.py`
3. Update the dashboard UI in `app/dashboard/page.tsx`

### Customizing the UI:
- All pages use Tailwind CSS for styling
- Dark mode is supported automatically
- Modify components in `client/app/` directories

## Support

For issues or questions:
1. Check the main documentation in `docs/`
2. Review API documentation at `/docs` endpoint
3. Verify all services are running correctly
