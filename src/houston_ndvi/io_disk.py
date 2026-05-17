"""Load NDVI slices from existing NetCDF downloads on disk."""

from __future__ import annotations

from pathlib import Path

import xarray as xr

from houston_ndvi.intervals import monthly_intervals
from houston_ndvi.ndvi import load_ndvi_slice


def load_year_slices(year: int, data_dir: Path) -> list[tuple[str, xr.DataArray]]:
    """Load monthly NDVI slices for a year from ndvi_{year}_{mm}.nc files."""
    slices: list[tuple[str, xr.DataArray]] = []
    for index, (start, _) in enumerate(monthly_intervals(year), start=1):
        path = data_dir / f"ndvi_{year}_{index:02d}.nc"
        if not path.exists():
            raise FileNotFoundError(f"Missing NDVI file: {path}")
        slices.append((start, load_ndvi_slice(path)))
    return slices


def load_years_from_disk(
    years: list[int], data_dir: Path
) -> dict[int, list[tuple[str, xr.DataArray]]]:
    """Load in-memory NDVI slices for multiple years."""
    return {year: load_year_slices(year, data_dir) for year in years}
