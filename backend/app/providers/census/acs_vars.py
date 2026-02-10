ADULTS_18_34_VARS = [
    # Male
    "B01001_007E",  # 18 and 19
    "B01001_008E",  # 20
    "B01001_009E",  # 21
    "B01001_010E",  # 22-24
    "B01001_011E",  # 25-29
    "B01001_012E",  # 30-34
    # Female
    "B01001_031E",  # 18 and 19
    "B01001_032E",  # 20
    "B01001_033E",  # 21
    "B01001_034E",  # 22-24
    "B01001_035E",  # 25-29
    "B01001_036E",  # 30-34
]

def sum_vars(row: dict, vars_: list[str]) -> int:
    total = 0
    for k in vars_:
        v = row.get(k,0)
        try:
            total += int(v)
        except (TypeError, ValueError):
            total += 0
    return total

def adults_18_34(row: dict) -> int:
    return sum_vars(row, ADULTS_18_34_VARS)
