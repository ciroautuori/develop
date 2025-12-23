# 📅 Booking System - StudiocentOS

**Last Updated**: November 5, 2025  
**Status**: ✅ Production Ready  
**Version**: 1.0.0

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [API Endpoints](#api-endpoints)
5. [Database Models](#database-models)
6. [Integrations](#integrations)
7. [Usage Examples](#usage-examples)
8. [Configuration](#configuration)

---

## 🎯 Overview

The Booking System provides a complete appointment scheduling solution with:
- **Calendar availability** management
- **Videocall integration** (Google Meet, Zoom, Teams)
- **Email notifications** (confirmations, reminders)
- **Multi-timezone** support
- **Service types** (consultation, demo, support, training)

---

## ✨ Features

### 1. Calendar Availability

- ✅ Configurable time slots per day/hour
- ✅ Customizable duration (15-180 minutes)
- ✅ Multiple service types
- ✅ Block dates (holidays, vacations)
- ✅ Timezone support

### 2. Videocall Integration

- ✅ **Google Meet** - Full OAuth2 integration
- ✅ **Zoom** - Meeting creation & management
- ✅ **Microsoft Teams** - Ready for integration
- ✅ **Whereby** - Ready for integration
- ✅ **Jitsi** - Ready for integration

### 3. Booking Management

- ✅ Create appointments
- ✅ Automatic confirmation
- ✅ Cancellation with reason
- ✅ Follow-up messages
- ✅ 24h reminder emails

### 4. Email Notifications

- ✅ Booking confirmation
- ✅ Calendar invite (.ics file)
- ✅ Automatic reminders
- ✅ Cancellation notices
- ✅ Follow-up emails

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Booking System                         │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Calendar   │  │   Booking    │  │ Videocall    │
│  Management  │  │  Management  │  │ Integration  │
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ▼
                  ┌──────────────┐
                  │    Email     │
                  │ Notifications│
                  └──────────────┘
```

### File Structure

```
apps/backend/app/domain/booking/
├── __init__.py
├── models.py          # Database models
├── schemas.py         # Pydantic schemas
├── routers.py         # API endpoints
└── services.py        # Business logic & integrations
```

---

## 📡 API Endpoints

### Public Endpoints

#### Get Available Slots

```http
POST /api/v1/booking/calendar/availability
Content-Type: application/json

{
  "start_date": "2025-11-05",
  "end_date": "2025-11-12",
  "service_type": "consultation",
  "timezone": "Europe/Rome"
}
```

**Response**: 200 OK
```json
{
  "availability": [
    {
      "date": "2025-11-05",
      "slots": [
        {
          "datetime": "2025-11-05T09:00:00",
          "duration_minutes": 30,
          "service_type": "consultation",
          "available": true
        }
      ],
      "total_available": 12
    }
  ],
  "blocked_dates": ["2025-11-11"],
  "bookings_count": 3
}
```

#### Create Booking

```http
POST /api/v1/booking/bookings
Content-Type: application/json

{
  "client_name": "Mario Rossi",
  "client_email": "mario@example.com",
  "client_phone": "+39 123 456 7890",
  "client_company": "Acme Inc",
  "service_type": "consultation",
  "title": "Consulenza StudiocentOS Framework",
  "description": "Vorrei discutere l'integrazione",
  "scheduled_at": "2025-11-05T09:00:00",
  "duration_minutes": 30,
  "timezone": "Europe/Rome",
  "meeting_provider": "google_meet",
  "client_notes": "Preferisco Google Meet"
}
```

**Response**: 201 Created
```json
{
  "id": 1,
  "client_name": "Mario Rossi",
  "client_email": "mario@example.com",
  "service_type": "consultation",
  "title": "Consulenza StudiocentOS Framework",
  "scheduled_at": "2025-11-05T09:00:00",
  "duration_minutes": 30,
  "status": "pending",
  "meeting_provider": "google_meet",
  "meeting_url": "https://meet.google.com/abc-defg-hij",
  "created_at": "2025-11-05T10:00:00Z"
}
```

#### Get Booking

```http
GET /api/v1/booking/bookings/{id}
```

**Response**: 200 OK
```json
{
  "id": 1,
  "client_name": "Mario Rossi",
  "client_email": "mario@example.com",
  "client_phone": "+39 123 456 7890",
  "service_type": "consultation",
  "title": "Consulenza StudiocentOS Framework",
  "scheduled_at": "2025-11-05T09:00:00",
  "duration_minutes": 30,
  "status": "confirmed",
  "meeting_provider": "google_meet",
  "meeting_url": "https://meet.google.com/abc-defg-hij",
  "meeting_id": "abc-defg-hij",
  "reminder_sent": true,
  "created_at": "2025-11-05T10:00:00Z"
}
```

#### Cancel Booking

```http
POST /api/v1/booking/bookings/{id}/cancel
Content-Type: application/json

{
  "cancellation_reason": "Cliente ha cambiato idea"
}
```

**Response**: 200 OK
```json
{
  "id": 1,
  "status": "cancelled",
  "cancellation_reason": "Cliente ha cambiato idea",
  "cancelled_at": "2025-11-05T11:00:00Z"
}
```

#### Health Check

```http
GET /api/v1/booking/health
```

**Response**: 200 OK
```json
{
  "status": "healthy",
  "service": "booking",
  "version": "1.0.0"
}
```

---

## 🗄️ Database Models

### 1. Booking

Main booking entity.

```python
class Booking(Base):
    __tablename__ = "bookings"
    
    id: int
    client_name: str
    client_email: str
    client_phone: str | None
    client_company: str | None
    service_type: str  # consultation, demo, support, training
    title: str
    description: str | None
    scheduled_at: datetime
    duration_minutes: int
    timezone: str
    status: str  # pending, confirmed, cancelled, completed
    meeting_provider: str  # google_meet, zoom, teams, whereby, jitsi
    meeting_url: str | None
    meeting_id: str | None
    reminder_sent: bool
    cancellation_reason: str | None
    client_notes: str | None
    created_at: datetime
    updated_at: datetime
```

### 2. AvailabilitySlot

Defines available time slots.

```python
class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"
    
    id: int
    day_of_week: int  # 0-6 (Monday-Sunday)
    start_time: time
    end_time: time
    slot_duration: int  # minutes
    service_type: str
    is_active: bool
    created_at: datetime
```

### 3. BlockedDate

Dates when booking is not available.

```python
class BlockedDate(Base):
    __tablename__ = "blocked_dates"
    
    id: int
    blocked_date: date
    reason: str
    description: str | None
    all_day: bool
    start_time: time | None
    end_time: time | None
    created_at: datetime
```

### 4. BookingFollowUp

Follow-up messages for bookings.

```python
class BookingFollowUp(Base):
    __tablename__ = "booking_follow_ups"
    
    id: int
    booking_id: int
    subject: str
    message: str
    sent: bool
    sent_at: datetime | None
    created_at: datetime
```

---

## 🔌 Integrations

### Google Meet

**Features**:
- OAuth2 authentication
- Calendar API integration
- Automatic meeting creation
- Email invites with calendar (.ics)
- Meeting cancellation

**Configuration**:
```bash
# .env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/integrations/google/callback
```

**Setup Steps**:
1. Create project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google Calendar API
3. Create OAuth 2.0 credentials
4. Add authorized redirect URIs
5. Copy Client ID and Secret to `.env`

### Zoom

**Features**:
- OAuth2 authentication
- Meeting creation & management
- Waiting room support
- Password protection
- Recording options

**Configuration**:
```bash
# .env
ZOOM_CLIENT_ID=your_zoom_client_id_here
ZOOM_CLIENT_SECRET=your_zoom_client_secret_here
ZOOM_REDIRECT_URI=http://localhost:8000/api/v1/integrations/zoom/callback
```

**Setup Steps**:
1. Create app in [Zoom Marketplace](https://marketplace.zoom.us/)
2. Choose OAuth app type
3. Add scopes: `meeting:write`, `meeting:read`
4. Set redirect URL
5. Copy Client ID and Secret to `.env`

### Email Notifications

**Features**:
- SendGrid API (primary)
- SMTP fallback (secondary)
- HTML templates
- Calendar invites (.ics)
- Multi-recipient support

**Configuration**:
```bash
# .env
SENDGRID_API_KEY=your_sendgrid_api_key_here
FROM_EMAIL=noreply@studiocentos.it
FROM_NAME=StudiocentOS

# SMTP Fallback
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

---

## 💡 Usage Examples

### Frontend Integration

```typescript
// Get available slots
const response = await fetch('/api/v1/booking/calendar/availability', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    start_date: '2025-11-05',
    end_date: '2025-11-12',
    service_type: 'consultation',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
  })
});

const { availability } = await response.json();

// Create booking
const booking = await fetch('/api/v1/booking/bookings', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    client_name: 'Mario Rossi',
    client_email: 'mario@example.com',
    service_type: 'consultation',
    title: 'Consulenza Framework',
    scheduled_at: '2025-11-05T09:00:00',
    duration_minutes: 30,
    timezone: 'Europe/Rome',
    meeting_provider: 'google_meet'
  })
});

const bookingData = await booking.json();
console.log('Meeting URL:', bookingData.meeting_url);
```

### Python Integration

```python
import httpx
from datetime import datetime, timedelta

# Get availability
async with httpx.AsyncClient() as client:
    response = await client.post(
        'http://localhost:8000/api/v1/booking/calendar/availability',
        json={
            'start_date': datetime.now().isoformat(),
            'end_date': (datetime.now() + timedelta(days=7)).isoformat(),
            'service_type': 'consultation',
            'timezone': 'Europe/Rome'
        }
    )
    availability = response.json()

# Create booking
async with httpx.AsyncClient() as client:
    response = await client.post(
        'http://localhost:8000/api/v1/booking/bookings',
        json={
            'client_name': 'Mario Rossi',
            'client_email': 'mario@example.com',
            'service_type': 'consultation',
            'title': 'Consulenza',
            'scheduled_at': '2025-11-05T09:00:00',
            'duration_minutes': 30,
            'timezone': 'Europe/Rome',
            'meeting_provider': 'google_meet'
        }
    )
    booking = response.json()
    print(f"Meeting URL: {booking['meeting_url']}")
```

---

## ⚙️ Configuration

### Service Types

Configure available service types in `apps/backend/app/domain/booking/schemas.py`:

```python
class ServiceType(str, Enum):
    CONSULTATION = "consultation"
    DEMO = "demo"
    SUPPORT = "support"
    TRAINING = "training"
```

### Availability Slots

Configure default availability in database:

```sql
INSERT INTO availability_slots (day_of_week, start_time, end_time, slot_duration, service_type, is_active)
VALUES
  (0, '09:00', '17:00', 30, 'consultation', true),  -- Monday
  (1, '09:00', '17:00', 30, 'consultation', true),  -- Tuesday
  (2, '09:00', '17:00', 30, 'consultation', true),  -- Wednesday
  (3, '09:00', '17:00', 30, 'consultation', true),  -- Thursday
  (4, '09:00', '17:00', 30, 'consultation', true);  -- Friday
```

### Block Dates

Block specific dates:

```sql
INSERT INTO blocked_dates (blocked_date, reason, all_day)
VALUES
  ('2025-12-25', 'Christmas', true),
  ('2025-12-26', 'Boxing Day', true),
  ('2025-01-01', 'New Year', true);
```

---

## 📚 Next Steps

- **[API Documentation](../api/booking.md)** - Complete API reference
- **[Integration Guide](../guides/api-integration.md)** - Integration examples
- **[Deployment Guide](../guides/deployment.md)** - Production deployment

---

## 🆘 Need Help?

- 📖 **[Troubleshooting](../getting-started/troubleshooting.md)**
- 🐛 **[GitHub Issues](https://github.com/yourusername/studiocentos/issues)**
- 📧 **Email**: ciro@studiocentos.it
