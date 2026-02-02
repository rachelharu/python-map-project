from sqlalchemy import Column, Text
from geoalchemy2 import Geometry
from ...db import Base

class County(Base):
    __tablename__ = "counties"
    geoid = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    state_fips = Column(Text, nullable=True)
    geom = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False)