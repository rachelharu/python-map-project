# Deployment

This project is intended to deploy as two services:

- Frontend: Vercel, built from `frontend/web`
- Backend API: Render, built from the production API `Dockerfile`
- Database: existing Neon PostgreSQL/PostGIS database

Keep migrations and data ingest separate from the normal web-service start
command. The app should start quickly and only serve API traffic.

## Backend API

The Dockerfile start command is equivalent to:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

Required environment variables:

```bash
DATABASE_URL=your_neon_postgres_url
CENSUS_API_KEY=your_census_api_key
CORS_ORIGINS=https://your-frontend-domain.vercel.app
```

`CORS_ORIGINS` accepts a comma-separated list if more than one frontend origin
needs access.

### Render

The repo includes `render.yaml` for the API service. It uses `runtime: docker`,
so Render builds the production image from the root `Dockerfile`. In Render, set
`DATABASE_URL`, `CENSUS_API_KEY`, and `CORS_ORIGINS` in the service environment.

Run migrations as a one-off shell command before relying on the deployed API:

```bash
cd backend
alembic upgrade head
```

Do not put `alembic upgrade head` in the normal start command.

## Docker

The repo includes a production API `Dockerfile`.

Build it from the repo root:

```bash
docker build -t spatial-intel-api .
```

Run it locally:

```bash
docker run --rm -p 8000:8000 \
  -e DATABASE_URL=your_neon_postgres_url \
  -e CORS_ORIGINS=http://localhost:5173 \
  spatial-intel-api
```

The Docker image installs `requirements-api.txt`, which includes the runtime
dependencies needed to serve the API, including GeoAlchemy2 and Shapely.
GeoPandas is intentionally not included in the production image because it is
only needed by `backend/scripts/load_counties.py` for local/data-loading work.

If you want to run Alembic inside the container as a one-off task, use:

```bash
docker run --rm \
  -e DATABASE_URL=your_neon_postgres_url \
  spatial-intel-api \
  sh -c "cd backend && alembic upgrade head"
```

Do not run the county geometry loader from this production image unless the
image is expanded to include the data-loading dependencies from
`requirements.txt`.

## Frontend

Deploy `frontend/web` as the Vercel project root.

Recommended settings:

```text
Root Directory: frontend/web
Install Command: npm install
Build Command: npm run build
Output Directory: build
```

Required frontend environment variable:

```bash
VITE_API_BASE_URL=https://your-api-domain.onrender.com
```

After the frontend URL is known, update the backend `CORS_ORIGINS` value to the
exact Vercel origin.

## Database

Neon remains the production database.

Before smoke testing, confirm:

- PostGIS extension exists
- Alembic migrations have been applied
- `counties` contains county geometries
- `county_migration_summaries` contains `2016-2020` migration summaries

Useful checks:

```sql
select count(*) from counties;
select period, count(*) from county_migration_summaries group by period order by period;
select count(*) as bad_net_rows
from county_migration_summaries
where net_migration <> moved_in - moved_out;
```

## Smoke Test

After both services are deployed:

1. Open `GET /` on the deployed API. It should return `status: running`.
2. Open `GET /metadata/migration-periods`. It should include `2016-2020`.
3. Open the deployed frontend.
4. Click Los Angeles County, CA.
5. Confirm the panel shows:

```text
Migration gain: 297,004
Migration loss: 348,525
Net loss: -51,521
```

The human sentence should read:

```text
51,521 more people moved out than in.
```
