"""create_customers_domain_tables

Revision ID: 007_customers_domain
Revises: 006_add_notifications
Create Date: 2025-11-26 09:00:00.000000

Creates tables for the Customers domain (CRM):
- customers: Main customer table with PII encryption
- customer_notes: Internal notes on customers
- customer_interactions: Interaction timeline log
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    """
    Create customers domain tables.
    """
    # ========================================================================
    # CREATE CUSTOMERS TABLE
    # ========================================================================

    op.create_table(
        'customers',
        sa.Column('id', sa.BigInteger(), nullable=False),

        # Basic Info
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(500), nullable=False),  # Encrypted
        sa.Column('phone', sa.String(500), nullable=True),  # Encrypted
        sa.Column('company_name', sa.String(255), nullable=True),
        sa.Column('company_vat_id', sa.String(50), nullable=True),
        sa.Column('company_website', sa.String(255), nullable=True),

        # Address
        sa.Column('address_line1', sa.String(255), nullable=True),
        sa.Column('address_line2', sa.String(255), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state_province', sa.String(100), nullable=True),
        sa.Column('postal_code', sa.String(20), nullable=True),
        sa.Column('country', sa.String(2), nullable=False, server_default='IT'),

        # CRM Fields
        sa.Column('status', sa.String(50), nullable=False, server_default='lead'),
        sa.Column('customer_type', sa.String(50), nullable=False, server_default='individual'),
        sa.Column('source', sa.String(50), nullable=False, server_default='website'),
        sa.Column('assigned_to', sa.BigInteger(), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),

        # Financial Tracking
        sa.Column('lifetime_value', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('total_spent', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('avg_deal_size', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('completed_projects', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_purchase_date', sa.Date(), nullable=True),

        # Engagement Tracking
        sa.Column('last_contact_date', sa.DateTime(), nullable=True),
        sa.Column('last_contact_type', sa.String(50), nullable=True),
        sa.Column('next_followup_date', sa.Date(), nullable=True),
        sa.Column('next_followup_notes', sa.Text(), nullable=True),

        # Privacy & Marketing
        sa.Column('marketing_consent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('marketing_consent_date', sa.DateTime(), nullable=True),

        # Audit Fields
        sa.Column('created_by', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),

        # Soft Delete
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_by', sa.BigInteger(), nullable=True),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_customers_email'),
        sa.ForeignKeyConstraint(['assigned_to'], ['admin_users.id'], name='fk_customers_assigned_to'),
        sa.ForeignKeyConstraint(['created_by'], ['admin_users.id'], name='fk_customers_created_by'),
        sa.ForeignKeyConstraint(['deleted_by'], ['admin_users.id'], name='fk_customers_deleted_by'),
        sa.CheckConstraint('lifetime_value >= 0', name='ck_customers_positive_ltv'),
        sa.CheckConstraint('total_spent >= 0', name='ck_customers_positive_spent'),
        sa.CheckConstraint('completed_projects >= 0', name='ck_customers_positive_projects'),
    )

    # Create indexes for customers table
    op.create_index('ix_customers_name', 'customers', ['name'])
    op.create_index('ix_customers_email', 'customers', ['email'])
    op.create_index('ix_customers_company_name', 'customers', ['company_name'])
    op.create_index('ix_customers_status', 'customers', ['status'])
    op.create_index('ix_customers_source', 'customers', ['source'])
    op.create_index('ix_customers_is_deleted', 'customers', ['is_deleted'])
    op.create_index('ix_customers_created_at', 'customers', ['created_at'])

    # ========================================================================
    # CREATE CUSTOMER_NOTES TABLE
    # ========================================================================

    op.create_table(
        'customer_notes',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('customer_id', sa.BigInteger(), nullable=False),
        sa.Column('note', sa.Text(), nullable=False),
        sa.Column('created_by', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['customer_id'],
            ['customers.id'],
            name='fk_customer_notes_customer',
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['created_by'],
            ['admin_users.id'],
            name='fk_customer_notes_created_by'
        ),
    )

    # Create indexes
    op.create_index('ix_customer_notes_customer_id', 'customer_notes', ['customer_id'])
    op.create_index('ix_customer_notes_created_at', 'customer_notes', ['created_at'])

    # ========================================================================
    # CREATE CUSTOMER_INTERACTIONS TABLE
    # ========================================================================

    op.create_table(
        'customer_interactions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('customer_id', sa.BigInteger(), nullable=False),
        sa.Column('interaction_type', sa.String(50), nullable=False),
        sa.Column('subject', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('outcome', sa.String(50), nullable=True),
        sa.Column('next_action', sa.Text(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['customer_id'],
            ['customers.id'],
            name='fk_customer_interactions_customer',
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['created_by'],
            ['admin_users.id'],
            name='fk_customer_interactions_created_by'
        ),
    )

    # Create indexes
    op.create_index('ix_customer_interactions_customer_id', 'customer_interactions', ['customer_id'])
    op.create_index('ix_customer_interactions_created_at', 'customer_interactions', ['created_at'])
    op.create_index('ix_customer_interactions_interaction_type', 'customer_interactions', ['interaction_type'])


def downgrade():
    """
    Drop customers domain tables.
    """
    # Drop tables in reverse order (dependencies first)
    op.drop_table('customer_interactions')
    op.drop_table('customer_notes')
    op.drop_table('customers')
