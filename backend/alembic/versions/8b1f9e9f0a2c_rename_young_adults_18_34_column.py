"""rename young_adults_18_34 column

Revision ID: 8b1f9e9f0a2c
Revises: 7d1a9c6a2f3b
Create Date: 2026-02-10 00:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "8b1f9e9f0a2c"
down_revision = "7d1a9c6a2f3b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "acs_county_age",
        "young_adults_18_34",
        new_column_name="adults_18_34",
    )


def downgrade() -> None:
    op.alter_column(
        "acs_county_age",
        "adults_18_34",
        new_column_name="young_adults_18_34",
    )
