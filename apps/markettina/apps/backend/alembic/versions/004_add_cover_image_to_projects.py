"""add cover_image to projects

Revision ID: 004
Revises: 002
Create Date: 2024-11-10 16:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '002_add_admin_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add cover_image field to projects table."""
    op.add_column(
        'projects',
        sa.Column('cover_image', sa.String(500), nullable=True)
    )


def downgrade() -> None:
    """Remove cover_image field from projects table."""
    op.drop_column('projects', 'cover_image')
