"""Download Sentinel-2 NDVI composites via Copernicus openEO."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import openeo
import xarray as xr

from houston_ndvi.intervals import monthly_intervals
from houston_ndvi.ndvi import load_ndvi_slice

logger = logging.getLogger(__name__)

YearSlices = dict[int, list[tuple[str, xr.DataArray]]]


def connect_openeo(endpoint: str) -> openeo.Connection:
    """Connect to openEO and authenticate with OIDC (interactive on first run)."""
    connection = openeo.connect(endpoint)
    connection.authenticate_oidc()
    return connection


def bbox_to_extent(bbox: list[float]) -> dict[str, float]:
    """Convert [west, south, east, north] to openEO spatial_extent keys."""
    west, south, east, north = bbox
    return {"west": west, "south": south, "east": east, "north": north}


def download_ndvi_interval(
    connection: openeo.Connection,
    *,
    collection: str,
    start: str,
    end: str,
    spatial_extent: dict[str, float],
    red_band: str,
    nir_band: str,
    out_format: str,
    output_path: Path,
    job_title: str,
) -> xr.DataArray:
    """Request, wait for, and download one NDVI composite."""
    cube = connection.load_collection(
        collection,
        temporal_extent=[start, end],
        spatial_extent=spatial_extent,
        bands=[red_band, nir_band],
    ).ndvi(red=red_band, nir=nir_band)
    job = cube.create_job(title=job_title, out_format=out_format)
    job.start_and_wait()
    job.download_result(output_path)
    return load_ndvi_slice(output_path)


def download_year(
    connection: openeo.Connection,
    year: int,
    config: dict[str, Any],
    data_dir: Path,
) -> list[tuple[str, xr.DataArray]]:
    """Download monthly NDVI slices for a single year."""
    openeo_cfg = config["openeo"]
    spatial_extent = bbox_to_extent(config["aoi"]["bbox"])
    slices: list[tuple[str, xr.DataArray]] = []
    for index, (start, end) in enumerate(monthly_intervals(year), start=1):
        output_path = data_dir / f"ndvi_{year}_{index:02d}.nc"
        logger.info("Requesting NDVI for %s to %s -> %s", start, end, output_path.name)
        ndvi_slice = download_ndvi_interval(
            connection,
            collection=openeo_cfg["collection"],
            start=start,
            end=end,
            spatial_extent=spatial_extent,
            red_band=openeo_cfg["red_band"],
            nir_band=openeo_cfg["nir_band"],
            out_format=openeo_cfg["out_format"],
            output_path=output_path,
            job_title=f"NDVI_{year}_{index:02d}",
        )
        slices.append((start, ndvi_slice))

    return slices


def download_years(
    connection: openeo.Connection,
    years: list[int],
    config: dict[str, Any],
    data_dir: Path,
) -> YearSlices:
    """Download NDVI for each year and return in-memory slices keyed by year."""
    data_dir.mkdir(parents=True, exist_ok=True)
    by_year: YearSlices = {}
    for year in years:
        logger.info("Processing year %s", year)
        by_year[year] = download_year(connection, year, config, data_dir)

    return by_year
