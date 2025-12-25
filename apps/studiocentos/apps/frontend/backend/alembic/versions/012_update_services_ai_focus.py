"""Update Services with AI Focus

Revision ID: 012_update_services_ai
Revises: 011_google_integration
Create Date: 2025-11-29

1. Aggiunge colonne mancanti alla tabella services
2. Aggiorna i servizi per riflettere l'offerta AI di StudioCentOS
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '012_update_services_ai'
down_revision: Union[str, None] = '011_google_integration'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Nuovi servizi basati su FastBank
SERVICES = [
    {
        "title": "Assistente Virtuale AI",
        "slug": "assistente-ai",
        "description": "Il tuo assistente virtuale intelligente che risponde ai clienti 24/7. Multi-lingua (IT, EN, ES), integrazione WhatsApp e Telegram, escalation automatica a operatore.",
        "icon": "🤖",
        "features": ["Risposte intelligenti 24/7", "Multi-lingua", "WhatsApp/Telegram", "Escalation automatica", "Analytics conversazioni"],
        "cta_text": "Attiva il tuo assistente →",
        "cta_url": "#contatti",
        "order": 1,
        "active": True,
        "is_featured": True
    },
    {
        "title": "Knowledge Base AI",
        "slug": "knowledge-base",
        "description": "Trasforma i tuoi documenti in una base di conoscenza intelligente. I tuoi clienti e dipendenti trovano risposte istantaneamente con ricerca semantica.",
        "icon": "📚",
        "features": ["Upload PDF/Word/Excel", "Ricerca semantica", "FAQ automatiche", "Citazione fonti", "Chat integrata"],
        "cta_text": "Organizza la conoscenza →",
        "cta_url": "#contatti",
        "order": 2,
        "active": True,
        "is_featured": False
    },
    {
        "title": "Dashboard Analytics",
        "slug": "dashboard-analytics",
        "description": "Visualizza il tuo business in tempo reale. KPI personalizzati, metriche automatiche, report settimanali. Alert su anomalie.",
        "icon": "📊",
        "features": ["Dashboard real-time", "KPI automatici", "Report settimanali", "Alert anomalie", "Export dati"],
        "cta_text": "Monitora il business →",
        "cta_url": "#contatti",
        "order": 3,
        "active": True,
        "is_featured": False
    },
    {
        "title": "Marketing Automation",
        "slug": "marketing-automation",
        "description": "Automatizza il tuo marketing: social media, email, contenuti. Calendario editoriale AI, analisi competitor, generazione contenuti automatica.",
        "icon": "📱",
        "features": ["Social automatico", "Email sequences", "Contenuti AI", "Analisi competitor", "A/B testing"],
        "cta_text": "Automatizza il marketing →",
        "cta_url": "#contatti",
        "order": 4,
        "active": True,
        "is_featured": False
    },
    {
        "title": "Sviluppo Web Enterprise",
        "slug": "sviluppo-web",
        "description": "Applicazioni web su misura: portali clienti, CRM, ERP, dashboard. React 19, FastAPI, PostgreSQL. Production-ready dal giorno 1.",
        "icon": "💻",
        "features": ["React 19 + TypeScript", "FastAPI backend", "PostgreSQL", "Multi-tenant", "API REST"],
        "cta_text": "Richiedi preventivo →",
        "cta_url": "#contatti",
        "order": 5,
        "active": True,
        "is_featured": False
    },
    {
        "title": "App Mobile",
        "slug": "app-mobile",
        "description": "App native iOS e Android. Push notifications, funziona offline, pubblicazione su App Store e Play Store inclusa.",
        "icon": "📲",
        "features": ["iOS + Android", "Push notifications", "Offline mode", "Store publishing", "Analytics"],
        "cta_text": "Crea la tua app →",
        "cta_url": "#contatti",
        "order": 6,
        "active": True,
        "is_featured": False
    },
    {
        "title": "E-commerce",
        "slug": "ecommerce",
        "description": "Shop online completo: catalogo prodotti, pagamenti sicuri, spedizioni integrate, fatturazione elettronica. Pronto a vendere in 30 giorni.",
        "icon": "🛒",
        "features": ["Catalogo illimitato", "Pagamenti sicuri", "Spedizioni integrate", "Fatturazione", "Multi-valuta"],
        "cta_text": "Apri il tuo shop →",
        "cta_url": "#contatti",
        "order": 7,
        "active": True,
        "is_featured": False
    },
    {
        "title": "Automazione Processi",
        "slug": "automazione",
        "description": "Automatizza processi ripetitivi: workflow, email, report automatici, integrazione CRM. Risparmia ore ogni settimana.",
        "icon": "⚡",
        "features": ["Workflow automation", "Email sequences", "Report automatici", "CRM integration", "Webhook"],
        "cta_text": "Automatizza il lavoro →",
        "cta_url": "#contatti",
        "order": 8,
        "active": True,
        "is_featured": False
    }
]


def upgrade() -> None:
    # 1. Aggiungi colonne mancanti (skip se esistono già)
    from sqlalchemy import inspect
    from sqlalchemy.engine import Engine

    bind = op.get_bind()
    inspector = inspect(bind)
    existing_columns = [c['name'] for c in inspector.get_columns('services')]

    if 'cta_text' not in existing_columns:
        op.add_column('services', sa.Column('cta_text', sa.String(200), nullable=True))
    if 'cta_url' not in existing_columns:
        op.add_column('services', sa.Column('cta_url', sa.String(500), nullable=True))
    if 'is_featured' not in existing_columns:
        op.add_column('services', sa.Column('is_featured', sa.Boolean(), server_default='false', nullable=False))
    if 'thumbnail_url' not in existing_columns:
        op.add_column('services', sa.Column('thumbnail_url', sa.String(500), nullable=True))

    # 2. Elimina i servizi esistenti
    op.execute("DELETE FROM services")

    # 3. Inserisci i nuovi servizi
    import json
    for service in SERVICES:
        features_json = json.dumps(service["features"])
        op.execute(f"""
            INSERT INTO services (
                title, slug, description, icon, category, features, benefits,
                cta_text, cta_url, "order", is_active, is_featured,
                created_at, updated_at
            ) VALUES (
                '{service["title"]}',
                '{service["slug"]}',
                '{service["description"].replace("'", "''")}',
                '{service["icon"]}',
                'ai_integration',
                '{features_json}'::jsonb,
                '[]'::jsonb,
                '{service["cta_text"]}',
                '{service["cta_url"]}',
                {service["order"]},
                {str(service["active"]).lower()},
                {str(service["is_featured"]).lower()},
                NOW(),
                NOW()
            )
        """)


def downgrade() -> None:
    # Rimuovi colonne aggiunte
    op.drop_column('services', 'thumbnail_url')
    op.drop_column('services', 'is_featured')
    op.drop_column('services', 'cta_url')
    op.drop_column('services', 'cta_text')

    # Svuota tabella
    op.execute("DELETE FROM services")
