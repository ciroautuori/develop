# 📚 StudioCentOS - Complete Documentation

**Version**: 2.0.0
**Last Updated**: December 10, 2025
**Author**: Ciro Autuori

---

## 📋 Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture](#2-architecture)
3. [Backend API Reference](#3-backend-api-reference)
4. [AI Microservice](#4-ai-microservice)
5. [Frontend Dashboard](#5-frontend-dashboard)
6. [Landing Page](#6-landing-page)
7. [Infrastructure](#7-infrastructure)
8. [Configuration](#8-configuration)
9. [Deployment](#9-deployment)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. System Overview

### 1.1 What is StudioCentOS?

StudioCentOS is an enterprise-grade, AI-powered full-stack platform consisting of:

| Component | Technology | Port | Description |
|-----------|------------|------|-------------|
| **Backend** | FastAPI + SQLAlchemy | 8002 | Business logic, APIs, Database |
| **AI Microservice** | FastAPI + LLM Agents | 8001 | AI processing, Content generation |
| **Frontend** | React + TypeScript | 3000 | Admin dashboard + Landing page |
| **PostgreSQL** | v16 | 5432 | Primary database |
| **Redis** | v7 | 6379 | Cache and job queue |

### 1.2 Project Statistics

```
Total Lines of Code: 152,310+
├── Backend:        79,610 lines (341 Python files)
├── AI Microservice: 30,361 lines (71 Python files)
└── Frontend:       42,339 lines (139 TSX files)

Business Domains: 21
AI Marketing Agents: 9
Backend Routers: 42
Admin Components: 20+
Landing Sections: 16
```

---

## 2. Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                 │
│  ┌──────────────────┐  ┌────────────────────────────────────┐  │
│  │  Landing Page    │  │       Admin Dashboard              │  │
│  │  (Public)        │  │  (Authenticated Users)             │  │
│  └────────┬─────────┘  └─────────────────┬──────────────────┘  │
└───────────┼──────────────────────────────┼──────────────────────┘
            │                              │
            └──────────────┬───────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TRAEFIK GATEWAY                              │
│  • SSL/TLS Termination    • Rate Limiting                      │
│  • Load Balancing         • CORS Headers                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
         ┌──────────────────┴──────────────────┐
         ▼                                     ▼
┌─────────────────────┐            ┌─────────────────────┐
│  BACKEND (:8002)    │◄──HTTP────►│ AI SERVICE (:8001)  │
│                     │            │                     │
│  💪 Business Logic  │            │  🧠 AI Processing   │
│  • 21 Domains       │            │  • 9 Agents         │
│  • 42 Routers       │            │  • LLM/Image/Video  │
│  • Auth/Billing     │            │  • Real APIs        │
│  • Database ORM     │            │  • Stateless        │
└─────────┬───────────┘            └─────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ PostgreSQL   │  │    Redis     │  │  ChromaDB    │          │
│  │ (Primary DB) │  │ (Cache/Queue)│  │ (Vectors)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Domain-Driven Design

The system follows DDD principles with clear separation:

**AI Microservice (Brain)**
- Generates content, images, videos
- Analyzes data, enriches leads
- Makes AI-powered decisions
- Stateless, horizontally scalable

**Backend (Arms)**
- Persists data to database
- Handles authentication/authorization
- Manages business workflows
- Exposes REST APIs

### 2.3 Backend Domains

| Domain | Files | Purpose |
|--------|-------|---------|
| `auth/` | 12 | OAuth2, JWT, MFA, Sessions |
| `marketing/` | 24 | Calendar, Leads, Email, A/B Testing, Analytics |
| `social/` | 6 | Multi-platform publishing |
| `analytics/` | 4 | GA4, Dashboard KPIs |
| `finance/` | 5 | Invoices, Stripe |
| `booking/` | 5 | Google Calendar integration |
| `support/` | 7 | AI Chatbot, Tickets |
| `customers/` | 4 | CRM features |
| `portfolio/` | 8 | Projects, Services, Uploads |
| `toolai/` | 6 | Daily AI tools discovery |
| `google/` | 3 | GMB, GA4, Places |
| `heygen/` | 3 | AI avatar videos |
| `seo/` | 2 | Sitemap, Robots.txt |
| `notifications/` | 4 | WebSocket, Push |
| `copilot/` | 2 | AI assistant proxy |
| `quotes/` | 4 | Quote management |
| `admin/` | 3 | Admin inbox |
| `imodels/` | 2 | Model management |

---

## 3. Backend API Reference

### 3.1 Authentication APIs

**Base Path**: `/api/v1/auth`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/register` | POST | User registration |
| `/login` | POST | JWT login |
| `/refresh` | POST | Refresh token |
| `/logout` | POST | Invalidate session |
| `/me` | GET | Current user info |
| `/oauth/google` | GET | Google OAuth |
| `/oauth/linkedin` | GET | LinkedIn OAuth |
| `/mfa/enable` | POST | Enable MFA |
| `/mfa/verify` | POST | Verify MFA code |

### 3.2 Marketing APIs

**Base Path**: `/api/v1/marketing`

| Router | Endpoints | Description |
|--------|-----------|-------------|
| **Calendar** | `/calendar/*` | Editorial calendar management |
| **Leads** | `/leads/*` | Lead CRUD operations |
| **Lead Enrichment** | `/enrichment/*` | Google Places + AI scoring |
| **Email** | `/email/*` | Email campaigns |
| **Brand DNA** | `/brand-dna/*` | Brand identity settings |
| **Scheduler** | `/scheduler/*` | Content scheduling |
| **A/B Testing** | `/ab-tests/*` | A/B test management |
| **Analytics** | `/analytics/*` | Marketing analytics dashboard |
| **Competitors** | `/competitors/*` | Competitor monitoring |
| **Webhooks** | `/webhooks/*` | Integration webhooks |
| **Workflows** | `/workflows/*` | Automation workflows |

#### 3.2.1 A/B Testing API

```
GET    /api/v1/marketing/ab-tests/          # List all tests
POST   /api/v1/marketing/ab-tests/          # Create new test
GET    /api/v1/marketing/ab-tests/{id}      # Get test details
PUT    /api/v1/marketing/ab-tests/{id}      # Update test
DELETE /api/v1/marketing/ab-tests/{id}      # Delete test
POST   /api/v1/marketing/ab-tests/{id}/start  # Start test
POST   /api/v1/marketing/ab-tests/{id}/stop   # Stop test
GET    /api/v1/marketing/ab-tests/{id}/results  # Get results
```

#### 3.2.2 Marketing Analytics API

```
GET    /api/v1/marketing/analytics/dashboard    # Full dashboard data
GET    /api/v1/marketing/analytics/kpis         # Key metrics
GET    /api/v1/marketing/analytics/trends       # Trend analysis
POST   /api/v1/marketing/analytics/report       # Generate PDF report
GET    /api/v1/marketing/analytics/export       # Export CSV/Excel
```

#### 3.2.3 Workflow API

```
GET    /api/v1/marketing/workflows/         # List workflows
POST   /api/v1/marketing/workflows/         # Create workflow
GET    /api/v1/marketing/workflows/{id}     # Get workflow
PUT    /api/v1/marketing/workflows/{id}     # Update workflow
DELETE /api/v1/marketing/workflows/{id}     # Delete workflow
POST   /api/v1/marketing/workflows/{id}/execute  # Execute workflow
GET    /api/v1/marketing/workflows/templates     # Get templates
```

### 3.3 Social APIs

**Base Path**: `/api/v1/social`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/publish` | POST | Publish to single platform |
| `/publish/multi` | POST | Publish to multiple platforms |
| `/schedule` | POST | Schedule post |
| `/posts` | GET | List published posts |
| `/posts/{id}` | GET | Get post details |
| `/platforms` | GET | Connected platforms |
| `/insights` | GET | Platform insights |

### 3.4 Analytics APIs

**Base Path**: `/api/v1/analytics`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/dashboard` | GET | KPI dashboard |
| `/ga4/report` | GET | GA4 report |
| `/events` | POST | Track custom event |

### 3.5 Other Domain APIs

| Domain | Base Path | Key Endpoints |
|--------|-----------|---------------|
| Finance | `/api/v1/finance` | `/invoices`, `/payments`, `/stripe` |
| Booking | `/api/v1/booking` | `/appointments`, `/slots`, `/calendar` |
| Support | `/api/v1/support` | `/tickets`, `/chat` |
| Portfolio | `/api/v1/portfolio` | `/projects`, `/services` |
| ToolAI | `/api/v1/toolai` | `/tools`, `/posts` |
| HeyGen | `/api/v1/heygen` | `/videos`, `/avatars` |

---

## 4. AI Microservice

### 4.1 Marketing Agents

| Agent | File | Lines | Description |
|-------|------|-------|-------------|
| **ContentCreator** | `content_creator.py` | 2,693 | Multi-format content generation |
| **SEOSpecialist** | `seo_specialist.py` | 1,502 | SEO analysis and optimization |
| **CampaignManager** | `campaign_manager.py` | 1,332 | Campaign orchestration |
| **EmailMarketing** | `email_marketing.py` | 1,229 | Email campaigns |
| **SocialMediaManager** | `social_media_manager.py` | 1,113 | Social publishing |
| **ImageGenerator** | `image_generator_agent.py` | 687 | AI image generation |
| **ImageBranding** | `image_branding.py` | 635 | Brand overlays |
| **LeadIntelligence** | `lead_intelligence_agent.py` | 398 | Lead enrichment |

### 4.2 Content Creator Agent

The most powerful agent with 9 POST_TYPE_PROMPTS:

```python
POST_TYPES = {
    "educational": "Educational content with tips and insights",
    "promotional": "Promotional content for products/services",
    "engagement": "Engagement-focused content (polls, questions)",
    "storytelling": "Brand storytelling and behind-the-scenes",
    "announcement": "News and announcements",
    "tips": "Quick tips and how-to content",
    "testimonial": "Customer testimonials and case studies",
    "seasonal": "Seasonal and holiday content",
    "trending": "Trending topics and current events"
}
```

**API Endpoints**:
```
POST /api/v1/copilot/content/generate     # Generate content
POST /api/v1/copilot/content/batch        # Batch generation
POST /api/v1/copilot/image/generate       # Generate image
POST /api/v1/copilot/video/generate       # Generate video
```

### 4.3 AI Infrastructure

#### LLM Providers (Priority Order)

1. **GROQ** (Primary) - llama-3.3-70b-versatile
2. **HuggingFace** - Open models
3. **Gemini** - Google AI
4. **OpenRouter** - Multiple models
5. **Ollama** - Local models

#### Image Providers (Priority Order)

1. **NanoBananaPRO** - Imagen 4 Ultra (requires special access)
2. **Pollinations** - FREE, no API key needed
3. **HuggingFace** - Stable Diffusion

#### Video Providers

1. **HeyGen** - AI avatar videos
2. **Veo 3.1** - Google video generation (requires access)

### 4.4 API Usage Examples

**Generate Content**:
```bash
curl -X POST http://localhost:8001/api/v1/copilot/content/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI in business",
    "platform": "instagram",
    "post_type": "educational",
    "tone": "professional",
    "language": "it"
  }'
```

**Generate Image**:
```bash
curl -X POST http://localhost:8001/api/v1/copilot/image/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Modern office with AI robots",
    "style": "photorealistic",
    "aspect_ratio": "1:1"
  }'
```

---

## 5. Frontend Dashboard

### 5.1 Admin Pages

| Page | File | Description |
|------|------|-------------|
| Dashboard | `Dashboard.tsx` | Main overview |
| AI Marketing | `AIMarketing/` | Marketing hub |
| Analytics | `Analytics.tsx` | Analytics overview |
| Analytics GA4 | `AnalyticsGA4.tsx` | Google Analytics |
| Analytics SEO | `AnalyticsSEO.tsx` | SEO metrics |
| Finance Hub | `FinanceHub.tsx` | Financial management |
| Business Hub | `BusinessHub.tsx` | Business overview |
| Portfolio Hub | `PortfolioHub.tsx` | Portfolio management |
| Portfolio List | `PortfolioList.tsx` | Projects list |
| Project Form | `ProjectForm.tsx` | Edit project |
| Service Form | `ServiceForm.tsx` | Edit service |
| Calendar View | `CalendarView.tsx` | Calendar |
| Editorial Calendar | `EditorialCalendar.tsx` | Content calendar |
| Settings Hub | `SettingsHub.tsx` | Settings |
| User Management | `UserManagement.tsx` | Users admin |
| ToolAI Backoffice | `ToolAIBackoffice.tsx` | AI tools admin |
| Admin Login | `AdminLogin.tsx` | Login page |

### 5.2 AI Marketing Components

| Component | Description | Backend API |
|-----------|-------------|-------------|
| `ContentGenerator` | AI content creation | `/copilot/content/generate` |
| `ImageGenerator` | AI image creation | `/copilot/image/generate` |
| `VideoGenerator` | AI video creation | `/heygen/videos` |
| `CalendarManager` | Editorial calendar | `/marketing/calendar` |
| `SocialPublisherPro` | Multi-platform publishing | `/social/publish` |
| `EmailCampaignPro` | Email campaigns | `/marketing/email` |
| `LeadFinderInline` | Lead discovery | `/marketing/enrichment` |
| `BusinessDNAGenerator` | Brand identity | `/marketing/brand-dna` |
| `MarketingAnalyticsPro` | Marketing KPIs | `/marketing/analytics/dashboard` |
| `ABTestingManager` | A/B testing | `/marketing/ab-tests` |
| `CompetitorMonitor` | Competitor tracking | `/marketing/competitors` |
| `WebhookManager` | Webhooks | `/marketing/webhooks` |
| `WorkflowBuilder` | Automation | `/marketing/workflows` |
| `ContentStudio` | Content studio | `/copilot/content` |
| `ConversionDashboard` | Conversions | `/marketing/analytics` |
| `KnowledgeBaseManager` | RAG knowledge | `/rag/knowledge` |
| `ChatInterface` | AI chatbot | `/support/chat` |
| `BatchContentModal` | Bulk generation | `/copilot/content/batch` |
| `VideoStoryCreator` | Story creation | `/copilot/video` |

### 5.3 State Management

Using **Zustand** for state management:

```typescript
// Example store
import { create } from 'zustand';

interface MarketingStore {
  leads: Lead[];
  posts: Post[];
  fetchLeads: () => Promise<void>;
  createPost: (post: CreatePostDTO) => Promise<void>;
}

export const useMarketingStore = create<MarketingStore>((set) => ({
  leads: [],
  posts: [],
  fetchLeads: async () => {
    const leads = await api.getLeads();
    set({ leads });
  },
  createPost: async (post) => {
    const newPost = await api.createPost(post);
    set((state) => ({ posts: [...state.posts, newPost] }));
  },
}));
```

---

## 6. Landing Page

### 6.1 Sections

| Section | Component | Description |
|---------|-----------|-------------|
| Hero | `HeroSection.tsx` | Animated hero with CTA |
| Services | `ServicesSection.tsx` | Services showcase |
| Portfolio | `PortfolioSection.tsx` | Projects gallery |
| Process | `ProcessSection.tsx` | Work process |
| Booking | `BookingSection.tsx` | Appointment booking |
| Booking Timeline | `BookingTimeline.tsx` | Booking flow |
| Contact | `ContactSection.tsx` | Contact form |
| ToolAI | `ToolAISection.tsx` | AI tools discovery |
| Case Studies | `CaseStudiesSection.tsx` | Success stories |
| Story | `StorySection.tsx` | Brand story |
| Header | `LandingHeader.tsx` | Navigation |
| Footer | `LandingFooter.tsx` | Footer |
| Cookie Banner | `CookieBanner.tsx` | GDPR consent |
| Project Card | `ProjectCard.tsx` | Project display |
| Service Card | `ServiceCard.tsx` | Service display |
| Contact Form | `ContactForm.tsx` | Form component |

### 6.2 i18n Support

The landing page supports internationalization:

```
src/features/landing/i18n/
├── en.json
├── it.json
└── index.ts
```

---

## 7. Infrastructure

### 7.1 Database (PostgreSQL 16)

**Key Tables**:
- `users` - User accounts
- `profiles` - User profiles
- `subscriptions` - Billing subscriptions
- `leads` - Marketing leads
- `posts` - Social media posts
- `campaigns` - Marketing campaigns
- `appointments` - Booking appointments
- `projects` - Portfolio projects
- `services` - Portfolio services
- `support_tickets` - Support tickets
- `toolai_posts` - AI tools posts

### 7.2 Cache (Redis 7)

**Usage**:
- Session storage
- API response caching
- Rate limiting counters
- Job queue (background tasks)
- Real-time pub/sub

### 7.3 Scheduler (APScheduler)

**Scheduled Jobs**:

| Job | Schedule | Description |
|-----|----------|-------------|
| ToolAI Discovery | 08:30 CET | Daily AI tools discovery |
| Marketing Content | 06:00 CET | Daily content generation |
| Post Publishing | Every 5 min | Check scheduled posts |
| Metrics Update | Hourly | Update analytics metrics |

### 7.4 Email Infrastructure

**Providers**:
1. **SendGrid** (Primary)
2. **Mailgun** (Fallback)
3. **SMTP** (Fallback)

**Features**:
- Transactional emails
- Marketing campaigns
- Template rendering
- Tracking (opens, clicks)

### 7.5 Social Infrastructure

**Platforms**:
| Platform | API | Features |
|----------|-----|----------|
| Facebook | Graph API | Publishing, Insights |
| Instagram | Graph API | Publishing, Stories |
| LinkedIn | Marketing API | Publishing, Analytics |
| Twitter/X | API v2 | Publishing |

---

## 8. Configuration

### 8.1 Environment Variables

**Backend** (`.env.production`):
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/studiocentos
REDIS_URL=redis://localhost:6379

# Auth
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256

# AI
GROQ_API_KEY=your-groq-key
HUGGINGFACE_TOKEN=your-hf-token
GOOGLE_API_KEY=your-google-key

# Email
SENDGRID_API_KEY=your-sendgrid-key

# Social
META_ACCESS_TOKEN=your-meta-token
LINKEDIN_ACCESS_TOKEN=your-linkedin-token

# Analytics
GA4_PROPERTY_ID=your-property-id
```

**AI Microservice** (`.env`):
```bash
# LLM
GROQ_API_KEY=your-groq-key
GROQ_MODEL=llama-3.3-70b-versatile

# Image
POLLINATIONS_ENABLED=true
NANOBANANA_API_KEY=optional

# Video
HEYGEN_API_KEY=your-heygen-key
```

### 8.2 Docker Configuration

**docker-compose.production.yml**:
```yaml
services:
  backend:
    image: studiocentos/backend:latest
    ports:
      - "8002:8000"
    depends_on:
      - db
      - cache

  ai_microservice:
    image: studiocentos/ai:latest
    ports:
      - "8001:8000"

  frontend:
    image: studiocentos/frontend:latest
    ports:
      - "3000:80"

  db:
    image: postgres:16
    volumes:
      - pgdata:/var/lib/postgresql/data

  cache:
    image: redis:7-alpine
    volumes:
      - redisdata:/data
```

---

## 9. Deployment

### 9.1 Docker Deployment

```bash
# Build all images
cd config/docker
docker compose -f docker-compose.production.yml build

# Start services
docker compose -f docker-compose.production.yml up -d

# Check logs
docker compose -f docker-compose.production.yml logs -f

# Scale AI service
docker compose -f docker-compose.production.yml up -d --scale ai_microservice=3
```

### 9.2 Database Migrations

```bash
# Run migrations
cd apps/backend
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "add new table"

# Rollback
alembic downgrade -1
```

### 9.3 SSL/TLS with Traefik

Traefik automatically handles SSL certificates via Let's Encrypt.

```yaml
# traefik.yml
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@studiocentos.it
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web
```

---

## 10. Troubleshooting

### 10.1 Common Issues

**Issue**: Backend returns 502 Bad Gateway
```bash
# Check backend logs
docker logs studiocentos-backend

# Restart backend
docker compose -f docker-compose.production.yml restart backend
```

**Issue**: AI Microservice timeout
```bash
# Increase timeout in .env
AI_REQUEST_TIMEOUT=120

# Check GROQ API status
curl https://api.groq.com/health
```

**Issue**: Database connection failed
```bash
# Check PostgreSQL
docker exec -it studiocentos-db psql -U postgres -c "SELECT 1"

# Check connection string
echo $DATABASE_URL
```

**Issue**: Redis connection refused
```bash
# Check Redis
docker exec -it studiocentos-cache redis-cli ping

# Should return PONG
```

### 10.2 Performance Optimization

**Database**:
- Enable connection pooling
- Add indexes on frequently queried columns
- Use `EXPLAIN ANALYZE` for slow queries

**API**:
- Enable response caching with Redis
- Use pagination for large datasets
- Implement rate limiting

**Frontend**:
- Enable code splitting
- Use lazy loading for images
- Enable gzip compression

### 10.3 Logs Location

| Service | Log Location |
|---------|--------------|
| Backend | `apps/backend/logs/` |
| AI Service | Docker stdout |
| Nginx | `/var/log/nginx/` |
| PostgreSQL | Docker stdout |

---

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/ciroautuori/studiocentos/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ciroautuori/studiocentos/discussions)
- **Email**: info@studiocentos.it

---

<p align="center">
  <strong>Made with ❤️ in Italy by Ciro Autuori</strong>
</p>
