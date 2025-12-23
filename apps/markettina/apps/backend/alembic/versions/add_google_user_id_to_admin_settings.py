"""add google_user_id to admin_google_settings

Revision ID: add_google_user_id
Revises:
Create Date: 2025-12-02 16:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_google_user_id'
down_revision: Union[str, None] = '014_toolai_posts'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add google_user_id column to admin_google_settings table."""
    op.add_column(
        'admin_google_settings',
        sa.Column('google_user_id', sa.String(100), nullable=True)
    )
    op.create_index(
        'ix_admin_google_settings_google_user_id',
        'admin_google_settings',
        ['google_user_id'],
        unique=True
    )


def downgrade() -> None:
    """Remove google_user_id column from admin_google_settings table."""
    op.drop_index('ix_admin_google_settings_google_user_id', table_name='admin_google_settings')
    op.drop_column('admin_google_settings', 'google_user_id')
