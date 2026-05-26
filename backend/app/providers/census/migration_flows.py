from math import sqrt


FLOW_SOURCE_YEAR = 2020
FLOW_PERIOD = "2016-2020"

FLOW_VARIABLES = [
    "GEOID1",
    "FULL1_NAME",
    "GEOID2",
    "MOVEDIN",
    "MOVEDIN_M",
    "MOVEDOUT",
    "MOVEDOUT_M",
]


def parse_int(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def combine_moe(values: list[int]) -> int | None:
    clean_values = [value for value in values if value > 0]
    if not clean_values:
        return None
    return round(sqrt(sum(value * value for value in clean_values)))


def difference_moe(left: int | None, right: int | None) -> int | None:
    values = [value for value in (left, right) if value is not None and value > 0]
    if not values:
        return None
    return round(sqrt(sum(value * value for value in values)))


def default_period(source_year: int) -> str:
    return f"{source_year - 4}-{source_year}"


def aggregate_county_summaries(
    rows: list[dict],
    period: str = FLOW_PERIOD,
    source_year: int = FLOW_SOURCE_YEAR,
) -> list[dict]:
    summaries: dict[str, dict] = {}
    moe_values: dict[str, dict[str, list[int]]] = {}

    for row in rows:
        geoid = str(row.get("GEOID1", "")).strip()
        if not geoid:
            continue

        summary = summaries.setdefault(
            geoid,
            {
                "geoid": geoid,
                "name": row.get("FULL1_NAME"),
                "period": period,
                "source_year": source_year,
                "moved_in": 0,
                "moved_out": 0,
                "net_migration": 0,
            },
        )
        county_moes = moe_values.setdefault(
            geoid,
            {
                "moved_in_moe": [],
                "moved_out_moe": [],
            },
        )

        summary["moved_in"] += parse_int(row.get("MOVEDIN"))
        summary["moved_out"] += parse_int(row.get("MOVEDOUT"))
        county_moes["moved_in_moe"].append(parse_int(row.get("MOVEDIN_M")))
        county_moes["moved_out_moe"].append(parse_int(row.get("MOVEDOUT_M")))

    for geoid, summary in summaries.items():
        county_moes = moe_values[geoid]
        summary["moved_in_moe"] = combine_moe(county_moes["moved_in_moe"])
        summary["moved_out_moe"] = combine_moe(county_moes["moved_out_moe"])
        summary["net_migration"] = summary["moved_in"] - summary["moved_out"]
        summary["net_migration_moe"] = difference_moe(
            summary["moved_in_moe"],
            summary["moved_out_moe"],
        )

    return list(summaries.values())
