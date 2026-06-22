# Spatial Intel - Project Direction

This document exists to keep the project grounded and prevent scope drift.

## What This Project Is

Spatial Intel is a spatial analysis engine focused on how people move across
geography over time.

The first version is not a generic dashboard, a social analytics platform, or a
prediction tool. It should answer one concrete question well.

## v1 Goal

Display county-level migration movement for the selected U.S. county.

The MVP is complete when a user can click a county on the map and see:

- moved in
- moved out
- net migration
- the ACS migration-flow period behind those numbers

## Core Question v1 Answers

> "For this county, how many people moved in, how many moved out, and what was
> the net movement during the selected ACS migration-flow period?"

## Data Strategy

### v1 Dataset

- U.S. Census ACS Migration Flows
- First supported release: 2016-2020 ACS 5-year migration flows
- Geographic level: county
- Primary metric: migration movement, not population snapshots

This avoids the age-cohort issue from the earlier ACS population-count plan:
population change for adults 18-34 mixes migration with people aging into the
cohort, people aging out, deaths, and survey noise. Migration flows better match
the product idea because they estimate movement between current residence and
residence 1 year ago.

### Future

- Top origin counties
- Top destination counties
- State-to-county releases after 2020
- Age-specific migration if a supported flow release exposes the needed fields
- Choropleth styling by net migration
- Additional datasets such as housing, POIs, and demographics

## Current Technical State

### Backend

- FastAPI app exists
- Postgres + PostGIS running on Neon
- Alembic migrations working
- County geometries are modeled and queryable by bbox
- Migration summary table and selected-county API are being added
- Events endpoints still exist as an older reference pattern

### Frontend

- SvelteKit app exists
- MapLibre map renders county geometry
- The active MVP UI is a selected-county migration panel

## Data Model

```text
counties(
  geoid primary key,
  name,
  state_fips,
  geom
)

county_migration_summaries(
  geoid foreign key -> counties.geoid,
  period,
  source_year,
  moved_in,
  moved_out,
  net_migration,
  moved_in_moe,
  moved_out_moe,
  net_migration_moe,
  primary key (geoid, period)
)
```

## API Surface

```text
GET /counties/in-bbox
GET /metadata/migration-periods
GET /migration/counties/{geoid}?period=2016-2020
```

## Next Concrete Steps

1. Apply the migration summary table migration
2. Load county geometries if they are not already present
3. Run `python backend/scripts/ingest_migration_flows.py --source-year 2020`
4. Verify `GET /metadata/migration-periods` returns `2016-2020`
5. Click a county in the frontend and confirm moved-in/out/net numbers render

## Tickets

### Ticket 0 - Deployment readiness

Goal: deploy the current MVP so it can be shared and listed on a resume.

Tasks:

- Deploy the Svelte frontend as a static/web frontend service
- Deploy the FastAPI backend as a separate Python web service
- Keep Neon as the managed Postgres/PostGIS database
- Verify and clean up `requirements.txt` for backend deployment
- Add backend deployment config or documented host settings
- Add frontend deployment config or documented host settings
- Configure production environment variables
- Configure CORS for the deployed frontend domain
- Run Alembic migrations as a one-off deployment step, not inside the app start command
- Confirm Neon has the required schema and ingested MVP data
- Add a production smoke-test checklist

Acceptance:

- Deployed frontend loads successfully
- Deployed frontend can call the deployed FastAPI API
- Backend service starts with a command equivalent to `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- `requirements.txt` installs the backend dependencies in a clean environment
- Alembic migrations can be run manually or as a one-off deploy task before app startup
- `GET /metadata/migration-periods` returns at least `2016-2020`
- Clicking a county displays migration gain, migration loss, and net gain/loss
- README includes the production URL and deploy notes

### Ticket 1 - Migration data model

Goal: represent county-level movement directly.

Tasks:

- Add `county_migration_summaries`
- Keep `counties` as the spatial boundary table
- Store moved-in, moved-out, net migration, and margins of error
- Compute displayed net migration as moved-in minus moved-out

Acceptance:

- Alembic upgrade creates the table
- `(geoid, period)` prevents duplicate summaries

### Ticket 2 - Census migration-flow ingest

Goal: load real movement data.

Tasks:

- Fetch ACS Migration Flows from the Census API
- Aggregate rows by reference county
- Upsert summaries by `(geoid, period)`

Acceptance:

- Rerunning ingest is idempotent
- Each loaded county has moved-in, moved-out, and net migration values
- `net_migration` equals `moved_in - moved_out`

### Ticket 3 - Selected-county API

Goal: frontend can request the MVP numbers for one county.

Endpoint:

```text
GET /migration/counties/{geoid}?period=2016-2020
```

Acceptance:

- Returns county name, period, moved-in, moved-out, net migration, and direction
- Returns 404 when data has not been ingested for that county/period

### Ticket 4 - Frontend selected-county panel

Goal: clicking the map shows migration movement.

Tasks:

- Load counties by viewport
- Fetch available migration periods
- Click county to fetch its migration summary
- Display moved-in, moved-out, and net migration

Acceptance:

- Selected county is visually outlined
- Panel updates when a new county is clicked
- Period selector reloads the selected county when changed

### Ticket 5 - Portfolio-ready pass

Goal: make the MVP understandable.

Tasks:

- README explains Census migration-flow data
- Add screenshots or GIF
- Add limitations section

Acceptance:

- Someone can run it locally and understand what the numbers mean in 2 minutes

## Non-Goals For v1

- Perfect UI polish
- Predictions
- Multiple datasets
- Age-specific migration unless the source release supports it clearly
- Claiming migration from population snapshots
