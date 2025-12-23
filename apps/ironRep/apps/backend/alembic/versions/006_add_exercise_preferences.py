"""Add exercise preferences table

Revision ID: 006
Revises: 005
Create Date: 2025-11-26

Adds table for user exercise preferences (like/dislike/rating).
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create exercise_preferences table."""
    op.create_table(
        'exercise_preferences',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('exercise_id', sa.String(100), nullable=False),
        sa.Column('exercise_name', sa.String(255), nullable=False),

        # Preference type: like, dislike, neutral
        sa.Column('preference', sa.String(20), nullable=False, default='neutral'),

        # Rating 1-5 (optional)
        sa.Column('rating', sa.Integer, nullable=True),

        # Reason for preference
        sa.Column('reason', sa.Text, nullable=True),

        # Extra data
        sa.Column('extra_data', JSONB, nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),

        # Unique constraint: one preference per user per exercise
        sa.UniqueConstraint('user_id', 'exercise_id', name='uq_user_exercise_preference')
    )

    # Create index for faster lookups
    op.create_index(
        'ix_exercise_preferences_user_id',
        'exercise_preferences',
        ['user_id']
    )
    op.create_index(
        'ix_exercise_preferences_exercise_id',
        'exercise_preferences',
        ['exercise_id']
    )
    op.create_index(
        'ix_exercise_preferences_preference',
        'exercise_preferences',
        ['preference']
    )


def downgrade() -> None:
    """Drop exercise_preferences table."""
    op.drop_index('ix_exercise_preferences_preference')
    op.drop_index('ix_exercise_preferences_exercise_id')
    op.drop_index('ix_exercise_preferences_user_id')
    op.drop_table('exercise_preferences')
