# Spatial Intel API

A backend service for ingesting geospatial events and performing
spatial + temporal analysis over them.

This project focuses on:
- storing real-world events with location + time
- querying them efficiently by map bounds
- detecting changes in activity over time
- returning map-native GeoJSON outputs

The API is designed to act as the "intelligence layer" behind a map UI.

---

## Tech Stack

- Python + FastAPI
- PostgreSQL (Neon)
- PostGIS
- SQLAlchemy / GeoAlchemy2

---

## What It Currently Does

The API currently supports:

- Ingesting point-based events (`POST /events`)
- Querying events within a map bounding box
- Querying events within a bounding box + time window
- Detecting changes in activity over time within a region

All spatial responses are returned as GeoJSON.

---

## Running Locally

### Requirements
- Python 3.11+
- PostgreSQL with PostGIS enabled
- `.env` file with a valid `DATABASE_URL`


### Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

### Start
#### backend:
uvicorn backend.app.main:app --reload

GET /events/in-bbox

GET /events/changes-in-bbox

#### frontend:
cd frontend/web

npm run dev
