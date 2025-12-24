# Agent Registry

This document tracks the status and capabilities of all AI Agents in the `ai_microservice`.

| Agent Name | Type | Model | Status | Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| **SEO Specialist** | `seo_specialist` | GPT-4o / Ollama | ✅ Active | Keyword Research, Competitor Analysis (GSC), Content Planning |
| **Social Media Manager** | `social_media` | GPT-4o | ✅ Active | Post Generation (LinkedIn, Insta), Scheduling |
| **Content Creator** | `content_creator` | GPT-4o | ✅ Active | Blog Writing, Copywriting |
| **Lead Generator** | `lead_generator` | GPT-4o | ⚠️ Partial | Email Scraping (Apollo.io missing), Outreach |
| **Support Bot** | `support` | Ollama | 🚧 Planned | Q&A, Ticket Resolution |

## Integration Details

### SEO Specialist
- **Path**: `app/domain/marketing/seo_specialist.py`
- **Tools**: Google Search Console API, Google Analytics 4 API.
- **Notes**: Recently patched to fix instantiation issues. Uses "Premium" UI modal.

### Social Media Manager
- **Path**: `app/domain/marketing/social_media.py`
- **Tools**: LinkedIn API (Mock/Real), Instagram Graph API.
- **Notes**: Supports batch generation.

## Common Architecture
All agents inherit from `BaseAgent` (`app/infrastructure/agents/base_agent.py`) and use `StateManager` for persistence.
