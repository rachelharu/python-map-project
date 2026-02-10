from backend.app.providers.census.acs_vars import ADULTS_18_34_VARS, adults_18_34


def test_adults_18_34_sums_selected_vars():
    row = {var: 1 for var in ADULTS_18_34_VARS}
    row.update(
        {
            "B01001_003E": 999,  # male under 5
            "B01001_027E": 999,  # female under 5
        }
    )

    assert adults_18_34(row) == len(ADULTS_18_34_VARS)


def test_adults_18_34_handles_missing_or_bad_values():
    row = {
        "B01001_007E": "5",
        "B01001_008E": None,
        "B01001_009E": "not-a-number",
    }

    assert adults_18_34(row) == 5
