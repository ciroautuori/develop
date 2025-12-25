"""
Seed Portfolio Data - Progetti e Servizi StudiocentOS.
"""

import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.domain.portfolio.models import Project, Service
from app.core.config import settings


async def seed_portfolio():
    """Seed portfolio data."""
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
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
        await session.commit()
        
        print("✅ Portfolio data seeded successfully!")
        print(f"   - {len(projects)} projects")
        print(f"   - {len(services)} services")


if __name__ == "__main__":
    asyncio.run(seed_portfolio())
