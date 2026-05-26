"""create county migration summaries

Revision ID: b62f4a9d2c18
Revises: 8b1f9e9f0a2c
Create Date: 2026-05-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b62f4a9d2c18"
down_revision = "8b1f9e9f0a2c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "county_migration_summaries",
        sa.Column(
            "geoid",
            sa.Text(),
            sa.ForeignKey("counties.geoid", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("period", sa.Text(), nullable=False),
        sa.Column("source_year", sa.Integer(), nullable=False),
        sa.Column("moved_in", sa.Integer(), nullable=False),
        sa.Column("moved_out", sa.Integer(), nullable=False),
        sa.Column("net_migration", sa.Integer(), nullable=False),
        sa.Column("moved_in_moe", sa.Integer(), nullable=True),
        sa.Column("moved_out_moe", sa.Integer(), nullable=True),
        sa.Column("net_migration_moe", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("geoid", "period", name="pk_county_migration_summaries"),
    )
    op.create_index(
        "ix_county_migration_summaries_period",
        "county_migration_summaries",
        ["period"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_county_migration_summaries_period",
        table_name="county_migration_summaries",
    )
    op.drop_table("county_migration_summaries")
