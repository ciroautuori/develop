"""Add integration toggles to admin_settings

Revision ID: 013
Revises: 012_update_services_ai_focus
Create Date: 2025-05-29

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '013_integration_toggles'
down_revision = '012_update_services_ai'
branch_labels = None
depends_on = None


def upgrade():
    """Add meta_enabled and stripe_enabled columns to admin_settings."""
    # Check if columns exist before adding
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('admin_settings')]

    if 'meta_enabled' not in columns:
        op.add_column('admin_settings',
            sa.Column('meta_enabled', sa.Boolean(), nullable=True, server_default='false')
        )

    if 'stripe_enabled' not in columns:
        op.add_column('admin_settings',
            sa.Column('stripe_enabled', sa.Boolean(), nullable=True, server_default='false')
        )


def downgrade():
    """Remove integration toggle columns."""
    op.drop_column('admin_settings', 'stripe_enabled')
    op.drop_column('admin_settings', 'meta_enabled')
