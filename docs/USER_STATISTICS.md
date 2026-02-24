# User Statistics & History Feature

## Overview
Added comprehensive user statistics tracking and history viewing capabilities to the AirBall application. Users can now track their basketball shooting performance over time with detailed metrics and visualizations.

## Features Implemented

### Backend (FastAPI)

#### 1. New Statistics API Endpoints
- **GET `/statistics/me`** - Retrieve comprehensive user statistics
  - Total videos/sessions
  - Total shots attempted
  - Makes and misses breakdown
  - Shooting percentage
  - Total practice time
  - Average shots per session
  - Best session percentage
  - Recent performance trend (improving/declining/stable)

- **GET `/statistics/history`** - Retrieve user's video history
  - List of all processed videos
  - Per-video statistics (makes, misses, shooting percentage)
  - Timestamp and duration information
  - Pagination support (limit/offset)

#### 2. Enhanced Data Models
- Added `UserStatistics` schema for statistics response
- Added `VideoHistory` schema for history response
- Updated video upload endpoint to automatically associate videos with authenticated users

#### 3. Authentication Integration
- All statistics endpoints require bearer token authentication
- Videos uploaded by authenticated users are automatically linked to their account
- Anonymous uploads still supported for non-authenticated users

### Frontend (Next.js/React)

#### 1. Dashboard Page (`/dashboard`)
Features:
- **Overview Cards**: Key metrics displayed prominently
  - Shooting percentage with makes/misses breakdown
  - Total practice sessions
  - Total practice time (formatted as hours/minutes)
  - Average shots per session
- **Performance Metrics**:
  - Best session percentage
  - Recent performance trend indicator
  - Shot breakdown (makes vs misses)
- **Visual Progress Bar**: Interactive visualization of shooting accuracy
- **Navigation**: Quick links to history and upload pages
- **Empty State**: Helpful prompt for new users

#### 2. History Page (`/history`)
Features:
- **Session List**: Chronological list of all practice sessions
- **Per-Session Stats**:
  - Date and time of session
  - Video duration
  - Number of shots detected
  - Shooting percentage with color coding
  - Makes and misses breakdown
  - Visual progress bar for each session
- **Color-Coded Performance**:
  - Green: 70%+ accuracy
  - Yellow: 50-69% accuracy
  - Red: Below 50% accuracy
- **Empty State**: Encourages users to upload their first video

#### 3. Enhanced Home Page (`/`)
- Navigation bar for authenticated users
- Quick access to dashboard and history
- User info and logout button
- Prompt for unauthenticated users to sign up/login

#### 4. Updated API Client
- Added `getUserStatistics()` function
- Added `getUserHistory()` function
- Updated `uploadVideo()` to include authentication token
- Proper TypeScript interfaces for all data types

## Technical Details

### Backend Architecture
```
Server/app/
├── routes/
│   ├── statistics.py  (NEW)
│   └── videos.py      (UPDATED)
├── schemas.py         (UPDATED)
└── main.py           (UPDATED)
```

### Frontend Architecture
```
client/
├── app/
│   ├── dashboard/
│   │   └── page.tsx   (NEW)
│   ├── history/
│   │   └── page.tsx   (NEW)
│   └── page.tsx       (UPDATED)
└── lib/
    └── api.ts         (UPDATED)
```

### Database Queries
- Efficient SQL queries using SQLAlchemy ORM
- Aggregation functions for statistics calculation
- Trend analysis based on last 10 sessions
- Optimized joins for fetching related data

## Usage

### For Users
1. **Sign up/Login** to start tracking progress
2. **Upload videos** - they will automatically be associated with your account
3. **View Dashboard** - See comprehensive statistics at a glance
4. **Check History** - Review individual session performance
5. **Track Progress** - Monitor shooting percentage trends over time

### API Examples

#### Get User Statistics
```bash
curl -X GET "http://localhost:8000/statistics/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Get User History
```bash
curl -X GET "http://localhost:8000/statistics/history?limit=20&offset=0" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Future Enhancements
- Advanced filtering and sorting in history page
- Date range selection for statistics
- Detailed shot-by-shot breakdown
- Export statistics to CSV/PDF
- Performance graphs and charts
- Comparison with previous periods
- Goal setting and achievement tracking
- Social features (compare with friends)

## Installation

### Backend
No additional dependencies required. The statistics feature uses existing packages.

### Frontend
No additional dependencies required. All features use existing Next.js and React capabilities.

## Testing

### Manual Testing Checklist
- [ ] User can view statistics after uploading videos
- [ ] All statistics calculate correctly
- [ ] History page displays all user videos
- [ ] Shooting percentages are accurate
- [ ] Trend analysis works correctly
- [ ] Authentication is properly enforced
- [ ] Empty states display for new users
- [ ] Navigation between pages works smoothly
- [ ] Logout clears user data properly
- [ ] Unauthenticated users see prompts to login

## Notes
- Statistics are calculated in real-time from the database
- No data is cached - always shows current state
- Trend analysis requires at least 6 completed sessions
- Anonymous uploads don't contribute to user statistics
- All times are displayed in user's local timezone
