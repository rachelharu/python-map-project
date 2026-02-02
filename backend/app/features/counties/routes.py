from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping

from ...db import get_db
from .models import County

router = APIRouter(prefix="/counties", tags=["counties"])

@router.get("/in-bbox")
def list_counties_in_bbox(
    west: float,
    south: float,
    east: float,
    north: float,
    limit: int = 500,
    db: Session = Depends(get_db),
):
    envelope = func.ST_MakeEnvelope(west, south, east, north, 4326)
    
    counties = (
        db.query(County)
        .filter(func.ST_Intersects(County.geom, envelope))
        .limit(limit)
        .all()
    )
    
    features = []
    for c in counties:
        features.append({
            "type": "Feature",
            "properties": {"geoid": c.geoid, "name": c.name},
            "geometry": mapping(to_shape(c.geom)),  
        })
        
    return {"type": "FeatureCollection", "features": features}