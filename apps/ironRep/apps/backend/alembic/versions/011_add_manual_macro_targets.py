"""Add manual macro targets to users table

Revision ID: 011_add_manual_macro_targets
Revises: 010_add_google_accounts
Create Date: 2025-12-20

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "011_add_manual_macro_targets"
down_revision = "010_add_google_accounts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_cols = {c["name"] for c in inspector.get_columns("users")}

    if "manual_target_calories" not in existing_cols:
        op.add_column(
            "users",
            sa.Column(
                "manual_target_calories",
                sa.Integer(),
                nullable=True,
                comment="Manual daily calorie target (kcal) for self-managed nutrition mode",
            ),
        )

    if "manual_target_protein_g" not in existing_cols:
        op.add_column(
            "users",
            sa.Column(
                "manual_target_protein_g",
                sa.Integer(),
                nullable=True,
                comment="Manual daily protein target (g) for self-managed nutrition mode",
            ),
        )

    if "manual_target_carbs_g" not in existing_cols:
        op.add_column(
            "users",
            sa.Column(
                "manual_target_carbs_g",
                sa.Integer(),
                nullable=True,
                comment="Manual daily carbs target (g) for self-managed nutrition mode",
            ),
        )

    if "manual_target_fat_g" not in existing_cols:
        op.add_column(
            "users",
            sa.Column(
                "manual_target_fat_g",
                sa.Integer(),
                nullable=True,
                comment="Manual daily fat target (g) for self-managed nutrition mode",
            ),
        )


def downgrade() -> None:
    op.drop_column("users", "manual_target_fat_g")
    op.drop_column("users", "manual_target_carbs_g")
    op.drop_column("users", "manual_target_protein_g")
    op.drop_column("users", "manual_target_calories")
