# Spatial Intel

Spatial Intel is a FastAPI geospatial API with a Svelte/MapLibre map frontend.
It uses U.S. Census ACS migration-flow data to show county-level migration gain,
loss, and net movement.

The MVP interaction is simple:

1. Open the map.
2. Click a U.S. county.
3. View how many people moved in, how many moved out, and whether the county had
   a net gain or net loss during the selected ACS period.

## What It Shows

For each selected county, the app displays:

- **Migration gain**: people who moved into the county
- **Migration loss**: people who moved out of the county
- **Net gain/loss**: migration gain minus migration loss
- **ACS period**: currently `2016-2020`

Example:

```text
Los Angeles County, CA
Net loss: -51,521
Migration gain: 297,004
Migration loss: 348,525
```

## Tech Stack

Backend:

- Python
- FastAPI
- PostgreSQL / Neon
- PostGIS
- SQLAlchemy / GeoAlchemy2
- Alembic

Frontend:

- SvelteKit
- TypeScript
- MapLibre GL JS

## Data Source

The MVP uses the Census ACS Migration Flows API.

Currently loaded:

```text
2020 ACS migration-flow endpoint -> 2016-2020 ACS period
```

The app stores county summaries as:

```text
moved_in = aggregated Census MOVEDIN
moved_out = aggregated Census MOVEDOUT
net_migration = moved_in - moved_out
```

County geometry is loaded separately into the `counties` PostGIS table.

## API Endpoints

Current MVP endpoints:

```text
GET /
GET /counties/in-bbox
GET /metadata/migration-periods
GET /migration/counties/{geoid}?period=2016-2020
```

Older `/events` endpoints still exist as a reference pattern, but they are not
the active MVP path.

## Local Setup

### 1. Backend Environment

From the repo root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env`:

```bash
DATABASE_URL=your_postgres_url
CENSUS_API_KEY=your_census_api_key
```

You can request a Census API key here:

```text
https://api.census.gov/data/key_signup.html
```

### 2. Database

Run migrations:

```bash
cd backend
alembic upgrade head
```

If county geometry is not loaded yet, load it:

```bash
python scripts/load_counties.py
```

Load ACS migration-flow summaries:

```bash
python scripts/ingest_migration_flows.py --source-year 2020
```

### 3. Start Backend

From the repo root:

```bash
uvicorn backend.app.main:app --reload
```

Or, from inside `backend/`:

```bash
uvicorn app.main:app --reload
```

The backend runs at:

```text
http://127.0.0.1:8000
```

### 4. Start Frontend

In another terminal:

```bash
cd frontend/web
npm install
npm run dev
```

The frontend expects this in `frontend/web/.env`:

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

## Deployment

Recommended MVP deployment:

- Frontend: Vercel
- Backend API: Render
- Database: Neon PostgreSQL/PostGIS

The Render backend uses the production API `Dockerfile`. Its start command is
equivalent to:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

Run Alembic migrations as a one-off deployment step, not as part of normal app
startup:

```bash
cd backend
alembic upgrade head
```

Deployment notes and smoke-test steps are in
[`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

The repo also includes a production API `Dockerfile`. It uses
`requirements-api.txt`, which intentionally excludes GeoPandas because the
production API serves already-loaded PostGIS data. Use `requirements.txt` for
local development and data-loading scripts.

## Known Limitations

- Only the `2016-2020` ACS migration-flow period is currently loaded.
- ACS migration flows are 5-year estimates, not exact annual counts.
- The current UI shows county-level totals only. It does not yet show top origin
  or destination counties.
- A small number of Census flow summaries are skipped when their GEOIDs do not
  match the loaded county geometry vintage.
