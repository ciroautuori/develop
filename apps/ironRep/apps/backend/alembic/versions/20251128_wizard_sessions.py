"""add wizard_sessions table

Revision ID: wizard_sessions_001
Revises:
Create Date: 2025-11-28

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision = 'wizard_sessions_001'
down_revision = '008'  # Latest migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create wizard_sessions table for persistent interview state."""
    op.create_table(
        'wizard_sessions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('email', sa.String(255), nullable=True),

        # Interview state
        sa.Column('phase', sa.String(50), nullable=False, server_default='greeting'),
        sa.Column('collected_data', JSON, nullable=False, server_default='{}'),
        sa.Column('agent_config', JSON, nullable=False, server_default='{}'),
        sa.Column('conversation_history', JSON, nullable=False, server_default='[]'),

        # Metadata
        sa.Column('started_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('is_completed', sa.Boolean, nullable=False, server_default='false'),
    )

    # Create indexes for common queries
    op.create_index('ix_wizard_sessions_user_completed', 'wizard_sessions', ['user_id', 'is_completed'])
    op.create_index('ix_wizard_sessions_updated_at', 'wizard_sessions', ['updated_at'])


def downgrade() -> None:
    """Drop wizard_sessions table."""
    op.drop_index('ix_wizard_sessions_updated_at', table_name='wizard_sessions')
    op.drop_index('ix_wizard_sessions_user_completed', table_name='wizard_sessions')
    op.drop_table('wizard_sessions')
