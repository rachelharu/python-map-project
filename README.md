# Spatial Intel

Spatial Intel is a geospatial migration viewer. It ingests U.S. Census ACS
migration-flow data, stores county geometry and migration summaries in
PostgreSQL/PostGIS, and serves a FastAPI API used by a SvelteKit + MapLibre map.

The current MVP lets a user click a U.S. county and view:

- moved in
- moved out
- net migration
- ACS migration-flow period

## Tech Stack

Backend:

- Python + FastAPI
- PostgreSQL / Neon
- PostGIS
- SQLAlchemy / GeoAlchemy2
- Alembic

Frontend:

- SvelteKit
- TypeScript
- MapLibre GL JS

## Data

The MVP uses the Census ACS Migration Flows API. The currently loaded period is
`2016-2020`, using the `2020` ACS migration-flow endpoint.

For the displayed county summary:

```text
moved_in = aggregated Census MOVEDIN
moved_out = aggregated Census MOVEDOUT
net_migration = moved_in - moved_out
```

County geometry is loaded separately from Census cartographic boundary data into
the `counties` PostGIS table.

## API

Current MVP endpoints:

```text
GET /
GET /counties/in-bbox
GET /metadata/migration-periods
GET /migration/counties/{geoid}?period=2016-2020
```

Older `/events` endpoints still exist as a reference pattern, but they are not
the active MVP path.

## Running Locally

### Requirements

- Python 3.11+
- Node.js matching `.nvmrc`
- PostgreSQL with PostGIS enabled, or the existing Neon database
- `backend/.env` with:

```bash
DATABASE_URL=...
CENSUS_API_KEY=...
```

The Census ACS migration-flow endpoint requires an API key. You can request one
from Census here:

```text
https://api.census.gov/data/key_signup.html
```

### Backend Setup

From the repo root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Apply migrations:

```bash
cd backend
alembic upgrade head
```

Load migration data:

```bash
python scripts/ingest_migration_flows.py --source-year 2020
```

Start the backend:

```bash
cd ..
uvicorn backend.app.main:app --reload
```

### Frontend Setup

```bash
cd frontend/web
npm install
npm run dev
```

The frontend expects `frontend/web/.env` to point at the FastAPI backend:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Testing

Backend:

```bash
pytest
```

Frontend:

```bash
cd frontend/web
npm run check
npm run build
```

## Known Limitations

- Only `2016-2020` migration-flow data is currently loaded.
- The ingest skips counties whose Census flow GEOIDs do not match the loaded
  county geometry table. This currently affects a small number of rows because
  the flow data and geometry file use different boundary vintages.
- ACS migration flows are estimates over a 5-year period, not exact annual
  counts.
- The current UI shows county-level totals only. Origin and destination
  breakdowns are future work.
