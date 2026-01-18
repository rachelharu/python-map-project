from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
from datetime import datetime

from app.db import get_db
from app.features.events.models import Event
from app.features.events.schemas import EventCreate

router = APIRouter(prefix="/events", tags=["events"])

@router.post("")
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    #store as WGS84 point (SRID 4326)
    wkt = f"POINT({payload.lon} {payload.lat})"
    ev = Event(geom=f"SRID=4326;{wkt}")
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return {"id": ev.id}

@router.get("/in-bbox-time")
def list_events_in_bbox_time(
    west: float,
    south: float,
    east: float,
    north: float,
    start: datetime,
    end: datetime,
    limit: int = 200,
    db: Session = Depends(get_db),
):
    envelope = func.ST_MakeEnvelope(west, south, east, north, 4326)
    
    events = (
        db.query(Event)
        .filter(func.ST_Intersects(Event.geom, envelope))
        .filter(Event.created_at >= start)
        .filter(Event.created_at < end)
        .order_by(Event.id.desc())
        .limit(limit)
        .all()
    )
    
    features = []
    for ev in events:
        geom_shape = to_shape(ev.geom)
        features.append({
            "type": "Feature",
            "properties": {"id": ev.id, "created_at": ev.created_at.isoformat()},
            "geometry": mapping(geom_shape),
        })
    
    return {"type": "FeatureCollection", "features": features}
    

@router.get("/in-bbox")
def list_event_in_bbox(
    west: float,
    south: float,
    east: float,
    north: float,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    envelope = func.ST_MakeEnvelope(west, south, east, north, 4326)
    
    events = (
        db.query(Event)
        .filter(func.ST_Intersects(Event.geom, envelope))
        .order_by(Event.id.desc())
        .limit(limit)
        .all()
    )
    
    features = []
    for ev in events:
        geom_shape = to_shape(ev.geom)
        features.append({
            "type": "Feature",
            "properties": {"id": ev.id},
            "geometry": mapping(geom_shape),
        })
        
    return {"type": "FeatureCollection", "features": features}

@router.get("")
def list_events(limit: int = 100, db: Session = Depends(get_db)):
    events = db.query(Event).order_by(Event.id.desc()).limit(limit).all()
    
    features = []
    for ev in events:
       geom_shape = to_shape(ev.geom)
       features.append({
           "type": "Feature",
           "properties": {"id": ev.id},
           "geometry": mapping(geom_shape),
       })
       
    return {"type": "FeatureCollection", "features": features}

@router.get("/health")
def health(db: Session = Depends(get_db)):
    # Quick DB check
    db.execute(text("SELECT 1"))
    return {"ok": True}

# from sqlalchemy import text

# @router.get("/where-am-i")
# def where_am_i(db: Session = Depends(get_db)):
#     row = db.execute(text("select inet_server_addr() as addr, current_database() as db, current_user as usr")).mappings().one()
#     return dict(row)
 

# @router.get("/postgis-check")
# def postgis_check(db: Session = Depends(get_db)):
#     row = db.execute(text("select postgis_version() as v")).mappings().one()
#     return dict(row)
