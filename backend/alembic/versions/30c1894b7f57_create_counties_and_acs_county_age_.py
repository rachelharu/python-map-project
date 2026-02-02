"""create counties and acs county age tables

Revision ID: 30c1894b7f57
Revises: f3d7f4863368
Create Date: 2026-01-28 14:00:33.431178

"""
from alembic import op
import sqlalchemy as sa

revision = "30c1894b7f57"
down_revision = "f3d7f4863368"
branch_labels = None
depends_on = None

try:
    from geoalchemy2 import Geometry
except Exception:
    Geometry = None

def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    # --- counties ---
    if Geometry is not None:
        geom_type = Geometry(geometry_type="MULTIPOLYGON", srid=4326)
    else:
        # Fallback: still works with PostGIS installed
        geom_type = sa.Text()

    op.create_table(
        "counties",
        sa.Column("geoid", sa.Text(), primary_key=True),   # e.g. "06037"
        sa.Column("name", sa.Text(), nullable=False),      # e.g. "Los Angeles County, CA"
        sa.Column("state_fips", sa.Text(), nullable=True), # e.g. "06"
        sa.Column("geom", geom_type, nullable=False),
    )

    op.create_index(
        "ix_counties_geom",
        "counties",
        ["geom"],
        unique=False,
        postgresql_using="gist",
    )

    # --- acs_county_age ---
    op.create_table(
        "acs_county_age",
        sa.Column("geoid", sa.Text(), sa.ForeignKey("counties.geoid", ondelete="CASCADE"), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("young_adults_18_34", sa.Integer(), nullable=False),
        sa.Column("total_population", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("geoid", "year", name="pk_acs_county_age"),
    )

    op.create_index("ix_acs_county_age_year", "acs_county_age", ["year"], unique=False)
    op.create_index("ix_acs_county_age_geoid", "acs_county_age", ["geoid"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_acs_county_age_geoid", table_name="acs_county_age")
    op.drop_index("ix_acs_county_age_year", table_name="acs_county_age")
    op.drop_table("acs_county_age")

    op.drop_index("ix_counties_geom", table_name="counties")
    op.drop_table("counties")

    # Don't drop postgis extension in downgrade; it may be shared/managed!
