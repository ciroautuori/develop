#!/usr/bin/env python3
"""
Seed Portfolio Data - Inserisce progetti e servizi nel database
DATI ESATTI dalla landing page originale
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'apps', 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.domain.portfolio.models import Project, Service
from app.infrastructure.database.session import Base

# Database URL
DATABASE_URL = "postgresql://studiocentos_user:studiocentos_password@localhost:5432/studiocentos_db"

# Crea engine e session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def seed_projects(db):
    """Inserisce i 2 progetti dalla landing originale"""
    
    projects_data = [
        {
            "title": "CV-Lab Pro",
            "slug": "cv-lab-pro",
            "description": "Portfolio builder con AI per professionisti",
            "year": 2024,
            "category": "SaaS Platform",
            "live_url": "https://cv-lab.pro",
            "github_url": None,
            "demo_url": None,
            "technologies": ["React 19", "FastAPI", "PostgreSQL 16", "AI Agents"],
            "metrics": {
                "File production-ready": "850+",
                "Domini business": "11",
                "Time to market": "45gg"
            },
            "status": "active",
            "is_featured": True,
            "is_public": True,
            "order": 1,
            "thumbnail_url": None,
            "images": []
        },
        {
            "title": "Phoenix AI",
            "slug": "phoenix-ai",
            "description": "Piattaforma multi-agent per automazione enterprise",
            "year": 2024,
            "category": "AI Platform",
            "live_url": "https://phoenix-ai.duckdns.org",
            "github_url": None,
            "demo_url": None,
            "technologies": ["Python 3.12", "LangChain", "ChromaDB", "GPT-4"],
            "metrics": {
                "Enterprise AI tools": "78",
                "Vector search": "RAG",
                "Monitoring": "24/7"
            },
            "status": "active",
            "is_featured": True,
            "is_public": True,
            "order": 2,
            "thumbnail_url": None,
            "images": []
        }
    ]
    
    print("🚀 Inserimento progetti...")
    for proj_data in projects_data:
        # Check se esiste già
        existing = db.query(Project).filter(Project.slug == proj_data["slug"]).first()
        if existing:
            print(f"  ⚠️  Progetto '{proj_data['title']}' già esistente, skip")
            continue
        
        project = Project(**proj_data)
        db.add(project)
        print(f"  ✅ Aggiunto: {proj_data['title']}")
    
    db.commit()
    print("✅ Progetti inseriti!\n")


def seed_services(db):
    """Inserisce i 6 servizi dalla landing originale"""
    
    services_data = [
        {
            "title": "STUDIOCENTOS Framework",
            "slug": "studiocentos-framework",
            "description": "Enterprise full-stack framework production-ready con 850+ file e 11 domini business.",
            "icon": "⚡",
            "category": "framework",
            "features": [
                "React 19 + FastAPI",
                "PostgreSQL 16 + Redis 7",
                "DDD Architecture",
                "Docker + CI/CD ready",
                "MVP in 45 giorni"
            ],
            "benefits": [],
            "value_indicator": "€100K valore codice",
            "cta_text": "Scopri di più →",
            "cta_url": "#contatti",
            "is_active": True,
            "is_featured": True,
            "order": 1
        },
        {
            "title": "AgentVanilla",
            "slug": "agentvanilla",
            "description": "Suite di 78 enterprise AI tools con monitoring Prometheus e Grafana integrato.",
            "icon": "🤖",
            "category": "ai_tools",
            "features": [
                "78 AI Tools pronti",
                "Multi-provider support",
                "Real-time monitoring",
                "Orchestrazione agents",
                "Production-tested"
            ],
            "benefits": [],
            "value_indicator": "€50K valore tools",
            "cta_text": "Scopri di più →",
            "cta_url": "#contatti",
            "is_active": True,
            "is_featured": True,
            "order": 2
        },
        {
            "title": "fastBank",
            "slug": "fastbank",
            "description": "Component library con 50+ componenti React + FastAPI riutilizzabili e production-ready.",
            "icon": "🧩",
            "category": "components",
            "features": [
                "50+ Componenti UI",
                "TypeScript + Storybook",
                "30+ Makefile commands",
                "Automation completa",
                "Enterprise-tested"
            ],
            "benefits": [],
            "value_indicator": "-90% dev time",
            "cta_text": "Scopri di più →",
            "cta_url": "#contatti",
            "is_active": True,
            "is_featured": True,
            "order": 3
        },
        {
            "title": "Sviluppo Custom",
            "slug": "sviluppo-custom",
            "description": "Siti web, app mobile e soluzioni su misura con tecnologie moderne.",
            "icon": "🌐",
            "category": "custom_dev",
            "features": [
                "Landing page & Corporate",
                "E-commerce completi",
                "Web app custom",
                "SEO ottimizzato"
            ],
            "benefits": [],
            "value_indicator": None,
            "cta_text": "Richiedi Preventivo →",
            "cta_url": "#contatti",
            "is_active": True,
            "is_featured": False,
            "order": 4
        },
        {
            "title": "App Mobile",
            "slug": "app-mobile",
            "description": "Applicazioni iOS e Android con React Native ed Expo 52.",
            "icon": "📱",
            "category": "mobile",
            "features": [
                "iOS + Android native",
                "Offline-first",
                "Push notifications",
                "Backend integration"
            ],
            "benefits": [],
            "value_indicator": None,
            "cta_text": "Richiedi Preventivo →",
            "cta_url": "#contatti",
            "is_active": True,
            "is_featured": False,
            "order": 5
        },
        {
            "title": "AI Integration",
            "slug": "ai-integration",
            "description": "Integrazione AI nei tuoi prodotti con ChatGPT, agents custom e RAG.",
            "icon": "🔮",
            "category": "ai_integration",
            "features": [
                "Chatbot intelligenti",
                "AI Agents custom",
                "Document analysis (RAG)",
                "Automation workflows"
            ],
            "benefits": [],
            "value_indicator": None,
            "cta_text": "Richiedi Preventivo →",
            "cta_url": "#contatti",
            "is_active": True,
            "is_featured": False,
            "order": 6
        }
    ]
    
    print("🚀 Inserimento servizi...")
    for serv_data in services_data:
        # Check se esiste già
        existing = db.query(Service).filter(Service.slug == serv_data["slug"]).first()
        if existing:
            print(f"  ⚠️  Servizio '{serv_data['title']}' già esistente, skip")
            continue
        
        service = Service(**serv_data)
        db.add(service)
        print(f"  ✅ Aggiunto: {serv_data['title']}")
    
    db.commit()
    print("✅ Servizi inseriti!\n")


def main():
    """Main function"""
    print("\n" + "="*60)
    print("  SEED PORTFOLIO DATA - StudiocentOS")
    print("="*60 + "\n")
    
    db = SessionLocal()
    
    try:
        seed_projects(db)
        seed_services(db)
        
        # Verifica
        total_projects = db.query(Project).count()
        total_services = db.query(Service).count()
        
        print("="*60)
        print(f"✅ COMPLETATO!")
        print(f"   Progetti totali nel DB: {total_projects}")
        print(f"   Servizi totali nel DB: {total_services}")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
