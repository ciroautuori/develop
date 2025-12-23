"""Add chat_history table

Revision ID: 004
Revises: 003
Create Date: 2025-11-22 11:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create chat_history table
    op.create_table(
        'chat_history',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('session_id', sa.String(36), nullable=False, index=True),
        sa.Column('role', sa.String(20), nullable=False),  # 'user' or 'assistant'
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),  # For storing context, tools used, etc.
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Create index for efficient session retrieval
    op.create_index(
        'ix_chat_history_session_timestamp',
        'chat_history',
        ['session_id', 'timestamp']
    )

    # Create index for user history queries
    op.create_index(
        'ix_chat_history_user_timestamp',
        'chat_history',
        ['user_id', 'timestamp']
    )


def downgrade() -> None:
    op.drop_index('ix_chat_history_user_timestamp', table_name='chat_history')
    op.drop_index('ix_chat_history_session_timestamp', table_name='chat_history')
    op.drop_table('chat_history')
