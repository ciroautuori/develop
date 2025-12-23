<p align="center">
  <a href="https://github.com/ciroautuori/studiocentos" target="_blank">
    <img src="https://raw.githubusercontent.com/ciroautuori/studiocentos/main/apps/frontend/public/logo/svg/light.svg" width="200" alt="StudioCentOS Logo" />
  </a>
</p>

<p align="center">
  <strong>🚀 Enterprise-Grade AI-Powered Full-Stack Framework</strong><br/>
  <em>Where Italian Craftsmanship Meets Modern Architecture</em>
</p>

<p align="center">
  <a href="https://github.com/ciroautuori/studiocentos/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python 3.12+" />
  <img src="https://img.shields.io/badge/FastAPI-0.115+-green.svg" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-18+-61DAFB.svg" alt="React 18" />
  <img src="https://img.shields.io/badge/TypeScript-5.6+-3178C6.svg" alt="TypeScript" />
  <img src="https://img.shields.io/badge/Made%20in-Italy%20🇮🇹-009246.svg" alt="Made in Italy" />
  <a href="https://github.com/ciroautuori/studiocentos/blob/main/CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome" /></a>
</p>

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Backend Python Files** | 341 |
| **AI Microservice Files** | 71 |
| **Frontend TSX Files** | 139 |
| **Total Lines of Code** | 152,310+ |
| **Backend Domains** | 21 |
| **AI Marketing Agents** | 9 |
| **Backend Routers** | 42 |
| **Admin Components** | 20+ |

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**StudioCentOS** is a production-ready, enterprise-grade platform that combines:

- **�� AI Microservice** - 9 specialized marketing agents with real API integrations
- **⚡ FastAPI Backend** - 21 business domains with DDD architecture  
- **🎨 React Admin Dashboard** - Complete backoffice with 20+ AI marketing tools
- **🌐 Landing Page** - Modern, responsive public website

### Philosophy

StudioCentOS embodies **Italian craftsmanship** in software engineering:
- **Quality over quantity**: Every file, every pattern, every decision is intentional
- **Enterprise-ready**: Built for real-world production environments
- **AI-First**: Native AI integration, not an afterthought
- **DDD Architecture**: Clean separation between AI (brain) and Backend (business logic)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐  │
│  │   Landing Page      │  │      Admin Dashboard            │  │
│  │   (Public Website)  │  │   (Backoffice AI Marketing)     │  │
│  │   React + Vite      │  │   React + TypeScript            │  │
│  └─────────────────────┘  └─────────────────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                    API GATEWAY (Traefik)                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  SSL/TLS • Rate Limiting • Load Balancing • CORS        │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
         ┌──────────────────────┴──────────────────────┐
         ▼                                             ▼
┌─────────────────────────┐              ┌─────────────────────────┐
│   BACKEND (:8002)       │              │  AI MICROSERVICE (:8001) │
│   FastAPI + SQLAlchemy  │◄────API─────►│  FastAPI + AI Agents    │
│                         │              │                         │
│   21 Business Domains:  │              │   9 Marketing Agents:   │
│   • Auth (OAuth2/JWT)   │              │   • ContentCreator      │
│   • Marketing (12 APIs) │              │   • SEOSpecialist       │
│   • Social (Multi-plat) │              │   • CampaignManager     │
│   • Analytics (GA4)     │              │   • EmailMarketing      │
│   • Finance (Invoices)  │              │   • SocialMediaManager  │
│   • Booking (Calendar)  │              │   • ImageGenerator      │
│   • Support (AI Chat)   │              │   • ImageBranding       │
│   • Customers (CRM)     │              │   • LeadIntelligence    │
│   • ToolAI (Discovery)  │              │   • VideoGenerator      │
│   • HeyGen (Avatars)    │              │                         │
│   • SEO (Sitemap)       │              │   AI Infrastructure:    │
│   • Notifications (WS)  │              │   • GROQ (llama-3.3-70b)│
│   • Portfolio           │              │   • NanoBananaPRO       │
│   • Quotes              │              │   • Pollinations (FREE) │
│   • Google (GMB/GA4)    │              │   • HuggingFace         │
│   └─────────────────────┘              │   • Gemini              │
│                                        └─────────────────────────┘
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                       DATA LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ PostgreSQL16 │  │   Redis 7    │  │  ChromaDB    │          │
│  │   Primary    │  │  Cache/Queue │  │   Vectors    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Why Two Services?

| AI Microservice | Backend |
|-----------------|---------|
| 🧠 **Brain** - Generates, analyzes, decides | 💪 **Arms** - Persists, schedules, publishes |
| Stateless, GPU-intensive | Stateful, Database-bound |
| Can scale independently | Business logic + Auth |
| LLM/Image/Video providers | REST APIs + WebSockets |

---

## ✨ Features

### 🧠 AI Marketing Suite (9 Agents)

| Agent | Description | Real APIs |
|-------|-------------|-----------|
| **ContentCreator** | Multi-format content (post, carousel, story, video) with 9 POST_TYPE_PROMPTS | GROQ llama-3.3-70b, Gemini |
| **ImageGenerator** | AI image generation with brand overlay | NanoBananaPRO (Imagen 4 Ultra), Pollinations (FREE) |
| **SEOSpecialist** | SEO analysis, keywords, meta optimization | Google Search Console API |
| **CampaignManager** | Multi-channel campaign orchestration | Meta, LinkedIn, Twitter APIs |
| **EmailMarketing** | Email campaigns with dynamic templates | SendGrid, Mailgun, SMTP |
| **SocialMediaManager** | Multi-platform publishing & scheduling | Meta Graph, LinkedIn, Twitter |
| **LeadIntelligence** | Lead enrichment, scoring, qualification | Apollo, Google Places |
| **ImageBranding** | Brand-consistent image overlays (logo, watermark) | PIL, Custom fonts |
| **VideoGenerator** | AI video content creation | HeyGen API, Veo 3.1 |

### �� Admin Dashboard (20+ Components)

| Component | Status | Description |
|-----------|--------|-------------|
| `ContentGenerator` | ✅ Active | AI content generation with 9 post types |
| `ImageGenerator` | ✅ Active | AI image creation with brand overlay |
| `VideoGenerator` | ✅ Active | AI video creation (HeyGen avatars) |
| `CalendarManager` | ✅ Active | Editorial calendar with drag-and-drop scheduling |
| `SocialPublisherPro` | ✅ Active | Multi-platform social publishing (FB, IG, LI, TW) |
| `EmailCampaignPro` | ✅ Active | Email campaign management with templates |
| `LeadFinderInline` | ✅ Active | Lead discovery via Google Places + AI scoring |
| `BusinessDNAGenerator` | ✅ Active | Brand identity configuration (colors, tone, values) |
| `MarketingAnalyticsPro` | ✅ Active | Marketing KPIs dashboard with real data |
| `ABTestingManager` | ✅ Active | A/B testing for email subjects, CTAs, landing pages |
| `CompetitorMonitor` | ✅ Active | Competitor tracking and analysis |
| `WebhookManager` | ✅ Active | Integration webhooks management |
| `WorkflowBuilder` | ✅ Active | Visual marketing automation workflows |
| `ContentStudio` | ✅ Active | Content creation studio |
| `ConversionDashboard` | ✅ Active | Conversion funnel tracking |
| `KnowledgeBaseManager` | ✅ Active | RAG knowledge base for AI context |
| `ChatInterface` | ✅ Active | AI chatbot interface |
| `BatchContentModal` | ✅ Active | Bulk content generation |
| `VideoStoryCreator` | ✅ Active | Instagram/TikTok story creator |

### 🌐 Landing Page (16 Sections)

| Section | Description |
|---------|-------------|
| `HeroSection` | Animated hero with gradient text and CTA |
| `ServicesSection` | Services showcase with cards |
| `PortfolioSection` | Projects portfolio gallery |
| `ProcessSection` | Work process timeline |
| `BookingSection` | Appointment booking integration |
| `BookingTimeline` | Visual booking flow |
| `ContactSection` | Contact form with validation |
| `ToolAISection` | Daily AI tools discovery |
| `CaseStudiesSection` | Success stories |
| `StorySection` | Brand story section |
| `LandingHeader` | Responsive navigation |
| `LandingFooter` | Footer with links |
| `CookieBanner` | GDPR cookie consent |

### ⚡ Backend APIs (42 Routers)

| Domain | Routers | Key Endpoints |
|--------|---------|---------------|
| **Auth** | 4 | OAuth2 (Google, LinkedIn), JWT, MFA, Sessions |
| **Marketing** | 12 | Calendar, Leads, Email, A/B Testing, Analytics, Workflows, Competitors, Webhooks |
| **Social** | 2 | Multi-platform publishing, Platform insights |
| **Analytics** | 2 | GA4 integration, KPI dashboard |
| **Finance** | 1 | Invoices, Payments, Stripe integration |
| **Booking** | 2 | Google Calendar sync, Appointments |
| **Support** | 1 | AI chatbot, Support tickets |
| **Customers** | 1 | CRM features |
| **Portfolio** | 3 | Projects, Services, Uploads |
| **ToolAI** | 2 | Daily AI tools discovery, RAG |
| **SEO** | 1 | Sitemap, Robots.txt generation |
| **HeyGen** | 1 | AI avatar video generation |
| **Google** | 1 | GMB, GA4, Places API |
| **Notifications** | 2 | WebSocket, Push notifications |
| **Copilot** | 1 | AI assistant proxy |

---

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended)
- **Python 3.12+** (for local development)
- **Node.js 20+** (for frontend)

### 🐳 Docker Installation

```bash
# 1. Clone the repository
git clone https://github.com/ciroautuori/studiocentos.git
cd studiocentos

# 2. Navigate to Docker config
cd config/docker

# 3. Copy environment file
cp .env.example .env.production
# Edit .env.production with your API keys

# 4. Start all services
docker compose -f docker-compose.production.yml up -d

# ✅ Services:
# • Backend API     → http://localhost:8002
# • AI Microservice → http://localhost:8001
# • Frontend        → http://localhost:3000
# • PostgreSQL      → localhost:5432
# • Redis           → localhost:6379
```

### 🔑 Required API Keys

See [API Keys Setup Guide](docs/guides/API_KEYS_SETUP_GUIDE.md) for detailed instructions.

| Service | Required For | Priority | Get Key |
|---------|--------------|----------|---------|
| **GROQ** | LLM (llama-3.3-70b) | 🔥 Critical | [console.groq.com](https://console.groq.com) |
| **SendGrid** | Email campaigns | 🔥 Critical | [sendgrid.com](https://sendgrid.com) |
| **Pollinations** | Image generation | ✅ FREE | No key needed! |
| **Meta** | Facebook/Instagram | ⭐ High | [developers.facebook.com](https://developers.facebook.com) |
| **LinkedIn** | LinkedIn publishing | ⭐ High | [linkedin.com/developers](https://linkedin.com/developers) |
| **Google** | GA4, GMB, Places | ⭐ High | [console.cloud.google.com](https://console.cloud.google.com) |
| **Apollo** | Lead enrichment | ⭐ High | [apollo.io](https://apollo.io) |
| **HeyGen** | AI avatar videos | ⏳ Optional | [heygen.com](https://heygen.com) |
| **NanoBananaPRO** | Imagen 4 Ultra | ⏳ Optional | Special access required |

### Verify Installation

```bash
# Check health endpoints
curl http://localhost:8001/health  # AI Microservice
curl http://localhost:8002/health  # Backend

# Check running containers
docker ps
```

---

## 📁 Project Structure

```
studiocentos/
├── apps/
│   ├── backend/                    # FastAPI Backend (341 files, 79K+ lines)
│   │   ├── app/
│   │   │   ├── core/              # Config, Security, Database
│   │   │   ├── domain/            # 21 Business Domains
│   │   │   │   ├── auth/          # OAuth2, JWT, Sessions, MFA
│   │   │   │   ├── marketing/     # 12 marketing routers
│   │   │   │   │   ├── calendar_router.py
│   │   │   │   │   ├── leads_router.py
│   │   │   │   │   ├── lead_enrichment_router.py
│   │   │   │   │   ├── email_router.py
│   │   │   │   │   ├── brand_dna_router.py
│   │   │   │   │   ├── scheduler_router.py
│   │   │   │   │   ├── ab_testing_router.py
│   │   │   │   │   ├── analytics_router.py
│   │   │   │   │   ├── competitor_router.py
│   │   │   │   │   ├── webhook_router.py
│   │   │   │   │   └── workflow_router.py
│   │   │   │   ├── social/        # Multi-platform publishing
│   │   │   │   ├── analytics/     # GA4, KPIs
│   │   │   │   ├── finance/       # Invoices, Stripe
│   │   │   │   ├── booking/       # Google Calendar
│   │   │   │   ├── support/       # AI Chatbot, Tickets
│   │   │   │   ├── customers/     # CRM
│   │   │   │   ├── portfolio/     # Projects, Services
│   │   │   │   ├── toolai/        # Daily AI tools
│   │   │   │   ├── google/        # GMB, GA4
│   │   │   │   ├── heygen/        # AI Avatars
│   │   │   │   ├── seo/           # Sitemap
│   │   │   │   └── notifications/ # WebSocket
│   │   │   └── infrastructure/    # DB, Cache, Email, Security
│   │   ├── alembic/               # Database migrations
│   │   └── tests/                 # Pytest tests
│   │
│   ├── ai_microservice/            # AI Agents (71 files, 30K+ lines)
│   │   ├── app/
│   │   │   ├── domain/
│   │   │   │   ├── marketing/     # 9 AI Marketing Agents
│   │   │   │   │   ├── content_creator.py      # 2,693 lines
│   │   │   │   │   ├── seo_specialist.py       # 1,502 lines
│   │   │   │   │   ├── campaign_manager.py     # 1,332 lines
│   │   │   │   │   ├── email_marketing.py      # 1,229 lines
│   │   │   │   │   ├── social_media_manager.py # 1,113 lines
│   │   │   │   │   ├── image_generator_agent.py
│   │   │   │   │   ├── image_branding.py
│   │   │   │   │   └── lead_intelligence_agent.py
│   │   │   │   ├── support/       # AI Chatbot
│   │   │   │   ├── toolai/        # AI Discovery
│   │   │   │   └── rag/           # RAG Pipeline
│   │   │   └── infrastructure/    
│   │   │       ├── agents/        # Base agent framework
│   │   │       ├── email/         # SendGrid client
│   │   │       ├── google/        # GSC, GA4, Places
│   │   │       ├── leads/         # Apollo client
│   │   │       └── social/        # Meta, LinkedIn, Twitter clients
│   │   └── tests/
│   │
│   └── frontend/                   # React Admin + Landing (139 files, 42K+ lines)
│       ├── src/
│       │   ├── features/
│       │   │   ├── admin/         # Dashboard + AI Marketing
│       │   │   │   ├── pages/
│       │   │   │   │   ├── AIMarketing/  # 20+ components
│       │   │   │   │   │   ├── components/
│       │   │   │   │   │   │   ├── ContentGenerator.tsx
│       │   │   │   │   │   │   ├── ImageGenerator.tsx
│       │   │   │   │   │   │   ├── VideoGenerator.tsx
│       │   │   │   │   │   │   ├── CalendarManager.tsx
│       │   │   │   │   │   │   ├── SocialPublisherPro.tsx
│       │   │   │   │   │   │   ├── LeadFinderInline.tsx
│       │   │   │   │   │   │   ├── MarketingAnalyticsPro.tsx
│       │   │   │   │   │   │   ├── ABTestingManager.tsx
│       │   │   │   │   │   │   ├── WorkflowBuilder.tsx
│       │   │   │   │   │   │   └── ...
│       │   │   │   │   ├── Dashboard.tsx
│       │   │   │   │   ├── Analytics.tsx
│       │   │   │   │   ├── FinanceHub.tsx
│       │   │   │   │   └── ...
│       │   │   │   └── components/
│       │   │   ├── landing/       # Public website
│       │   │   │   ├── components/  # 16 sections
│       │   │   │   └── pages/
│       │   │   └── support/       # Support chat
│       │   ├── components/        # Shared UI components
│       │   └── services/          # API services
│       └── public/                # Static assets
│
├── config/
│   ├── docker/                    # Docker configurations
│   │   ├── docker-compose.production.yml
│   │   ├── dockerfiles/
│   │   └── nginx/
│   └── services/                  # Infrastructure configs
│
├── docs/                          # Documentation
│   ├── guides/                    # Setup guides
│   ├── features/                  # Feature documentation
│   └── analysis/                  # Architecture analysis
│
└── scripts/                       # Utility scripts
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.12+ | Core Language |
| FastAPI | 0.115+ | Web Framework |
| SQLAlchemy | 2.0+ | ORM |
| PostgreSQL | 16 | Primary Database |
| Redis | 7 | Cache & Job Queue |
| Alembic | 1.13+ | Migrations |
| Pydantic | 2.0+ | Validation |

### AI Microservice
| Technology | Purpose |
|------------|---------|
| GROQ | LLM (llama-3.3-70b-versatile) |
| HuggingFace | Embeddings, Open models |
| Gemini | Multimodal AI |
| NanoBananaPRO | Imagen 4 Ultra |
| Pollinations | FREE image generation |
| ChromaDB | Vector Database |
| LangChain | Agent framework |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18+ | UI Framework |
| TypeScript | 5.6+ | Type Safety |
| Vite | 6.0+ | Build Tool |
| TailwindCSS | 3.4+ | Styling |
| Radix UI | Latest | Accessible Components |
| Zustand | Latest | State Management |
| React Query | Latest | Server State |
| React Hook Form | Latest | Forms |

### DevOps
| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| Docker Compose | Orchestration |
| Traefik | Reverse Proxy, SSL |
| Prometheus | Metrics |
| Grafana | Dashboards |
| GitHub Actions | CI/CD |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [API Keys Setup](docs/guides/API_KEYS_SETUP_GUIDE.md) | Configure all API integrations |
| [Docker Setup](docs/getting-started/docker-setup.md) | Docker configuration guide |
| [Quick Start](docs/getting-started/quick-start.md) | Get started in 5 minutes |
| [Marketing Agents](docs/guides/marketing-agents.md) | AI marketing agents usage |
| [Social Integration](docs/features/social_media_integration.md) | Social media setup |
| [Google OAuth](docs/guides/google_oauth_architecture.md) | Google API integration |
| [Image Generation](docs/guides/IMAGE-GENERATION-GOOGLE-GEMINI.md) | AI image setup |
| [Deployment](docs/guides/deployment.md) | Production deployment |
| [Architecture](docs/features/ARCHITETTURA_BACKEND_VS_AI_MICROSERVICE.md) | System architecture |

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Fork, clone, and create a branch
git checkout -b feature/amazing-feature

# Make changes and test
cd apps/backend && pytest
cd apps/frontend && npm test

# Commit with conventional commits
git commit -m "feat: add amazing feature"

# Push and create PR
git push origin feature/amazing-feature
```

### Commit Convention

```
feat: add new feature
fix: bug fix
docs: documentation
style: formatting
refactor: code refactoring
test: add tests
chore: maintenance
```

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **DataPizza AI** - AI Agent Framework (Made in Italy 🇮🇹)
- **GROQ** - Ultra-fast LLM inference
- **Pollinations** - Free AI image generation
- **FastAPI** - Modern Python web framework
- **React** - UI component library
- **TailwindCSS** - Utility-first CSS

---

<p align="center">
  <strong>Made with ❤️ in Italy by <a href="https://github.com/ciroautuori">Ciro Autuori</a></strong>
</p>

<p align="center">
  <a href="https://studiocentos.it">🌐 Website</a> •
  <a href="https://github.com/ciroautuori/studiocentos/issues">🐛 Report Bug</a> •
  <a href="https://github.com/ciroautuori/studiocentos/discussions">💬 Discussions</a>
</p>
