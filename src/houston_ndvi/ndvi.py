"""NDVI classification and raster helpers."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import xarray as xr


def classify_ndvi(
    ndvi: xr.DataArray,
    low: float = 0.1,
    medium: float = 0.3,
) -> xr.DataArray:
    """Map NDVI to vegetation classes: 0=low, 1=medium, 2=high."""
    return xr.where(
        ndvi < low,
        0,
        xr.where(ndvi < medium, 1, 2),
    )


def load_ndvi_slice(path: Path | str) -> xr.DataArray:
    """Load the first time slice of the NDVI variable from a NetCDF file."""
    with xr.open_dataset(path) as dataset:
        return dataset["var"].isel(t=0)


def mean_ndvi(ndvi: xr.DataArray) -> float:
    """Return the spatial mean NDVI as a float."""
    return float(ndvi.mean().values)


def flatten_valid_pairs(
    left: xr.DataArray,
    right: xr.DataArray,
) -> tuple[np.ndarray, np.ndarray]:
    """Flatten paired classification arrays, dropping NaN pixels."""
    mask = (~np.isnan(left)) & (~np.isnan(right))
    y_left = left.values[mask].flatten()
    y_right = right.values[mask].flatten()
    return y_left, y_right
