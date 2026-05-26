# Spatial Intel API

Data analysis project focused on detecting and visualizing geographic movement across the United States.

The system is designed to ingest real-world migration datasets, store them in a spatial database (PostGIS), and expose APIs for querying movement by county. A web frontend visualizes these numbers on an interactive map.

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

The MVP supports:

- Loading county geometries into PostGIS
- Ingesting ACS county migration-flow summaries
- Querying counties within a map bounding box
- Selecting a county and viewing moved-in, moved-out, and net migration numbers

County geometry responses are returned as GeoJSON.

---

## Running Locally

### Requirements
- Python 3.11+
- PostgreSQL with PostGIS enabled
- `backend/.env` file with a valid `DATABASE_URL`


### Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

### Testing
```bash
pip install pytest
pytest
```

### Start
#### backend:
uvicorn backend.app.main:app --reload


#### frontend:
cd frontend/web

npm run dev

#### database changes:
cd backend

alembic upgrade head

#### migration data:
Set `CENSUS_API_KEY` in `backend/.env`, then run from the repo root:

```bash
python backend/scripts/ingest_migration_flows.py --source-year 2020
```

Or, if your shell is already in `backend/`:

```bash
python scripts/ingest_migration_flows.py --source-year 2020
```

The Census ACS migration flows API requires a key for this endpoint.
