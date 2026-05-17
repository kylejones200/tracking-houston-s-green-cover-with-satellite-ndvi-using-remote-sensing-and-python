import numpy as np
import xarray as xr

from houston_ndvi.ndvi import classify_ndvi, flatten_valid_pairs, mean_ndvi


def test_classify_ndvi_buckets() -> None:
    values = xr.DataArray([-0.2, 0.05, 0.2, 0.5])
    classes = classify_ndvi(values, low=0.1, medium=0.3)
    assert classes.values.tolist() == [0, 0, 1, 2]


def test_mean_ndvi() -> None:
    raster = xr.DataArray(np.array([[0.2, 0.4], [0.6, 0.8]]))
    assert mean_ndvi(raster) == 0.5


def test_flatten_valid_pairs_drops_nan() -> None:
    left = xr.DataArray([0.0, np.nan, 1.0])
    right = xr.DataArray([1.0, 1.0, np.nan])
    y_left, y_right = flatten_valid_pairs(left, right)
    assert y_left.tolist() == [0.0]
    assert y_right.tolist() == [1.0]
