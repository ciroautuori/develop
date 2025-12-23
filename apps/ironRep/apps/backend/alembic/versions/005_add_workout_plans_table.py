"""Add workout_plans table

Revision ID: 005
Revises: 004
Create Date: 2025-11-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create workout_plans table
    op.create_table(
        'workout_plans',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('date', sa.DateTime(), nullable=False, index=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='generated'),

        # Plan content
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('exercises', sa.JSON(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),

        # Medical constraints
        sa.Column('constraints', sa.JSON(), nullable=True),
        sa.Column('clearance_level', sa.String(20), nullable=True),
        sa.Column('max_intensity_percent', sa.Integer(), nullable=True),

        # Completion tracking
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('pain_after', sa.Integer(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create index on status for filtering
    op.create_index('ix_workout_plans_status', 'workout_plans', ['status'])
    op.create_index('ix_workout_plans_user_date', 'workout_plans', ['user_id', 'date'])


def downgrade() -> None:
    op.drop_index('ix_workout_plans_user_date', table_name='workout_plans')
    op.drop_index('ix_workout_plans_status', table_name='workout_plans')
    op.drop_table('workout_plans')
