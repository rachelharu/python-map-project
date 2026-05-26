from backend.app.providers.census.migration_flows import (
    aggregate_county_summaries,
    default_period,
)


def test_aggregate_county_summaries_groups_by_reference_county():
    rows = [
        {
            "GEOID1": "06037",
            "FULL1_NAME": "Los Angeles County, California",
            "GEOID2": "06059",
            "MOVEDIN": "10",
            "MOVEDIN_M": "3",
            "MOVEDOUT": "4",
            "MOVEDOUT_M": "2",
        },
        {
            "GEOID1": "06037",
            "FULL1_NAME": "Los Angeles County, California",
            "GEOID2": "36061",
            "MOVEDIN": "5",
            "MOVEDIN_M": "4",
            "MOVEDOUT": "9",
            "MOVEDOUT_M": "1",
        },
    ]

    summaries = aggregate_county_summaries(rows)

    assert summaries == [
        {
            "geoid": "06037",
            "name": "Los Angeles County, California",
            "period": "2016-2020",
            "source_year": 2020,
            "moved_in": 15,
            "moved_out": 13,
            "net_migration": 2,
            "moved_in_moe": 5,
            "moved_out_moe": 2,
            "net_migration_moe": 5,
        }
    ]


def test_default_period_uses_acs_5_year_window():
    assert default_period(2020) == "2016-2020"
    assert default_period(2019) == "2015-2019"
