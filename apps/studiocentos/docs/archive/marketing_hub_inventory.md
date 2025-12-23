# MarketingHub Architecture Inventory & Tracing

**Date:** 2025-12-05
**Total Files:** 53
**Total Lines of Code:** ~21,000

---

## 1. Frontend Layer (React/Next.js)
**Path:** [apps/frontend/src/features/admin/pages/AIMarketing](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing)

### 🚀 Core Dashboard & Navigation
| File | Lines | Description |
|------|-------|-------------|
| [index.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/index.tsx) | ~200 | Main Entry Point. Mounts [AcquisitionWizard](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/AcquisitionWizard.tsx#273-786), [ConversionDashboard](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/ConversionDashboard.tsx#138-361), [WeeklyCalendar](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/dashboard/WeeklyCalendar.tsx#130-337). |
| [components/AcquisitionWizard.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/AcquisitionWizard.tsx) | 785 | **[NEW]** Unified 1-Click Acquisition System. Orchestrates Search -> Enrich -> Email. |
| [components/ConversionDashboard.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/ConversionDashboard.tsx) | 360 | **[NEW]** Real-time analytics stats & pipeline funnel visualization. |
| [components/dashboard/WeeklyCalendar.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/dashboard/WeeklyCalendar.tsx) | 336 | Content calendar view. Fetches scheduled posts & emails. |
| [components/dashboard/DashboardStats.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/dashboard/DashboardStats.tsx) | 202 | High-level KPI cards (top of page). |
| [components/dashboard/QuickActions.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/dashboard/QuickActions.tsx) | 199 | Action buttons for fast access to tools. |

### 🧠 Strategic Components (Pro)
| File | Lines | Description |
|------|-------|-------------|
| [components/LeadFinderPro.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/LeadFinderPro.tsx) | 825 | Advanced Google Places search & scoring interface. |
| [components/modals/LeadFinderProModal.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/modals/LeadFinderProModal.tsx) | 1,287 | **[HUGE]** Full-screen modal version of LeadFinder with stepper UI. |
| [components/SocialPublisherPro.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/SocialPublisherPro.tsx) | 954 | Complex social media post creator & scheduler (multi-platform). |
| [components/VideoStoryCreator.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/VideoStoryCreator.tsx) | 988 | AI Video & Story creation tool. |
| [components/EmailCampaignPro.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/EmailCampaignPro.tsx) | 730 | Advanced email campaign builder. |
| [components/MarketingAnalyticsPro.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/MarketingAnalyticsPro.tsx) | 708 | Deep dive analytics charts & reports. |
| [components/StoriesAIGenerator.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/StoriesAIGenerator.tsx) | 711 | Instagram Stories generator agent interface. |
| [components/BusinessDNAGenerator.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/BusinessDNAGenerator.tsx) | 529 | Brand voice & persona configuration (Business DNA). |
| [components/CalendarManager.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/CalendarManager.tsx) | 586 | Advanced calendar management interface. |

### 🛠️ Feature Components & Modals
| File | Lines | Description |
|------|-------|-------------|
| [components/BatchContentModal.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/BatchContentModal.tsx) | 385 | Batch generation content wizard. |
| [components/EmailCampaignGenerator.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/EmailCampaignGenerator.tsx) | 337 | Simple email generator. |
| [components/ContentGenerator.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/ContentGenerator.tsx) | 332 | Generic content generation component. |
| [components/VideoGenerator.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/VideoGenerator.tsx) | 275 | Simple video generator. |
| [components/MarketingAnalyticsDashboard.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/MarketingAnalyticsDashboard.tsx) | 252 | Simplified analytics dashboard. |
| [components/SocialPublisher.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/SocialPublisher.tsx) | 229 | Simple social publisher. |
| [components/ImageGenerator.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/ImageGenerator.tsx) | 210 | AI Image generation tool. |
| [components/ChatInterface.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/ChatInterface.tsx) | 201 | Marketing AI Chatbot interface. |
| [components/LeadFinder.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/LeadFinder.tsx) | 438 | *Legacy* Lead finder component. |
| [components/modals/CreatePostModal.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/modals/CreatePostModal.tsx) | 756 | Modal for creating a new post. |
| [components/modals/SettingsModal.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/modals/SettingsModal.tsx) | 720 | Settings configuration modal. |
| [components/modals/LeadFinderModal.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/modals/LeadFinderModal.tsx) | 668 | Modal wrapper for Lead Finder. |
| [components/modals/CreateEmailModal.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/modals/CreateEmailModal.tsx) | 623 | Modal for email creation. |
| [components/modals/CreateVideoModal.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing/components/modals/CreateVideoModal.tsx) | 538 | Modal for video creation. |

---

## 2. Backend Layer (FastAPI)
**Path:** `apps/backend/app/domain/marketing`

### 🔌 API Routers
| File | Lines | Description |
|------|-------|-------------|
| `router.py` | 130 | Main Router. Includes all other marketing routers. |
| `acquisition_router.py` | 489 | **[NEW]** `/acquisition` endpoints. Handles Launch, Stats, Pipeline. |
| `scheduler_router.py` | 312 | `/scheduler` endpoints. Handles Week View & Triggers. |
| `routers.py` | 732 | **[LEGACY/MAIN]** General marketing endpoints (posts, calendar). |
| `email_router.py` | 497 | Email marketing endpoints. |
| `lead_enrichment_router.py` | 578 | Google Places & Enrichment endpoints. |
| `brand_dna_router.py` | 197 | Business DNA management endpoints. |

### ⚙️ Services & Logic
| File | Lines | Description |
|------|-------|-------------|
| `lead_enrichment_service.py` | 773 | Logic for searching Google Places & scoring leads. |
| `email_service.py` | 639 | Logic for sending emails & managing campaigns. |
| `service.py` | 436 | General marketing service logic. |
| `models.py` | 324 | SQLAlchemy Models (`Lead`, `ScheduledPost`, `EmailCampaign`). |
| `schemas.py` | 470 | Pydantic Models (Request/Response schemas). |

---

## 3. AI Microservice Layer (Python)
**Path:** `apps/ai_microservice/app/domain/marketing`

### 🤖 AI Agents
| File | Lines | Description |
|------|-------|-------------|
| `email_marketing.py` | 814 | **Email Agent**: Generates copy, subject lines, sequences. |
| `social_media_manager.py` | 809 | **Social Agent**: Generates captions, hashtags, scheduling logic. |
| `campaign_manager.py` | 804 | **Strategy Agent**: High-level campaign planning. |
| `seo_specialist.py` | 698 | **SEO Agent**: Keyword research, content optimization. |
| `content_creator.py` | 696 | **Content Agent**: General blog/article writing. |
| `image_branding.py` | 632 | **Design Agent**: Applies brand overlay/watermarks to images. |
| `image_generator_agent.py` | 438 | **Creative Agent**: Generates images via DALL-E/Midjourney APIs. |
| `lead_intelligence_agent.py` | 258 | **Data Agent**: Scores leads based on enriched data. |

---

## 🔄 Runtime Flow Tracing

### Flow 1: Acquisition (Find Clients)
1.  **Frontend**: `AcquisitionWizard.tsx` (User Inputs Target)
2.  **Backend**: `acquisition_router.py` -> `lead_enrichment_service.py`
3.  **AI**: `lead_intelligence_agent.py` (Scores Leads)
4.  **AI**: `email_marketing.py` (Generates Personalized Email)
5.  **Backend**: Stores to `db.Leads` (via `models.py`)
6.  **Frontend**: `ConversionDashboard.tsx` polls `/acquisition/stats`

### Flow 2: Scheduling (Week View)
1.  **Frontend**: `WeeklyCalendar.tsx` calls `GET /scheduler/week`
2.  **Backend**: `scheduler_router.py` queries `scheduled_posts` & `email_campaigns`
3.  **Frontend**: Displays unified view of posts & emails

### Flow 3: Content Generation (Social)
1.  **Frontend**: `SocialPublisherPro.tsx` (User Request)
2.  **Backend**: `scheduler_router.py` / `routers.py`
3.  **AI**: `social_media_manager.py` (Generate Text)
4.  **AI**: `image_generator_agent.py` (Generate Image)
5.  **AI**: `image_branding.py` (Apply Logo/Brand)
6.  **Backend**: Saves `ScheduledPost`
