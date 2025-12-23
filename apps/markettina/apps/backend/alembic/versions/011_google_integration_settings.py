"""Add Google Integration Settings table

Revision ID: 011_google_integration
Revises: 010_scheduled_posts_editorial_calendar
Create Date: 2025-11-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '011_google_integration'
down_revision: Union[str, None] = '010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create admin_google_settings table
    op.create_table(
        'admin_google_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('ga4_property_id', sa.String(100), nullable=True),
        sa.Column('ga4_account_id', sa.String(100), nullable=True),
        sa.Column('gmb_account_id', sa.String(100), nullable=True),
        sa.Column('gmb_location_id', sa.String(100), nullable=True),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('scopes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_google_settings_admin_id'), 'admin_google_settings', ['admin_id'], unique=True)
    op.create_index(op.f('ix_admin_google_settings_id'), 'admin_google_settings', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_admin_google_settings_id'), table_name='admin_google_settings')
    op.drop_index(op.f('ix_admin_google_settings_admin_id'), table_name='admin_google_settings')
    op.drop_table('admin_google_settings')
