"""Cohen's kappa for NDVI vegetation class agreement across years."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score

from houston_ndvi.ndvi import classify_ndvi, flatten_valid_pairs, load_ndvi_slice


def kappa_for_pair(
    path_left: Path,
    path_right: Path,
    *,
    low: float = 0.1,
    medium: float = 0.3,
) -> float:
    """Compute Cohen's kappa between two monthly NDVI rasters."""
    left = classify_ndvi(load_ndvi_slice(path_left), low=low, medium=medium)
    right = classify_ndvi(load_ndvi_slice(path_right), low=low, medium=medium)
    y_left, y_right = flatten_valid_pairs(left, right)
    return float(cohen_kappa_score(y_left, y_right))


def monthly_kappa_series(
    data_dir: Path,
    years: tuple[int, int],
    *,
    low: float = 0.1,
    medium: float = 0.3,
) -> pd.DataFrame:
    """Compute monthly kappa scores between two years of NetCDF files."""
    year_a, year_b = years
    records: list[dict[str, float | int]] = []

    for month in range(1, 13):
        path_a = data_dir / f"ndvi_{year_a}_{month:02d}.nc"
        path_b = data_dir / f"ndvi_{year_b}_{month:02d}.nc"
        if not path_a.exists() or not path_b.exists():
            continue
        records.append(
            {
                "month": month,
                "kappa": kappa_for_pair(path_a, path_b, low=low, medium=medium),
            }
        )

    return pd.DataFrame(records)
