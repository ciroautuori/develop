# StudioCentos Architecture Documentation

## Overview

StudioCentos is a monorepo containing a full-stack AI-first application suite. It consists of three main components:
1.  **Backend API**: A FastAPI-based REST API handling business logic, database interactions, and authentication.
2.  **AI Microservice**: A dedicated FastAPI service for AI operations, LLM interactions, and image/video generation.
3.  **Frontend**: A modern React application (Vite-powered) serving both the public Landing Page and the secure Admin Dashboard.

## System Architecture Diagram

```mermaid
graph TD
    User[User] -->|HTTPS| CDN[Cloudflare/CDN]
    CDN -->|HTTPS| Frontend[Frontend (React + Vite)]
    Frontend -->|REST API :8002| Backend[Backend API (FastAPI)]
    Frontend -->|REST API :8001| AI[AI Microservice (FastAPI)]
    
    subgraph "Backend Services"
        Backend -->|SQL| DB[(PostgreSQL 16)]
        Backend -->|Cache/Queue| Redis[(Redis 7)]
    end
    
    subgraph "AI Services"
        AI -->|Vector Search| ChromaDB[(ChromaDB)]
        AI -->|LLM API| Groq[Groq Llama 3]
        AI -->|Image API| NanoBanana[NanoBananaPro]
        AI -->|Video API| HeyGen[HeyGen]
    end
    
    Backend <-->|Internal API| AI
```

## Component Details

### 1. Backend Application (`apps/backend`)

*   **Framework**: FastAPI, Uvicorn
*   **Language**: Python 3.12+
*   **Database**: PostgreSQL 16 (via SQLAlchemy 2.0+ ORM)
*   **Migrations**: Alembic
*   **State & Caching**: Redis
*   **Architecture**: Domain-Driven Design (DDD)
*   **Key Directories**:
    *   `app/core`: Configuration, Security, Middleware.
    *   `app/domain`: Logic split by business domain (`auth`, `marketing`, `portfolio`, `finance`, etc.).
    *   `app/main.py`: Entry point and router registration.

### 2. AI Microservice (`apps/ai_microservice`)

*   **Framework**: FastAPI
*   **Language**: Python 3.12+
*   **Port**: 8001
*   **Purpose**: Specialized service for compute-intensive and GPU-reliant AI tasks.
*   **Key Features**:
    *   **RAG**: Retrieval Augmented Generation using ChromaDB.
    *   **Marketing Agents**: 9 specialized agents (ContentCreator, SEOSpecialist, etc.).
    *   **Integrations**: Groq, Google Gemini, NanoBanana, HeyGen.
*   **Key Directories**:
    *   `app/domain/marketing`: Implementations of specific AI agents.
    *   `app/core/api/v1`: Route definitions.

### 3. Frontend Application (`apps/frontend`)

*   **Framework**: React 18, Vite 6
*   **Language**: TypeScript 5.6
*   **Styling**: TailwindCSS 3.4
*   **State Management**: Zustand, TanStack Query (React Query)
*   **UI Library**: Radix UI (Headless), custom components.
*   **Key Directories**:
    *   `src/features`: Feature-based modularity (`landing`, `admin`, `crm`, `booking`).
    *   `src/shared`: Reusable UI components and hooks.
    *   `src/services`: API client layers.

## Configuration & DevOps

*   **Docker**: Docker Compose setup for both Development (`docker-compose.yml`) and Production (`docker-compose.production.yml`).
*   **Proxies**: Traefik (Production), Nginx.
*   **Build System**: Custom `Makefile` for orchestrating Docker, builds, and maintenance tasks.

## Key Workflows

### AI Content Generation
1.  Frontend sends request to **AI Microservice**.
2.  Microservice processes prompt via `Groq` or other providers.
3.  Generated content is returned to Frontend.
4.  User approves/saves content -> Frontend sends save request to **Backend**.
5.  Backend persists content to PostgreSQL.

### Authentication
*   JWT-based authentication.
*   OAuth2 support (Google, LinkedIn).
*   Role-based access control (Admin vs User).

## Current Status
*   **Monorepo**: Custom structure.
*   **Codebase Size**: Large (~150k+ lines implied by README).
*   **Deployment**: Docker-based, ready for production.
