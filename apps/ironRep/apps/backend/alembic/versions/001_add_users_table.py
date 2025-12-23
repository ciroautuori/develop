"""Add users table

Revision ID: 001
Revises:
Create Date: 2025-11-22 10:32:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=True),  # Nullable for OAuth users
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('age', sa.Integer, nullable=True),
        sa.Column('weight_kg', sa.Float, nullable=True),
        sa.Column('height_cm', sa.Float, nullable=True),
        sa.Column('sex', sa.String(1), nullable=True),  # M/F

        # Injury details
        sa.Column('injury_date', sa.DateTime, nullable=True),
        sa.Column('diagnosis', sa.String(255), nullable=True, server_default=''),
        sa.Column('pain_locations', postgresql.JSONB, nullable=True),
        sa.Column('injury_description', sa.Text, nullable=True),

        # Baseline strength (pre-injury)
        sa.Column('baseline_deadlift_1rm', sa.Float, nullable=True),
        sa.Column('baseline_squat_1rm', sa.Float, nullable=True),
        sa.Column('baseline_front_squat_1rm', sa.Float, nullable=True),
        sa.Column('baseline_bench_press_1rm', sa.Float, nullable=True),
        sa.Column('baseline_shoulder_press_1rm', sa.Float, nullable=True),
        sa.Column('baseline_snatch_1rm', sa.Float, nullable=True),
        sa.Column('baseline_clean_jerk_1rm', sa.Float, nullable=True),
        sa.Column('baseline_pullups_max', sa.Integer, nullable=True),

        # Current program state
        sa.Column('current_phase', sa.String(50), nullable=False, server_default='Fase 1: Decompressione'),
        sa.Column('weeks_in_current_phase', sa.Integer, nullable=False, server_default='0'),
        sa.Column('program_start_date', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        # Goals
        sa.Column('target_return_date', sa.DateTime, nullable=True),
        sa.Column('primary_goal', sa.String(255), nullable=True),
        sa.Column('goals_description', sa.Text, nullable=True),

        # Equipment & Preferences
        sa.Column('equipment_available', postgresql.JSONB, nullable=True),
        sa.Column('preferred_training_time', sa.String(50), nullable=True),
        sa.Column('session_duration_minutes', sa.Integer, nullable=True, server_default='60'),

        # Account status
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('is_onboarded', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_login_at', sa.DateTime, nullable=True),
    )

    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_is_active', 'users', ['is_active'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])


def downgrade() -> None:
    # Drop users table
    op.drop_index('idx_users_created_at', 'users')
    op.drop_index('idx_users_is_active', 'users')
    op.drop_index('idx_users_email', 'users')
    op.drop_table('users')
