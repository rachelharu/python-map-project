from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

from ...db import get_db
from ..counties.models import County
from .models import CountyMigrationSummary

router = APIRouter(prefix="/migration", tags=["migration"])
metadata_router = APIRouter(prefix="/metadata", tags=["metadata"])


def _summary_response(summary: CountyMigrationSummary, county: County) -> dict:
    direction = "flat"
    if summary.net_migration > 0:
        direction = "gained"
    elif summary.net_migration < 0:
        direction = "lost"

    return {
        "geoid": county.geoid,
        "name": county.name,
        "period": summary.period,
        "source_year": summary.source_year,
        "moved_in": summary.moved_in,
        "moved_out": summary.moved_out,
        "net_migration": summary.net_migration,
        "direction": direction,
        "moe": {
            "moved_in": summary.moved_in_moe,
            "moved_out": summary.moved_out_moe,
            "net_migration": summary.net_migration_moe,
        },
    }


def _latest_period(db: Session) -> str | None:
    try:
        return (
            db.query(CountyMigrationSummary.period)
            .distinct()
            .order_by(CountyMigrationSummary.period.desc())
            .limit(1)
            .scalar()
        )
    except ProgrammingError:
        db.rollback()
        return None


@metadata_router.get("/migration-periods")
def list_migration_periods(db: Session = Depends(get_db)):
    try:
        periods = (
            db.query(CountyMigrationSummary.period)
            .distinct()
            .order_by(CountyMigrationSummary.period)
            .all()
        )
    except ProgrammingError:
        db.rollback()
        return {"periods": []}

    return {"periods": [period for (period,) in periods]}


@router.get("/counties/{geoid}")
def get_county_migration_summary(
    geoid: str,
    period: str | None = None,
    db: Session = Depends(get_db),
):
    selected_period = period or _latest_period(db)
    if selected_period is None:
        raise HTTPException(status_code=404, detail="No migration periods have been ingested")

    row = (
        db.query(CountyMigrationSummary, County)
        .join(County, County.geoid == CountyMigrationSummary.geoid)
        .filter(CountyMigrationSummary.geoid == geoid)
        .filter(CountyMigrationSummary.period == selected_period)
        .first()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="No migration summary found for county")

    summary, county = row
    return _summary_response(summary, county)
