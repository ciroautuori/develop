"""
Quick Database Seeding - RAW SQL version.
Bypasses SQLAlchemy ORM to avoid model loading issues.
"""

import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://studiocentos:studiocentos2025@postgres:5432/studiocentos")
engine = create_engine(DATABASE_URL)


def seed_portfolio():
    """Seed portfolio data using raw SQL."""
    
    with engine.connect() as conn:
        # Check existing data
        result = conn.execute(text("SELECT COUNT(*) FROM projects"))
        existing_projects = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM services"))
        existing_services = result.scalar()
        
        print(f"📊 Current database state:")
        print(f"   - Projects: {existing_projects}")
        print(f"   - Services: {existing_services}\n")
        
        # ================================================================
        # PROJECTS
        # ================================================================
        
        projects_sql = """
        INSERT INTO projects (
            title, slug, description, year, category, live_url, github_url,
            images, technologies, metrics, status, is_featured, is_public, "order",
            created_at, updated_at
        ) VALUES
        (
            'StudioCentOS Enterprise Platform',
            'studiocentos-enterprise',
            'Full-stack framework enterprise production-ready con AI integration',
            2024,
            'Enterprise Framework',
            'https://studiocentos.it',
            NULL,
            '[]'::jsonb,
            '["React 19", "FastAPI", "PostgreSQL 16", "Redis 7", "Docker", "AI Agents"]'::jsonb,
            '{"files": "850+", "domains": "11", "components": "200+", "time_to_market": "45gg"}'::jsonb,
            'active',
            true,
            true,
            1,
            NOW(),
            NOW()
        ),
        (
            'Phoenix AI',
            'phoenix-ai',
            'Piattaforma multi-agent per automazione enterprise',
            2024,
            'AI Platform',
            'https://phoenix-ai.duckdns.org',
            NULL,
            '[]'::jsonb,
            '["Python 3.12", "LangChain", "ChromaDB", "GPT-4"]'::jsonb,
            '{"tools": "78", "rag": "Vector search", "monitoring": "24/7"}'::jsonb,
            'active',
            true,
            true,
            2,
            NOW(),
            NOW()
        ),
        (
            'StudioCentOS Platform',
            'studiocentos-platform',
            'Enterprise full-stack framework production-ready',
            2024,
            'Framework',
            'https://studiocentos.it',
            NULL,
            '[]'::jsonb,
            '["React 19", "FastAPI", "PostgreSQL 16", "Redis 7", "Docker"]'::jsonb,
            '{"files": "850+", "domains": "11", "components": "200+"}'::jsonb,
            'active',
            true,
            true,
            3,
            NOW(),
            NOW()
        )
        ON CONFLICT (slug) DO NOTHING;
        """
        
        # ================================================================
        # SERVICES
        # ================================================================
        
        services_sql = """
        INSERT INTO services (
            title, slug, description, icon, category, features, benefits,
            value_indicator, cta_text, cta_url, is_active, is_featured, "order",
            created_at, updated_at
        ) VALUES
        (
            'STUDIOCENTOS Framework',
            'studiocentos-framework',
            'Enterprise full-stack framework production-ready con 850+ file e 11 domini business.',
            '⚡',
            'framework',
            '["React 19 + FastAPI", "PostgreSQL 16 + Redis 7", "DDD Architecture", "Docker + CI/CD ready", "MVP in 45 giorni"]'::jsonb,
            '[]'::jsonb,
            '€100K valore codice',
            'Scopri di più →',
            '#contatti',
            true,
            true,
            1,
            NOW(),
            NOW()
        ),
        (
            'AgentVanilla',
            'agent-vanilla',
            'Suite di 78 enterprise AI tools con monitoring Prometheus e Grafana integrato.',
            '🤖',
            'ai_tools',
            '["78 AI Tools pronti", "Multi-provider support", "Real-time monitoring", "Orchestrazione agents", "Production-tested"]'::jsonb,
            '[]'::jsonb,
            '€50K valore tools',
            'Scopri di più →',
            '#contatti',
            true,
            true,
            2,
            NOW(),
            NOW()
        ),
        (
            'fastBank',
            'fast-bank',
            'Component library con 50+ componenti React + FastAPI riutilizzabili e production-ready.',
            '🧩',
            'components',
            '["50+ Componenti UI", "TypeScript + Storybook", "30+ Makefile commands", "Automation completa", "Enterprise-tested"]'::jsonb,
            '[]'::jsonb,
            '-90% dev time',
            'Scopri di più →',
            '#contatti',
            true,
            false,
            3,
            NOW(),
            NOW()
        ),
        (
            'Sviluppo Custom',
            'sviluppo-custom',
            'Siti web, app mobile e soluzioni su misura con tecnologie moderne.',
            '🌐',
            'custom_dev',
            '["Landing page & Corporate", "E-commerce completi", "Web app custom", "SEO ottimizzato"]'::jsonb,
            '[]'::jsonb,
            NULL,
            'Richiedi Preventivo →',
            '#contatti',
            true,
            false,
            4,
            NOW(),
            NOW()
        ),
        (
            'App Mobile',
            'app-mobile',
            'Applicazioni iOS e Android con React Native ed Expo 52.',
            '📱',
            'mobile',
            '["iOS + Android native", "Offline-first", "Push notifications", "Backend integration"]'::jsonb,
            '[]'::jsonb,
            NULL,
            'Richiedi Preventivo →',
            '#contatti',
            true,
            false,
            5,
            NOW(),
            NOW()
        ),
        (
            'AI Integration',
            'ai-integration',
            'Integrazione AI nei tuoi prodotti con ChatGPT, agents custom e RAG.',
            '🔮',
            'ai_integration',
            '["Chatbot intelligenti", "AI Agents custom", "Document analysis (RAG)", "Automation workflows"]'::jsonb,
            '[]'::jsonb,
            NULL,
            'Richiedi Preventivo →',
            '#contatti',
            true,
            false,
            6,
            NOW(),
            NOW()
        )
        ON CONFLICT (slug) DO NOTHING;
        """
        
        # Execute
        result_projects = conn.execute(text(projects_sql))
        result_services = conn.execute(text(services_sql))
        conn.commit()
        
        print("✅ Portfolio data seeded successfully!")
        print(f"   - Projects added: {result_projects.rowcount}")
        print(f"   - Services added: {result_services.rowcount}\n")


if __name__ == "__main__":
    try:
        seed_portfolio()
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}\n")
        import traceback
        traceback.print_exc()
