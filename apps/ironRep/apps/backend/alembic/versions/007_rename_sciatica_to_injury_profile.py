"""Rename sciatica_risk to injury_risk_profile

Revision ID: 007
Revises: 006
Create Date: 2025-11-26 07:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add the injury_risk_profile column (multi-injury support)
    op.add_column(
        'exercises',
        sa.Column('injury_risk_profile', postgresql.JSONB, nullable=True, server_default='{}')
    )

    # Migrate data from sciatica_risk to injury_risk_profile
    # Convert 'low', 'medium', 'high' to proper JSON structure
    op.execute("""
        UPDATE exercises
        SET injury_risk_profile = CASE
            WHEN sciatica_risk = 'high' THEN '{"sciatica": {"risk_level": "high", "notes": "Use caution"}}'::jsonb
            WHEN sciatica_risk = 'medium' THEN '{"sciatica": {"risk_level": "medium", "notes": "Proceed carefully"}}'::jsonb
            ELSE '{"sciatica": {"risk_level": "low", "notes": "Generally safe"}}'::jsonb
        END
        WHERE sciatica_risk IS NOT NULL
    """)

    # Drop the old sciatica_risk column and its index
    op.drop_index('ix_exercises_sciatica_risk', 'exercises')
    op.drop_column('exercises', 'sciatica_risk')


def downgrade() -> None:
    # Re-add sciatica_risk column
    op.add_column(
        'exercises',
        sa.Column('sciatica_risk', sa.String(20), nullable=False, server_default='low')
    )

    # Migrate data back
    op.execute("""
        UPDATE exercises
        SET sciatica_risk = COALESCE(
            injury_risk_profile->'sciatica'->>'risk_level',
            'low'
        )
        WHERE injury_risk_profile IS NOT NULL
    """)

    # Recreate the index
    op.create_index('idx_exercises_sciatica_risk', 'exercises', ['sciatica_risk'])

    # Drop injury_risk_profile
    op.drop_column('exercises', 'injury_risk_profile')
