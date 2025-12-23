from fastapi import APIRouter

from app.api.v1.endpoints import (
    projects, events, news, volunteer, bandi, bando_config, semantic_search, stats, aps_users, notifications, analytics, admin,
    corsi, eventi, progetti, volontariato, newspost, testimonials, partners
)
from app.api.v1 import auth, users

api_router = APIRouter()

# Authentication & Users (NEW SYSTEM)
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# ISS Platform Endpoints (NEW - Frontend Integration) - ORA ATTIVI! 🚀
api_router.include_router(corsi.router, prefix="/corsi", tags=["corsi"])
api_router.include_router(eventi.router, prefix="/eventi", tags=["eventi"])
api_router.include_router(progetti.router, prefix="/progetti", tags=["progetti"])
api_router.include_router(volontariato.router, prefix="/volontariato", tags=["volontariato"])
api_router.include_router(newspost.router, prefix="/newspost", tags=["newspost"])
api_router.include_router(testimonials.router, prefix="/testimonials", tags=["testimonials"])
api_router.include_router(partners.router, prefix="/partners", tags=["partners"])

# Legacy endpoints (for compatibility)
api_router.include_router(projects.router, prefix="/projects", tags=["projects-legacy"])
api_router.include_router(events.router, prefix="/events", tags=["events-legacy"])
api_router.include_router(news.router, prefix="/news", tags=["news-legacy"])
api_router.include_router(volunteer.router, prefix="/volunteer-applications", tags=["volunteer-legacy"])

# Bandi monitoring system
api_router.include_router(bandi.router, prefix="/bandi", tags=["bandi"])
api_router.include_router(bando_config.router, prefix="/admin/bandi-config", tags=["bandi-admin"])

# AI & Semantic Search System 🤖
api_router.include_router(semantic_search.router, prefix="/ai", tags=["ai-semantic-search"])

# ISS Platform Statistics 📊
api_router.include_router(stats.router, prefix="/stats", tags=["statistics"])

# APS Users & Organizations System 👥
api_router.include_router(aps_users.router, prefix="/aps-users", tags=["aps-users"])

# Notifications & Alerts System 📧
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])

# Analytics & Dashboard 📊
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

# Admin & System Management 🔐
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

# Sistema Donazioni (per supportare i progetti)
# api_router.include_router(donations.router, prefix="/donazioni", tags=["donazioni"])

# Sistema Notifiche
# api_router.include_router(notifications.router, prefix="/notifiche", tags=["notifiche"])

# Sistema Certificati (per corsi completati)
# api_router.include_router(certificates.router, prefix="/certificati", tags=["certificati"])

# Sistema Feedback e Recensioni
# api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
