"""add admin settings tables

Revision ID: 005
Revises: 004
Create Date: 2024-11-10 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Admin Settings
    op.create_table(
        'admin_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('display_name', sa.String(100), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('timezone', sa.String(50), nullable=False, server_default='Europe/Rome'),
        sa.Column('language', sa.String(10), nullable=False, server_default='it'),
        sa.Column('email_notifications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('push_notifications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sms_notifications', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notify_new_booking', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('notify_new_contact', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('notify_project_update', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notify_system_alert', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('theme', sa.String(20), nullable=False, server_default='dark'),
        sa.Column('sidebar_collapsed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('items_per_page', sa.Integer(), nullable=False, server_default='20'),
        sa.Column('two_factor_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('two_factor_method', sa.String(20), nullable=True),
        sa.Column('session_timeout_minutes', sa.Integer(), nullable=False, server_default='120'),
        sa.Column('custom_preferences', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['admin_id'], ['admin_users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('admin_id')
    )
    
    # Password History
    op.create_table(
        'admin_password_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['admin_id'], ['admin_users.id'], ondelete='CASCADE')
    )
    
    # Indexes
    op.create_index('ix_admin_settings_admin_id', 'admin_settings', ['admin_id'])
    op.create_index('ix_admin_password_history_admin_id', 'admin_password_history', ['admin_id'])


def downgrade() -> None:
    op.drop_table('admin_password_history')
    op.drop_table('admin_settings')
