# Schema

## MVP Tables

```text
counties(
  geoid text primary key,
  name text not null,
  state_fips text,
  geom geometry(MULTIPOLYGON, 4326) not null
)

county_migration_summaries(
  geoid text not null references counties(geoid),
  period text not null,
  source_year integer not null,
  moved_in integer not null,
  moved_out integer not null,
  net_migration integer not null,
  moved_in_moe integer,
  moved_out_moe integer,
  net_migration_moe integer,
  primary key (geoid, period)
)
```

`county_migration_summaries` stores aggregated ACS migration-flow estimates for
the reference county. It is intentionally separate from population-count tables:
movement and population change are related, but they are not the same metric.

`moved_in` aggregates Census `MOVEDIN`, including domestic county-to-county
inbound rows and rows from abroad/world regions. `moved_out` aggregates Census
`MOVEDOUT`, which is domestic county-to-county outbound movement. The app stores
`net_migration` as `moved_in - moved_out` so the displayed panel is internally
consistent for the MVP.
