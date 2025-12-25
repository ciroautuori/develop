"""
Quick Database Seeding Script - StudioCentOS Portfolio.
Simplified version for container execution.
"""

import sys
import os

# Minimal imports to avoid circular dependencies
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

# Use DATABASE_URL directly
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://studiocentos:studiocentos2025@postgres:5432/studiocentos")
engine = create_engine(DATABASE_URL)

# Import only what we need - avoid loading all models
sys.path.insert(0, "/app")
from app.domain.portfolio.models import Project, Service


def seed_portfolio():
    """Seed portfolio data synchronously."""
    
    with Session(engine) as session:
        # Check if data already exists
        existing_projects = session.query(Project).count()
        existing_services = session.query(Service).count()
        
        if existing_projects > 0 or existing_services > 0:
            print(f"⚠️  Database already has data:")
            print(f"   - {existing_projects} projects")
            print(f"   - {existing_services} services")
            response = input("Do you want to continue and add more? (y/n): ")
            if response.lower() != 'y':
                print("❌ Seeding cancelled")
                return
        
        # ====================================================================
        # PROGETTI
        # ====================================================================
        
        projects = [
            Project(
                title="CV-Lab Pro",
                slug="cv-lab-pro",
                description="Portfolio builder con AI per professionisti",
                year=2024,
                category="SaaS Platform",
                live_url="https://cv-lab.pro",
                github_url=None,
                technologies=["React 19", "FastAPI", "PostgreSQL 16", "AI Agents"],
                metrics={
                    "files": "850+",
                    "domains": "11",
                    "time_to_market": "45gg"
                },
                status="active",
                is_featured=True,
                is_public=True,
                order=1
            ),
            Project(
                title="Phoenix AI",
                slug="phoenix-ai",
                description="Piattaforma multi-agent per automazione enterprise",
                year=2024,
                category="AI Platform",
                live_url="https://phoenix-ai.duckdns.org",
                github_url=None,
                technologies=["Python 3.12", "LangChain", "ChromaDB", "GPT-4"],
                metrics={
                    "tools": "78",
                    "rag": "Vector search",
                    "monitoring": "24/7"
                },
                status="active",
                is_featured=True,
                is_public=True,
                order=2
            ),
            Project(
                title="StudioCentOS Platform",
                slug="studiocentos-platform",
                description="Enterprise full-stack framework production-ready",
                year=2024,
                category="Framework",
                live_url="https://studiocentos.it",
                github_url=None,
                technologies=["React 19", "FastAPI", "PostgreSQL 16", "Redis 7", "Docker"],
                metrics={
                    "files": "850+",
                    "domains": "11",
                    "components": "200+"
                },
                status="active",
                is_featured=True,
                is_public=True,
                order=3
            )
        ]
        
        # ====================================================================
        # SERVIZI
        # ====================================================================
        
        services = [
            Service(
                title="STUDIOCENTOS Framework",
                slug="studiocentos-framework",
                description="Enterprise full-stack framework production-ready con 850+ file e 11 domini business.",
                icon="⚡",
                category="framework",
                features=[
                    "React 19 + FastAPI",
                    "PostgreSQL 16 + Redis 7",
                    "DDD Architecture",
                    "Docker + CI/CD ready",
                    "MVP in 45 giorni"
                ],
                value_indicator="€100K valore codice",
                cta_text="Scopri di più →",
                cta_url="#contatti",
                is_active=True,
                is_featured=True,
                order=1
            ),
            Service(
                title="AgentVanilla",
                slug="agent-vanilla",
                description="Suite di 78 enterprise AI tools con monitoring Prometheus e Grafana integrato.",
                icon="🤖",
                category="ai_tools",
                features=[
                    "78 AI Tools pronti",
                    "Multi-provider support",
                    "Real-time monitoring",
                    "Orchestrazione agents",
                    "Production-tested"
                ],
                value_indicator="€50K valore tools",
                cta_text="Scopri di più →",
                cta_url="#contatti",
                is_active=True,
                is_featured=True,
                order=2
            ),
            Service(
                title="fastBank",
                slug="fast-bank",
                description="Component library con 50+ componenti React + FastAPI riutilizzabili e production-ready.",
                icon="🧩",
                category="components",
                features=[
                    "50+ Componenti UI",
                    "TypeScript + Storybook",
                    "30+ Makefile commands",
                    "Automation completa",
                    "Enterprise-tested"
                ],
                value_indicator="-90% dev time",
                cta_text="Scopri di più →",
                cta_url="#contatti",
                is_active=True,
                is_featured=False,
                order=3
            ),
            Service(
                title="Sviluppo Custom",
                slug="sviluppo-custom",
                description="Siti web, app mobile e soluzioni su misura con tecnologie moderne.",
                icon="🌐",
                category="custom_dev",
                features=[
                    "Landing page & Corporate",
                    "E-commerce completi",
                    "Web app custom",
                    "SEO ottimizzato"
                ],
                value_indicator=None,
                cta_text="Richiedi Preventivo →",
                cta_url="#contatti",
                is_active=True,
                is_featured=False,
                order=4
            ),
            Service(
                title="App Mobile",
                slug="app-mobile",
                description="Applicazioni iOS e Android con React Native ed Expo 52.",
                icon="📱",
                category="mobile",
                features=[
                    "iOS + Android native",
                    "Offline-first",
                    "Push notifications",
                    "Backend integration"
                ],
                value_indicator=None,
                cta_text="Richiedi Preventivo →",
                cta_url="#contatti",
                is_active=True,
                is_featured=False,
                order=5
            ),
            Service(
                title="AI Integration",
                slug="ai-integration",
                description="Integrazione AI nei tuoi prodotti con ChatGPT, agents custom e RAG.",
                icon="🔮",
                category="ai_integration",
                features=[
                    "Chatbot intelligenti",
                    "AI Agents custom",
                    "Document analysis (RAG)",
                    "Automation workflows"
                ],
                value_indicator=None,
                cta_text="Richiedi Preventivo →",
                cta_url="#contatti",
                is_active=True,
                is_featured=False,
                order=6
            )
        ]
        
        # Add all
        session.add_all(projects + services)
        session.commit()
        
        print("\n✅ Portfolio data seeded successfully!")
        print(f"   - {len(projects)} projects added")
        print(f"   - {len(services)} services added")
        print(f"   - Total: {len(projects) + len(services)} items\n")


if __name__ == "__main__":
    try:
        seed_portfolio()
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
