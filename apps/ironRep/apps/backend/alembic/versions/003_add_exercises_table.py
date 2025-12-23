"""Add exercises table

Revision ID: 003
Revises: 002
Create Date: 2025-11-22 10:34:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create exercises table
    op.create_table(
        'exercises',
        sa.Column('id', sa.String(100), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),  # mobility, stability, strength, olympic, gymnastics, metcon
        sa.Column('movement_pattern', sa.String(50), nullable=True),  # hinge, squat, push, pull, carry
        sa.Column('phases', postgresql.JSONB, nullable=False),  # Array of phase names
        sa.Column('equipment', postgresql.JSONB, nullable=False),  # Array of equipment needed
        sa.Column('contraindications', postgresql.JSONB, nullable=False),  # Array of contraindications
        sa.Column('progressions', postgresql.JSONB, nullable=True),  # Array of exercise IDs
        sa.Column('regressions', postgresql.JSONB, nullable=True),  # Array of exercise IDs
        sa.Column('coaching_cues', postgresql.JSONB, nullable=False),  # Array of coaching cues
        sa.Column('video_url', sa.String(500), nullable=True),
        sa.Column('thumbnail_url', sa.String(500), nullable=True),
        sa.Column('sets_range_min', sa.Integer, nullable=False, server_default='2'),
        sa.Column('sets_range_max', sa.Integer, nullable=False, server_default='4'),
        sa.Column('reps_range_min', sa.Integer, nullable=False, server_default='5'),
        sa.Column('reps_range_max', sa.Integer, nullable=False, server_default='12'),
        sa.Column('rest_seconds', sa.Integer, nullable=False, server_default='60'),
        sa.Column('difficulty', sa.String(20), nullable=False, server_default='beginner'),  # beginner, intermediate, advanced
        sa.Column('sciatica_risk', sa.String(20), nullable=False, server_default='low'),  # low, medium, high
        sa.Column('modifications', postgresql.JSONB, nullable=True),  # Pain-based modifications
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Create indexes
    op.create_index('idx_exercises_category', 'exercises', ['category'])
    op.create_index('idx_exercises_difficulty', 'exercises', ['difficulty'])
    op.create_index('idx_exercises_sciatica_risk', 'exercises', ['sciatica_risk'])
    op.create_index('idx_exercises_is_active', 'exercises', ['is_active'])


def downgrade() -> None:
    op.drop_index('idx_exercises_is_active', 'exercises')
    op.drop_index('idx_exercises_sciatica_risk', 'exercises')
    op.drop_index('idx_exercises_difficulty', 'exercises')
    op.drop_index('idx_exercises_category', 'exercises')
    op.drop_table('exercises')
