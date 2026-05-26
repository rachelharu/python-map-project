from sqlalchemy import Column, ForeignKey, Integer, Text

from ...db import Base


class CountyMigrationSummary(Base):
    __tablename__ = "county_migration_summaries"

    geoid = Column(
        Text,
        ForeignKey("counties.geoid", ondelete="CASCADE"),
        primary_key=True,
    )
    period = Column(Text, primary_key=True)
    source_year = Column(Integer, nullable=False)
    moved_in = Column(Integer, nullable=False)
    moved_out = Column(Integer, nullable=False)
    net_migration = Column(Integer, nullable=False)
    moved_in_moe = Column(Integer, nullable=True)
    moved_out_moe = Column(Integer, nullable=True)
    net_migration_moe = Column(Integer, nullable=True)
