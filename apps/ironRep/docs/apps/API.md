# API Documentation

## Base URL
```
Development: http://localhost:8000
Production: https://api.ironrep.com
```

## Authentication

All API requests require authentication using JWT tokens in the Authorization header:

```http
Authorization: Bearer <token>
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "success": true,
  "token": "eyJhbGc...",
  "user": {
    "id": "1",
    "email": "user@example.com",
    "name": "User Name"
  }
}
```

### Register
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "User Name"
}
```

## Workouts

### Get Today's Workout
```http
GET /api/workouts/today
Authorization: Bearer <token>
```

**Response**:
```json
{
  "success": true,
  "workout": {
    "id": "1",
    "date": "2025-11-25",
    "phase": "Phase 1",
    "warm_up": [...],
    "technical_work": [...],
    "conditioning": [...],
    "cool_down": [...]
  }
}
```

### Complete Workout
```http
POST /api/workouts/{id}/complete
Authorization: Bearer <token>
Content-Type: application/json

{
  "completed_exercises": ["Exercise 1", "Exercise 2"],
  "total_duration_minutes": 45,
  "notes": "Great session!"
}
```

## Pain Assessment

### Submit Assessment
```http
POST /api/pain/assess
Authorization: Bearer <token>
Content-Type: application/json

{
  "pain_level": 5,
  "location": "lower_back",
  "notes": "Slight discomfort"
}
```

### Get Pain History
```http
GET /api/pain/history?days=30
Authorization: Bearer <token>
```

## AI Chat

### Start Conversation
```http
POST /api/chat/start
Authorization: Bearer <token>
Content-Type: application/json

{
  "mode": "workout"
}
```

### Send Message
```http
POST /api/chat/message
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_id": "session_123",
  "message": "I need help with my workout"
}
```

## Progress

### Get Dashboard
```http
GET /api/progress/dashboard
Authorization: Bearer <token>
```

**Response**:
```json
{
  "success": true,
  "recent_workouts": [...],
  "recent_pain": [...],
  "kpis": {
    "workouts_completed": 15,
    "avg_pain_level": 3.5,
    "streak_days": 7
  }
}
```

## Error Responses

All errors follow this format:

```json
{
  "success": false,
  "message": "Error description",
  "detail": "Additional details"
}
```

### Status Codes
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Rate Limiting

- 100 requests per minute per user
- 1000 requests per hour per user

Exceeded limits return `429 Too Many Requests`.

## Webhooks (Future)

Documentation coming soon.

---

For interactive API documentation, visit: http://localhost:8000/docs
