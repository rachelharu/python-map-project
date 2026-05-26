import argparse
import json
import os
import sys
from json import JSONDecodeError
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError
from urllib.request import urlopen

from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import insert

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.app.db import SessionLocal
from backend.app.features.counties.models import County
from backend.app.features.migration.models import CountyMigrationSummary
from backend.app.providers.census.migration_flows import (
    FLOW_SOURCE_YEAR,
    FLOW_VARIABLES,
    aggregate_county_summaries,
    default_period,
)

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def census_url(source_year: int, api_key: str | None = None) -> str:
    params = {
        "get": ",".join(FLOW_VARIABLES),
        "for": "county:*",
        "in": "state:*",
    }
    if api_key:
        params["key"] = api_key

    return f"https://api.census.gov/data/{source_year}/acs/flows?{urlencode(params)}"


def fetch_rows(source_year: int, api_key: str | None = None) -> list[dict]:
    url = census_url(source_year, api_key)
    try:
        with urlopen(url, timeout=60) as response:
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Census API request failed: {body[:500]}") from exc

    try:
        payload = json.loads(body)
    except JSONDecodeError as exc:
        raise RuntimeError(f"Census API returned a non-JSON response: {body[:500]}") from exc

    header = payload[0]
    return [dict(zip(header, values)) for values in payload[1:]]


def upsert_summaries(summaries: list[dict]) -> int:
    with SessionLocal() as db:
        county_geoids = {geoid for (geoid,) in db.query(County.geoid).all()}

    original_count = len(summaries)
    summaries = [summary for summary in summaries if summary["geoid"] in county_geoids]
    skipped_count = original_count - len(summaries)
    if skipped_count:
        print(f"Skipped {skipped_count} summaries without matching county geometry.")

    rows = [
        {
            "geoid": summary["geoid"],
            "period": summary["period"],
            "source_year": summary["source_year"],
            "moved_in": summary["moved_in"],
            "moved_out": summary["moved_out"],
            "net_migration": summary["net_migration"],
            "moved_in_moe": summary["moved_in_moe"],
            "moved_out_moe": summary["moved_out_moe"],
            "net_migration_moe": summary["net_migration_moe"],
        }
        for summary in summaries
    ]

    if not rows:
        return 0

    table = CountyMigrationSummary.__table__
    stmt = insert(table).values(rows)
    update_columns = {
        column.name: getattr(stmt.excluded, column.name)
        for column in table.columns
        if column.name not in {"geoid", "period"}
    }
    stmt = stmt.on_conflict_do_update(
        index_elements=["geoid", "period"],
        set_=update_columns,
    )

    with SessionLocal() as db:
        db.execute(stmt)
        db.commit()

    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest ACS county migration flow summaries."
    )
    parser.add_argument("--source-year", type=int, default=FLOW_SOURCE_YEAR)
    parser.add_argument("--period", default=None)
    args = parser.parse_args()
    period = args.period or default_period(args.source_year)

    api_key = os.getenv("CENSUS_API_KEY")
    if not api_key:
        raise RuntimeError(
            "CENSUS_API_KEY is required by the Census ACS migration flows API. "
            "Add CENSUS_API_KEY=your_key to backend/.env, then rerun this command."
        )

    rows = fetch_rows(args.source_year, api_key)
    summaries = aggregate_county_summaries(
        rows,
        period=period,
        source_year=args.source_year,
    )
    inserted = upsert_summaries(summaries)
    print(f"Upserted {inserted} county migration summaries for {period}.")


if __name__ == "__main__":
    main()
