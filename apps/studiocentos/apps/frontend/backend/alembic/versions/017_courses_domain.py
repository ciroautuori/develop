"""add courses table

Revision ID: 017_courses_domain
Revises: 016_whatsapp_messages
Create Date: 2024-12-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '017_courses_domain'
down_revision: Union[str, None] = '016_whatsapp_messages'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create courses table for Corso Tool AI."""
    op.create_table(
        'courses',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('icon', sa.String(length=50), nullable=False),
        sa.Column('module_number', sa.Integer(), nullable=False),
        sa.Column('translations', postgresql.JSONB(), nullable=True, server_default='{}'),
        sa.Column('purchase_url', sa.String(length=500), nullable=False),
        sa.Column('preview_url', sa.String(length=500), nullable=True),
        sa.Column('duration_hours', sa.Integer(), nullable=True),
        sa.Column('difficulty', sa.String(length=50), nullable=True, server_default='beginner'),
        sa.Column('topics', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('price', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='active'),
        sa.Column('is_featured', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_new', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_public', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('thumbnail_url', sa.String(length=500), nullable=True),
        sa.Column('cover_image', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_courses_id'), 'courses', ['id'], unique=False)
    op.create_index(op.f('ix_courses_slug'), 'courses', ['slug'], unique=True)
    
    # Insert initial seed data - Corso Tool AI modules
    op.execute("""
        INSERT INTO courses (title, slug, description, icon, module_number, purchase_url, difficulty, topics, is_new, is_featured, "order")
        VALUES
        ('Il Meta Game', 'meta-game', 'Strategie avanzate per dominare l''ecosistema AI. Impara a pensare come un orchestratore di intelligenze artificiali.', '🎮', 1, 'https://gum.co/corso-toolai-meta', 'advanced', '["Strategia AI", "Ecosistema", "Meta-thinking"]', false, true, 1),
        ('Fondamenta Digitali', 'fondamenta-digitali', 'Le basi essenziali per costruire la tua presenza digitale AI-powered. Setup, tools, workflow ottimizzati.', '🏗️', 2, 'https://gum.co/corso-toolai-fondamenta', 'beginner', '["Setup", "Tools Base", "Workflow"]', false, false, 2),
        ('Visual Wow', 'visual-wow', 'Crea visual mozzafiato con AI. Da Midjourney a DALL-E, padroneggia la generazione visiva.', '✨', 3, 'https://gum.co/corso-toolai-visual', 'intermediate', '["Midjourney", "DALL-E", "Design AI"]', true, true, 3),
        ('Articoli Ninja', 'articoli-ninja', 'Scrivi contenuti che convertono. SEO, copywriting e storytelling potenziati dall''AI.', '✍️', 4, 'https://gum.co/corso-toolai-articoli', 'intermediate', '["SEO", "Copywriting", "Content Strategy"]', false, false, 4),
        ('Video Mastery', 'video-mastery', 'Produci video professionali con AI. Editing, script, voiceover automatizzati.', '🎬', 5, 'https://gum.co/corso-toolai-video', 'intermediate', '["Video AI", "Editing", "Script Generation"]', true, false, 5),
        ('Social Domination', 'social-domination', 'Automatizza e scala la tua presenza social. Scheduling, analytics, engagement AI-driven.', '📱', 6, 'https://gum.co/corso-toolai-social', 'beginner', '["Social Media", "Automazione", "Analytics"]', false, false, 6),
        ('Monetizzazione AI', 'monetizzazione-ai', 'Trasforma le competenze AI in revenue. Modelli di business, pricing, scaling strategies.', '💰', 7, 'https://gum.co/corso-toolai-monetize', 'advanced', '["Business", "Revenue", "Scaling"]', true, true, 7)
    """)


def downgrade() -> None:
    """Drop courses table."""
    op.drop_index(op.f('ix_courses_slug'), table_name='courses')
    op.drop_index(op.f('ix_courses_id'), table_name='courses')
    op.drop_table('courses')
