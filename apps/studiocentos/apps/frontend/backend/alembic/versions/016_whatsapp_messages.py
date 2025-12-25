"""Add whatsapp_messages table for WhatsApp Cloud API integration

Revision ID: 016_whatsapp_messages
Revises: 015_brand_settings
Create Date: 2025-12-05

Tables created:
- whatsapp_messages: Tracks WhatsApp messages sent via Cloud API
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '016_whatsapp_messages'
down_revision = '015_brand_settings'
branch_labels = None
depends_on = None


def upgrade():
    # Check if table already exists
    connection = op.get_bind()

    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'whatsapp_messages')"
    ))
    table_exists = result.scalar()

    if table_exists:
        print("whatsapp_messages table already exists, skipping creation")
        return

    # Create whatsapp_messages table
    op.create_table(
        'whatsapp_messages',
        sa.Column('id', sa.Integer(), nullable=False),

        # WhatsApp API identifiers
        sa.Column('waba_message_id', sa.String(100), unique=True, nullable=True,
                  comment='Message ID returned by WhatsApp API'),

        # Recipient info
        sa.Column('phone_number', sa.String(20), nullable=False,
                  comment='Recipient phone in international format (+39...)'),
        sa.Column('lead_id', sa.Integer(), nullable=True),

        # Message content
        sa.Column('message_type', sa.String(20), nullable=False, server_default='template'),
        sa.Column('template_name', sa.String(100), nullable=True,
                  comment='Template name if using template message'),
        sa.Column('template_language', sa.String(10), nullable=True, server_default='it',
                  comment='Template language code'),
        sa.Column('message_text', sa.Text(), nullable=True,
                  comment='Message text content or template parameters JSON'),

        # Status tracking
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('error_code', sa.String(50), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('read_at', sa.DateTime(), nullable=True),

        # Campaign tracking
        sa.Column('campaign_id', sa.String(50), nullable=True,
                  comment='Internal campaign ID for tracking'),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ondelete='SET NULL'),
    )

    # Create indexes
    op.create_index('ix_whatsapp_messages_id', 'whatsapp_messages', ['id'])
    op.create_index('ix_whatsapp_messages_status', 'whatsapp_messages', ['status'])
    op.create_index('idx_whatsapp_phone_status', 'whatsapp_messages', ['phone_number', 'status'])
    op.create_index('idx_whatsapp_campaign', 'whatsapp_messages', ['campaign_id'])
    op.create_index('idx_whatsapp_lead', 'whatsapp_messages', ['lead_id'])

    print("✅ whatsapp_messages table created successfully")


def downgrade():
    # Drop indexes
    op.drop_index('idx_whatsapp_lead', table_name='whatsapp_messages')
    op.drop_index('idx_whatsapp_campaign', table_name='whatsapp_messages')
    op.drop_index('idx_whatsapp_phone_status', table_name='whatsapp_messages')
    op.drop_index('ix_whatsapp_messages_status', table_name='whatsapp_messages')
    op.drop_index('ix_whatsapp_messages_id', table_name='whatsapp_messages')

    # Drop table
    op.drop_table('whatsapp_messages')

    print("✅ whatsapp_messages table dropped")
