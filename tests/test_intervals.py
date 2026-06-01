from houston_ndvi.intervals import monthly_intervals


def test_monthly_intervals_count() -> None:
    intervals = monthly_intervals(2021)
    assert len(intervals) == 12


def test_monthly_intervals_format() -> None:
    start, end = monthly_intervals(2017)[0]
    assert start == "2017-01-01"
    assert end == "2017-01-10"
