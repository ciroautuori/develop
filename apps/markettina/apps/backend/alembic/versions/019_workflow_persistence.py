"""
019_workflow_persistence.py

MARKETTINA v2.0 - Workflow Persistence Migration
Creates workflow_definitions, workflow_executions, workflow_schedules tables.

Revision ID: 019
Revises: 018_analytics_advanced
Create Date: 2025-12-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '019_workflow_persistence'
down_revision = '018_analytics_advanced'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create workflow persistence tables."""

    # ========================================================================
    # WORKFLOW DEFINITIONS
    # ========================================================================

    op.create_table(
        'workflow_definitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Info
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        # Status
        sa.Column('status', sa.Enum('draft', 'active', 'paused', 'archived', name='workflowstatus'), nullable=False, server_default='draft'),
        # Trigger
        sa.Column('trigger_type', sa.Enum('manual', 'scheduled', 'event', 'webhook', 'api', name='triggertype'), nullable=False, server_default='manual'),
        sa.Column('trigger_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        # Steps
        sa.Column('steps', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        # Stats
        sa.Column('total_executions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('successful_executions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_executions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_execution_at', sa.DateTime(timezone=True), nullable=True),
        # Mixins
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE')
    )
    op.create_index('ix_workflow_definitions_account', 'workflow_definitions', ['account_id', 'status'])

    # ========================================================================
    # WORKFLOW EXECUTIONS
    # ========================================================================

    op.create_table(
        'workflow_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('triggered_by', sa.Integer(), nullable=True),
        # Status
        sa.Column('status', sa.Enum('pending', 'running', 'completed', 'failed', 'cancelled', 'retrying', name='executionstatus'), nullable=False, server_default='pending'),
        sa.Column('trigger_type', sa.Enum('manual', 'scheduled', 'event', 'webhook', 'api', name='triggertype_exec', create_type=False), nullable=False),
        # Progress
        sa.Column('current_step_id', sa.String(100), nullable=True),
        sa.Column('current_step_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_steps', sa.Integer(), nullable=False, server_default='0'),
        # Timing
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        # Results
        sa.Column('step_results', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('output', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_stack', sa.Text(), nullable=True),
        # Retry
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_retries', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('next_retry_at', sa.DateTime(timezone=True), nullable=True),
        # Input
        sa.Column('input_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('workflow_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflow_definitions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['triggered_by'], ['users.id'], ondelete='SET NULL')
    )
    op.create_index('ix_workflow_executions_workflow_status', 'workflow_executions', ['workflow_id', 'status'])
    op.create_index('ix_workflow_executions_account_date', 'workflow_executions', ['account_id', 'started_at'])

    # ========================================================================
    # WORKFLOW SCHEDULES
    # ========================================================================

    op.create_table(
        'workflow_schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Schedule
        sa.Column('cron_expression', sa.String(100), nullable=False),
        sa.Column('timezone', sa.String(50), nullable=False, server_default='Europe/Rome'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        # Tracking
        sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_run_status', sa.Enum('pending', 'running', 'completed', 'failed', 'cancelled', 'retrying', name='executionstatus_sched', create_type=False), nullable=True),
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflow_definitions.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('workflow_id', 'cron_expression', name='uq_workflow_schedule')
    )

    # ========================================================================
    # WORKFLOW STEP LOGS
    # ========================================================================

    op.create_table(
        'workflow_step_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('execution_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Step info
        sa.Column('step_id', sa.String(100), nullable=False),
        sa.Column('step_type', sa.String(100), nullable=False),
        sa.Column('step_name', sa.String(255), nullable=True),
        # Execution
        sa.Column('status', sa.Enum('pending', 'running', 'completed', 'failed', 'cancelled', 'retrying', name='executionstatus_log', create_type=False), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        # I/O
        sa.Column('input_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('output_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        # Errors
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_code', sa.String(100), nullable=True),
        # Metrics
        sa.Column('tokens_consumed', sa.Integer(), nullable=True),
        sa.Column('api_calls_made', sa.Integer(), nullable=True),
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['execution_id'], ['workflow_executions.id'], ondelete='CASCADE')
    )
    op.create_index('ix_workflow_step_logs_execution', 'workflow_step_logs', ['execution_id', 'step_id'])


def downgrade() -> None:
    """Drop workflow tables."""
    op.drop_table('workflow_step_logs')
    op.drop_table('workflow_schedules')
    op.drop_table('workflow_executions')
    op.drop_table('workflow_definitions')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS workflowstatus")
    op.execute("DROP TYPE IF EXISTS triggertype")
    op.execute("DROP TYPE IF EXISTS executionstatus")
