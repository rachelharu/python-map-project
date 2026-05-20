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
    offset: int = 0,
    simplify: float | None = None,
    db: Session = Depends(get_db),
):
    envelope = func.ST_MakeEnvelope(west, south, east, north, 4326)

    max_limit = 2000
    limit = max(1, min(limit, max_limit))
    offset = max(0, offset)

    geom_expr = County.geom
    if simplify is not None and simplify > 0:
        geom_expr = func.ST_SimplifyPreserveTopology(County.geom, simplify)

    total = (
        db.query(func.count(County.geoid))
        .filter(func.ST_Intersects(County.geom, envelope))
        .scalar()
    )

    counties = (
        db.query(County.geoid, County.name, geom_expr.label("geom"))
        .filter(func.ST_Intersects(County.geom, envelope))
        .order_by(County.geoid)
        .offset(offset)
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

    has_more = (offset + len(features)) < (total or 0)
    return {
        "type": "FeatureCollection",
        "features": features,
        "meta": {
            "limit": limit,
            "offset": offset,
            "returned": len(features),
            "total": total,
            "has_more": has_more,
        },
    }
