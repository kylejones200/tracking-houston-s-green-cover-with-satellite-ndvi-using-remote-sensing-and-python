import pandas as pd
import pytest

from houston_ndvi.timeseries import annual_means, months_above_threshold, pivot_monthly


def test_pivot_monthly() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2017-01-01", "2017-02-01", "2023-01-01"]),
            "ndvi": [0.2, 0.3, 0.25],
            "year": [2017, 2017, 2023],
            "month": [1, 2, 1],
        }
    )
    pivot = pivot_monthly(frame)
    assert pivot.loc[1, 2017] == 0.2
    assert pivot.loc[1, 2023] == 0.25


def test_annual_means_and_threshold() -> None:
    pivot = pd.DataFrame({2017: [0.2, 0.4], 2023: [0.35, 0.25]}, index=[1, 2])
    means = annual_means(pivot)
    assert means[2017] == pytest.approx(0.3)
    assert months_above_threshold(pivot, 0.3).tolist() == [1, 1]
