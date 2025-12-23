"""create_quotes_domain_tables

Revision ID: 008_quotes_domain
Revises: 007_customers_domain
Create Date: 2025-11-26 09:20:00.000000

Creates tables for the Quotes domain (Preventivi):
- quotes: Main quote table with financial calculations
- quote_line_items: Line items for quotes
- quote_versions: Version history for audit
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    """
    Create quotes domain tables.
    """
    # ========================================================================
    # CREATE QUOTES TABLE
    # ========================================================================

    op.create_table(
        'quotes',
        sa.Column('id', sa.BigInteger(), nullable=False),

        # Quote Identification
        sa.Column('quote_number', sa.String(50), nullable=False, unique=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),

        # Customer Relationship
        sa.Column('customer_id', sa.BigInteger(), nullable=False),

        # Versioning
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_latest', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('parent_quote_id', sa.BigInteger(), nullable=True),

        # Financial
        sa.Column('currency', sa.String(3), nullable=False, server_default='EUR'),
        sa.Column('subtotal', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('tax_rate', sa.Numeric(5, 2), nullable=False, server_default='22.00'),
        sa.Column('tax_amount', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('discount_percentage', sa.Numeric(5, 2), nullable=False, server_default='0.00'),
        sa.Column('discount_amount', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('total', sa.Numeric(10, 2), nullable=False, server_default='0.00'),

        # Validity & Dates
        sa.Column('issue_date', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')),
        sa.Column('valid_until', sa.Date(), nullable=False),
        sa.Column('payment_terms_days', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('delivery_date', sa.Date(), nullable=True),

        # Status Tracking
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('viewed_at', sa.DateTime(), nullable=True),
        sa.Column('accepted_at', sa.DateTime(), nullable=True),
        sa.Column('accepted_by_name', sa.String(255), nullable=True),
        sa.Column('accepted_by_email', sa.String(255), nullable=True),
        sa.Column('rejected_at', sa.DateTime(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),

        # Terms & Conditions
        sa.Column('payment_terms', sa.Text(), nullable=True),
        sa.Column('terms_and_conditions', sa.Text(), nullable=True),
        sa.Column('notes_to_customer', sa.Text(), nullable=True),
        sa.Column('internal_notes', sa.Text(), nullable=True),

        # PDF
        sa.Column('pdf_file_path', sa.String(500), nullable=True),
        sa.Column('pdf_generated_at', sa.DateTime(), nullable=True),

        # Audit
        sa.Column('created_by', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),

        # Soft Delete
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_by', sa.BigInteger(), nullable=True),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('quote_number', name='uq_quotes_quote_number'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], name='fk_quotes_customer'),
        sa.ForeignKeyConstraint(['parent_quote_id'], ['quotes.id'], name='fk_quotes_parent'),
        sa.ForeignKeyConstraint(['created_by'], ['admin_users.id'], name='fk_quotes_created_by'),
        sa.ForeignKeyConstraint(['deleted_by'], ['admin_users.id'], name='fk_quotes_deleted_by'),
        sa.CheckConstraint('subtotal >= 0', name='ck_quotes_positive_subtotal'),
        sa.CheckConstraint('tax_rate >= 0 AND tax_rate <= 100', name='ck_quotes_valid_tax_rate'),
        sa.CheckConstraint('discount_percentage >= 0 AND discount_percentage <= 100', name='ck_quotes_valid_discount'),
        sa.CheckConstraint('total >= 0', name='ck_quotes_positive_total'),
        sa.CheckConstraint('version >= 1', name='ck_quotes_positive_version'),
        sa.CheckConstraint('payment_terms_days >= 0', name='ck_quotes_positive_payment_terms'),
    )

    # Create indexes
    op.create_index('ix_quotes_quote_number', 'quotes', ['quote_number'])
    op.create_index('ix_quotes_customer_id', 'quotes', ['customer_id'])
    op.create_index('ix_quotes_status', 'quotes', ['status'])
    op.create_index('ix_quotes_is_latest', 'quotes', ['is_latest'])
    op.create_index('ix_quotes_valid_until', 'quotes', ['valid_until'])
    op.create_index('ix_quotes_is_deleted', 'quotes', ['is_deleted'])
    op.create_index('ix_quotes_created_at', 'quotes', ['created_at'])

    # ========================================================================
    # CREATE QUOTE_LINE_ITEMS TABLE
    # ========================================================================

    op.create_table(
        'quote_line_items',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('quote_id', sa.BigInteger(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),

        # Item Details
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sku', sa.String(100), nullable=True),

        # Pricing
        sa.Column('quantity', sa.Numeric(10, 2), nullable=False, server_default='1.00'),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('discount_percentage', sa.Numeric(5, 2), nullable=False, server_default='0.00'),
        sa.Column('discount_amount', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('subtotal', sa.Numeric(10, 2), nullable=False, server_default='0.00'),

        # Metadata
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['quote_id'],
            ['quotes.id'],
            name='fk_quote_line_items_quote',
            ondelete='CASCADE'
        ),
        sa.CheckConstraint('quantity > 0', name='ck_line_items_positive_quantity'),
        sa.CheckConstraint('unit_price >= 0', name='ck_line_items_non_negative_price'),
        sa.CheckConstraint('discount_percentage >= 0 AND discount_percentage <= 100', name='ck_line_items_valid_discount'),
        sa.CheckConstraint('subtotal >= 0', name='ck_line_items_positive_subtotal'),
    )

    # Create indexes
    op.create_index('ix_quote_line_items_quote_id', 'quote_line_items', ['quote_id'])
    op.create_index('ix_quote_line_items_position', 'quote_line_items', ['position'])

    # ========================================================================
    # CREATE QUOTE_VERSIONS TABLE
    # ========================================================================

    op.create_table(
        'quote_versions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('original_quote_id', sa.BigInteger(), nullable=False),
        sa.Column('new_quote_id', sa.BigInteger(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('changes_summary', sa.Text(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_by', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['original_quote_id'],
            ['quotes.id'],
            name='fk_quote_versions_original'
        ),
        sa.ForeignKeyConstraint(
            ['new_quote_id'],
            ['quotes.id'],
            name='fk_quote_versions_new'
        ),
        sa.ForeignKeyConstraint(
            ['created_by'],
            ['admin_users.id'],
            name='fk_quote_versions_created_by'
        ),
    )

    # Create indexes
    op.create_index('ix_quote_versions_original_quote_id', 'quote_versions', ['original_quote_id'])
    op.create_index('ix_quote_versions_new_quote_id', 'quote_versions', ['new_quote_id'])


def downgrade():
    """
    Drop quotes domain tables.
    """
    op.drop_table('quote_versions')
    op.drop_table('quote_line_items')
    op.drop_table('quotes')
