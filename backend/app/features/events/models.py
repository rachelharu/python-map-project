from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, DateTime, func
from geoalchemy2 import Geometry

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    geom = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
