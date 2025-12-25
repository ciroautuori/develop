"""add_customer_id_to_bookings

Revision ID: 009_booking_customer_integration
Revises: 008_quotes_domain
Create Date: 2025-11-26 09:30:00.000000

Adds customer_id foreign key to bookings table to integrate with
the new centralized Customers domain.

This migration:
1. Adds customer_id column (nullable for backward compatibility)
2. Creates foreign key constraint to customers table
3. Creates index on customer_id

Note: A separate data migration script should be run to populate
customer_id from existing booking data (client_name, client_email, etc.)
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade():
    """
    Add customer_id column to bookings table.
    """
    # Add customer_id column (nullable for backward compatibility)
    op.add_column(
        'bookings',
        sa.Column('customer_id', sa.Integer(), nullable=True)
    )

    # Create foreign key constraint
    op.create_foreign_key(
        'fk_bookings_customer',
        'bookings',
        'customers',
        ['customer_id'],
        ['id']
    )

    # Create index on customer_id
    op.create_index(
        'ix_bookings_customer_id',
        'bookings',
        ['customer_id']
    )


def downgrade():
    """
    Remove customer_id column from bookings table.
    """
    # Drop index
    op.drop_index('ix_bookings_customer_id', table_name='bookings')

    # Drop foreign key
    op.drop_constraint('fk_bookings_customer', 'bookings', type_='foreignkey')

    # Drop column
    op.drop_column('bookings', 'customer_id')
