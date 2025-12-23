"""Add google_accounts table

Revision ID: 010_add_google_accounts
Revises: 20251128_wizard_sessions
Create Date: 2025-12-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = '010_add_google_accounts'
down_revision = 'wizard_sessions_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if 'google_accounts' not in existing_tables:
        op.create_table(
            'google_accounts',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
            sa.Column('google_user_id', sa.String(255), nullable=True, unique=True),
            sa.Column('google_email', sa.String(255), nullable=True),
            sa.Column('access_token', sa.Text(), nullable=False),
            sa.Column('refresh_token', sa.Text(), nullable=True),
            sa.Column('token_expires_at', sa.DateTime(), nullable=True),
            sa.Column('scopes', sa.JSON(), nullable=True),
            sa.Column('fit_sync_enabled', sa.Boolean(), nullable=False, default=True),
            sa.Column('calendar_sync_enabled', sa.Boolean(), nullable=False, default=True),
            sa.Column('last_fit_sync_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
        )

    existing_indexes = {ix.get('name') for ix in inspector.get_indexes('google_accounts')}
    if 'idx_google_accounts_user_id' not in existing_indexes:
        op.create_index('idx_google_accounts_user_id', 'google_accounts', ['user_id'])


def downgrade() -> None:
    op.drop_index('idx_google_accounts_user_id', table_name='google_accounts')
    op.drop_table('google_accounts')
