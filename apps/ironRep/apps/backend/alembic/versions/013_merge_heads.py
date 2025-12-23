"""Merge heads 009 and 012_food_fav_fs_id

Revision ID: 013_merge_heads
Revises: 009, 012_food_fav_fs_id
Create Date: 2025-12-20

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "013_merge_heads"
down_revision = ("009", "012_food_fav_fs_id")
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Merge revision: no-op
    pass


def downgrade() -> None:
    # Merge revision: no-op
    pass
