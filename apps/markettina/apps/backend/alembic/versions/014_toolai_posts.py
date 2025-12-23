"""ToolAI daily posts feature

Revision ID: 014
Revises: 013_add_integration_toggles
Create Date: 2025-01-15

Tables created:
- toolai_posts: Daily AI tools discovery posts
- toolai_tools: Individual AI tools featured in posts
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '014_toolai_posts'
down_revision = '013_integration_toggles'
branch_labels = None
depends_on = None


def upgrade():
    # Check if table already exists
    connection = op.get_bind()

    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'toolai_posts')"
    ))
    table_exists = result.scalar()

    if table_exists:
        print("ToolAI tables already exist, skipping creation")
        return

    # Create toolai_posts table
    op.create_table(
        'toolai_posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft'),

        # Multi-language titles
        sa.Column('title_it', sa.String(length=255), nullable=False),
        sa.Column('title_en', sa.String(length=255), nullable=True),
        sa.Column('title_es', sa.String(length=255), nullable=True),

        # Multi-language summaries
        sa.Column('summary_it', sa.Text(), nullable=False),
        sa.Column('summary_en', sa.Text(), nullable=True),
        sa.Column('summary_es', sa.Text(), nullable=True),

        # Multi-language content
        sa.Column('content_it', sa.Text(), nullable=False),
        sa.Column('content_en', sa.Text(), nullable=True),
        sa.Column('content_es', sa.Text(), nullable=True),

        # Multi-language insights
        sa.Column('insights_it', sa.Text(), nullable=True),
        sa.Column('insights_en', sa.Text(), nullable=True),
        sa.Column('insights_es', sa.Text(), nullable=True),

        # Multi-language takeaway
        sa.Column('takeaway_it', sa.Text(), nullable=True),
        sa.Column('takeaway_en', sa.Text(), nullable=True),
        sa.Column('takeaway_es', sa.Text(), nullable=True),

        # SEO metadata
        sa.Column('meta_description', sa.String(length=160), nullable=True),
        sa.Column('meta_keywords', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('slug', sa.String(length=255), nullable=True),

        # Featured image
        sa.Column('image_url', sa.String(length=512), nullable=True),

        # AI generation metadata
        sa.Column('ai_generated', sa.Boolean(), default=True),
        sa.Column('ai_model', sa.String(length=100), nullable=True),
        sa.Column('generation_time', sa.Integer(), nullable=True),

        # Publishing
        sa.Column('published_at', sa.DateTime(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),

        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for toolai_posts
    op.create_index('ix_toolai_posts_id', 'toolai_posts', ['id'])
    op.create_index('ix_toolai_posts_post_date', 'toolai_posts', ['post_date'], unique=True)
    op.create_index('ix_toolai_posts_slug', 'toolai_posts', ['slug'], unique=True)
    op.create_index('ix_toolai_posts_status_date', 'toolai_posts', ['status', 'post_date'])

    # Create toolai_tools table
    op.create_table(
        'toolai_tools',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),

        # Tool info
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('source_url', sa.String(length=512), nullable=True),

        # Multi-language descriptions
        sa.Column('description_it', sa.Text(), nullable=False),
        sa.Column('description_en', sa.Text(), nullable=True),
        sa.Column('description_es', sa.Text(), nullable=True),

        # Multi-language relevance
        sa.Column('relevance_it', sa.Text(), nullable=True),
        sa.Column('relevance_en', sa.Text(), nullable=True),
        sa.Column('relevance_es', sa.Text(), nullable=True),

        # Category and tags
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),

        # Metrics
        sa.Column('stars', sa.Integer(), nullable=True),
        sa.Column('downloads', sa.Integer(), nullable=True),
        sa.Column('trending_score', sa.Integer(), nullable=True),

        # Display order
        sa.Column('display_order', sa.Integer(), default=0),

        # Timestamp
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(['post_id'], ['toolai_posts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for toolai_tools
    op.create_index('ix_toolai_tools_id', 'toolai_tools', ['id'])
    op.create_index('ix_toolai_tools_category', 'toolai_tools', ['category'])
    op.create_index('ix_toolai_tools_post_order', 'toolai_tools', ['post_id', 'display_order'])


def downgrade():
    # Drop tables
    op.drop_table('toolai_tools')
    op.drop_table('toolai_posts')

    # Drop enum
    op.execute("DROP TYPE toolaipoststatus")
