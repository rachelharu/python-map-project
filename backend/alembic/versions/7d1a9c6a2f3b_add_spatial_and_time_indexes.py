"""add spatial and time indexes

Revision ID: 7d1a9c6a2f3b
Revises: 30c1894b7f57
Create Date: 2026-02-06 00:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "7d1a9c6a2f3b"
down_revision = "30c1894b7f57"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_events_geom",
        "events",
        ["geom"],
        unique=False,
        postgresql_using="gist",
    )
    op.create_index(
        "ix_events_created_at",
        "events",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_acs_county_age_year_geoid",
        "acs_county_age",
        ["year", "geoid"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_acs_county_age_year_geoid", table_name="acs_county_age")
    op.drop_index("ix_events_created_at", table_name="events")
    op.drop_index("ix_events_geom", table_name="events")
