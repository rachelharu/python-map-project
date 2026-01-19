# Spatial Intel API

Data analysis project focused on detecting and visualizing geographic trends over time across the United States.

The system is designed to ingest real-world datasets, store them in a spatial database (PostGIS), and expose APIs for querying change across space and time. A web frontend visualizes these trends on an interactive map.

---

## Tech Stack
**Backend**
- Python + FastAPI
- PostgreSQL (Neon)
- PostGIS
- SQLAlchemy / GeoAlchemy2

---

**Frontend**
- SvelteKit
- TypeScript
- MapLibre GL JS

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
