# Agent Registry

This document tracks the status and capabilities of all AI Agents in the `ai_microservice`.

| Agent Name | Type | Model | Status | Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| **SEO Specialist** | `seo_specialist` | Ollama / GPT-4o | ✅ Active | Keyword Research, GSC Analysis, Nginx SEO Logic, Soft 404 Fixes |
| **Social Media Manager** | `social_media` | GPT-4o | ✅ Active | Post Generation (LinkedIn, Insta), Scheduling |
| **Content Creator** | `content_creator` | GPT-4o / Ollama | ✅ Active | Blog Writing, Copywriting, SEO-aware articles |
| **Deep Analyst** | `analyst` | Ollama | ✅ Active | Multi-step research, Document synthesis (RAG), Competitive intel |
| **Draft Service** | `draft` | Ollama | ✅ Active | automated document creation, contract drafting, proposal generation |
| **Support Bot** | `support` | Ollama | 🚧 Planned | Q&A, Ticket Resolution |

## Integration Details

### LLM Strategy
- **Primary**: **Ollama** (centralized service for privacy and low latency in agency workflows).
- **Fallback**: Google Gemini / OpenAI (for high-complexity reasoning or if local resources are saturated).

### Agent Logic
- **Path**: `app/domain/marketing/` (Core Agents)
- **Infrastructure**: `app/infrastructure/agents/` (Base Agent, State Management)
- **Tools**: Google Search Console, Analytics, LinkedIn, Apollo.io (Integrations).

## Common Architecture
All agents inherit from `BaseAgent` and utilize shared infrastructure for RAG and memory persistence.
