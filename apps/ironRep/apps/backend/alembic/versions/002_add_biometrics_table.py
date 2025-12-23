"""Add biometrics table

Revision ID: 002
Revises: 001
Create Date: 2025-11-22 10:33:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create biometric_entries table
    op.create_table(
        'biometric_entries',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('date', sa.DateTime, nullable=False),
        sa.Column('type', sa.String(50), nullable=False),  # STRENGTH, ROM, BODY_COMP, CARDIOVASCULAR

        # Strength metrics
        sa.Column('exercise_id', sa.String(100), nullable=True),
        sa.Column('exercise_name', sa.String(255), nullable=True),
        sa.Column('weight_kg', sa.Float, nullable=True),
        sa.Column('reps', sa.Integer, nullable=True),
        sa.Column('estimated_1rm', sa.Float, nullable=True),

        # ROM metrics
        sa.Column('rom_test', sa.String(100), nullable=True),  # hip_flexion, shoulder_mobility, etc.
        sa.Column('rom_degrees', sa.Float, nullable=True),
        sa.Column('rom_side', sa.String(10), nullable=True),  # left, right, bilateral

        # Body composition
        sa.Column('weight', sa.Float, nullable=True),
        sa.Column('body_fat_percent', sa.Float, nullable=True),
        sa.Column('muscle_mass_kg', sa.Float, nullable=True),

        # Cardiovascular
        sa.Column('resting_hr', sa.Integer, nullable=True),
        sa.Column('hrv', sa.Integer, nullable=True),
        sa.Column('vo2max_estimate', sa.Float, nullable=True),

        # Metadata
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Create indexes
    op.create_index('idx_biometrics_user_date', 'biometric_entries', ['user_id', 'date'])
    op.create_index('idx_biometrics_user_type_date', 'biometric_entries', ['user_id', 'type', 'date'])
    op.create_index('idx_biometrics_exercise', 'biometric_entries', ['exercise_id'])


def downgrade() -> None:
    op.drop_index('idx_biometrics_exercise', 'biometric_entries')
    op.drop_index('idx_biometrics_user_type_date', 'biometric_entries')
    op.drop_index('idx_biometrics_user_date', 'biometric_entries')
    op.drop_table('biometric_entries')
