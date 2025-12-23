"""Remove food_cache and store favorites by fatsecret_id

Revision ID: 012_food_fav_fs_id
Revises: 011_add_manual_macro_targets
Create Date: 2025-12-20

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "012_food_fav_fs_id"
down_revision = "011_add_manual_macro_targets"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop legacy food_cache table if present
    op.execute("DROP TABLE IF EXISTS food_cache CASCADE")

    # Update favorites table to store fatsecret_id directly
    # Remove old unique constraint (if it exists)
    op.execute("ALTER TABLE user_favorite_foods DROP CONSTRAINT IF EXISTS unique_user_food")

    # Drop legacy food_id column (if present)
    op.execute("ALTER TABLE user_favorite_foods DROP COLUMN IF EXISTS food_id")

    # Add fatsecret_id column (if missing)
    op.execute(
        "ALTER TABLE user_favorite_foods "
        "ADD COLUMN IF NOT EXISTS fatsecret_id VARCHAR"
    )

    # Add index for lookups
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_user_favorite_foods_fatsecret_id "
        "ON user_favorite_foods (fatsecret_id)"
    )

    # Recreate unique constraint on (user_id, fatsecret_id)
    op.execute(
        "DO $$ BEGIN "
        "ALTER TABLE user_favorite_foods "
        "ADD CONSTRAINT unique_user_food UNIQUE (user_id, fatsecret_id); "
        "EXCEPTION WHEN duplicate_object THEN NULL; "
        "END $$;"
    )


def downgrade() -> None:
    # Best-effort downgrade: recreate minimal schema to restore old shape
    op.execute("ALTER TABLE user_favorite_foods DROP CONSTRAINT IF EXISTS unique_user_food")
    op.execute("DROP INDEX IF EXISTS ix_user_favorite_foods_fatsecret_id")

    op.execute("ALTER TABLE user_favorite_foods DROP COLUMN IF EXISTS fatsecret_id")

    op.add_column(
        "user_favorite_foods",
        sa.Column("food_id", sa.String(), nullable=True),
    )

    op.create_unique_constraint(
        "unique_user_food",
        "user_favorite_foods",
        ["user_id", "food_id"],
    )
