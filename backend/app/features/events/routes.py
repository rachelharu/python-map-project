from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
from datetime import datetime, timedelta, timezone

from ...db import get_db
from .models import Event
from .schemas import EventCreate

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

@router.get("/changes-in-bbox")
def changes_in_bbox(
    west: float,
    south: float,
    east: float,
    north: float,
    window_minutes: int = 60,
    db: Session = Depends(get_db),
):
    envelope = func.ST_MakeEnvelope(west, south, east, north, 4326)
    
    now = datetime.now(timezone.utc)
    window = timedelta(minutes=window_minutes)
    
    current_start = now - window
    current_end = now
    
    prev_start = now - (window * 2)
    prev_end = now - window
    
    current_count = (
        db.query(func.count(Event.id))
        .filter(func.ST_Intersects(Event.geom, envelope))
        .filter(Event.created_at >= current_start)
        .filter(Event.created_at < current_end)
        .scalar()
    )
    
    previous_count = (
        db.query(func.count(Event.id))
        .filter(func.ST_Intersects(Event.geom, envelope))
        .filter(Event.created_at >= prev_start)
        .filter(Event.created_at < prev_end)
        .scalar()
    )
    
    delta = int(current_count) - int(previous_count)
    trend = "flat"
    if int(previous_count) == 0 and int(current_count) > 0:
        trend = "new"
    elif delta > 0:
        trend = "up"
    elif delta < 0:
        trend = "down"

    pct_change = None
    if int(previous_count) > 0:
        pct_change = delta / int(previous_count)
    
    return {
        "bbox": {"west": west, "south": south, "east": east, "north": north},
        "window_minutes": window_minutes,
        "current": {
            "start": current_start.isoformat(),
            "end": current_end.isoformat(),
            "count": int(current_count),
        },
        "previous": {
            "start": prev_start.isoformat(),
            "end": prev_end.isoformat(),
            "count": int(previous_count),
        },
        "delta": delta,
        "pct_change": pct_change,  # e.g. 0.25 = +25%
        "trend": trend,
    }

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
