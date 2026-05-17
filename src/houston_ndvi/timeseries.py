"""Aggregate NDVI time series from downloaded NetCDF files."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

from houston_ndvi.ndvi import mean_ndvi


def load_mean_ndvi_series(
    data_dir: Path,
    pattern: str = "ndvi_*.nc",
) -> pd.DataFrame:
    """Build a DataFrame of mean NDVI and timestamps from NetCDF files."""
    records: list[dict[str, object]] = []

    for path in sorted(data_dir.glob(pattern)):
        with xr.open_dataset(path) as dataset:
            ndvi = dataset["var"].isel(t=0)
            timestamp = dataset.coords["t"].values[0]
        records.append(
            {
                "date": np.datetime64(timestamp),
                "ndvi": mean_ndvi(ndvi),
                "source": path.name,
            }
        )

    frame = pd.DataFrame(records)
    if frame.empty:
        return frame

    frame["year"] = pd.DatetimeIndex(frame["date"]).year
    frame["month"] = pd.DatetimeIndex(frame["date"]).month
    return frame.sort_values("date").reset_index(drop=True)


def pivot_monthly(frame: pd.DataFrame) -> pd.DataFrame:
    """Pivot mean NDVI into month (rows) by year (columns)."""
    return frame.pivot(index="month", columns="year", values="ndvi")


def annual_means(pivot: pd.DataFrame) -> pd.Series:
    """Return the mean NDVI for each year column."""
    return pivot.mean()


def months_above_threshold(pivot: pd.DataFrame, threshold: float) -> pd.Series:
    """Count months per year where mean NDVI exceeds a threshold."""
    return (pivot > threshold).sum()
