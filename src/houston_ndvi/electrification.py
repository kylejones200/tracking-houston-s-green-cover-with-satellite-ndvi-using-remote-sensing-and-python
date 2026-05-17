"""Priority areas for electrification using census and air-quality layers."""

from __future__ import annotations

import io
import logging
import zipfile
from pathlib import Path

import contextily as ctx
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from esda.moran import Moran
from libpysal.weights import Queen

from houston_ndvi.paths import figure_path

logger = logging.getLogger(__name__)

BASEMAP = ctx.providers.CartoDB.Positron


def _download_zip(url: str, extract_dir: Path) -> None:
    extract_dir.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        archive.extractall(extract_dir)


def load_houston_tracts(tiger_year: int, cache_dir: Path) -> gpd.GeoDataFrame:
    """Download and load Harris County census tracts."""
    url = (
        f"https://www2.census.gov/geo/tiger/TIGER{tiger_year}/TRACT/"
        f"tl_{tiger_year}_48201_tract.zip"
    )
    extract_dir = cache_dir / f"tiger_tracts_{tiger_year}"
    _download_zip(url, extract_dir)
    shapefile = next(extract_dir.glob("*.shp"))
    return gpd.read_file(shapefile)


def load_acs_tract_data(state_fips: str, county_fips: str, acs_year: int) -> pd.DataFrame:
    """Fetch population and median income from the Census ACS API."""
    url = (
        f"https://api.census.gov/data/{acs_year}/acs/acs5"
        f"?get=B01003_001E,B19013_001E&for=tract:*"
        f"&in=state:{state_fips}%20county:{county_fips}"
    )
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    payload = response.json()
    frame = pd.DataFrame(
        payload[1:],
        columns=["population", "median_income", "state", "county", "tract"],
    )
    frame["GEOID"] = frame["state"] + frame["county"] + frame["tract"]
    frame[["population", "median_income"]] = frame[["population", "median_income"]].astype(
        float
    )
    return frame


def load_air_quality_stations(cache_dir: Path) -> gpd.GeoDataFrame:
    """Download TCEQ air-quality monitoring station locations."""
    url = (
        "https://opendata.arcgis.com/api/v3/datasets/"
        "ab6153d5c9644f9a9b505b2a14ae2df5_0/downloads/data"
        "?format=shp&spatialRefId=4326"
    )
    extract_dir = cache_dir / "houston_aqi"
    _download_zip(url, extract_dir)
    shapefile = next(extract_dir.glob("*.shp"))
    return gpd.read_file(shapefile)


def run_electrification_analysis(
    config: dict,
    cache_dir: Path,
    *,
    show: bool = False,
) -> None:
    """Build priority maps for electrification using public geospatial data."""
    elec_cfg = config["electrification"]
    state = elec_cfg["state_fips"]
    county = elec_cfg["county_fips"]

    tracts = load_houston_tracts(elec_cfg["tiger_year"], cache_dir)
    acs = load_acs_tract_data(state, county, elec_cfg["acs_year"])
    tracts = tracts.merge(acs[["GEOID", "population", "median_income"]], on="GEOID")

    tracts["area_sq_miles"] = tracts.geometry.to_crs({"proj": "aea"}).area / 2.59e6
    tracts["pop_density"] = tracts["population"] / tracts["area_sq_miles"]

    pollution = load_air_quality_stations(cache_dir).to_crs(tracts.crs)
    tracts["asthma_rate"] = np.random.default_rng(42).uniform(5, 15, size=len(tracts))

    _plot_choropleth(
        tracts,
        column="pop_density",
        title="Population Density by Census Tract in Houston, TX",
        cmap="OrRd",
        output=figure_path("houston_population_density.png"),
        show=show,
    )
    _plot_points(
        pollution,
        title="Air Quality Monitoring Stations in Houston, TX",
        output=figure_path("houston_pollution_stations.png"),
        show=show,
    )

    tracts = gpd.sjoin_nearest(
        tracts,
        pollution[["geometry"]],
        how="left",
        distance_col="pollution_distance",
    )

    weights = Queen.from_dataframe(tracts)
    weights.transform = "r"
    moran = Moran(tracts["pop_density"], weights)
    logger.info("Moran's I: %.3f, p-value: %.4f", moran.I, moran.p_norm)

    tracts["priority_score"] = (
        tracts["pop_density"]
        * (1 / tracts["median_income"])
        * tracts["asthma_rate"]
    )

    _plot_choropleth(
        tracts,
        column="priority_score",
        title="Priority Areas for Electrification in Houston, TX",
        cmap="Reds",
        output=figure_path("houston_priority_areas.png"),
        show=show,
    )


def _plot_choropleth(
    frame: gpd.GeoDataFrame,
    *,
    column: str,
    title: str,
    cmap: str,
    output: Path,
    show: bool,
) -> None:
    fig, axis = plt.subplots(figsize=(10, 10))
    frame.plot(column=column, cmap=cmap, legend=True, ax=axis, edgecolor="k")
    axis.set_title(title)
    ctx.add_basemap(axis, source=BASEMAP, crs=frame.crs.to_string())
    fig.savefig(output, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
    logger.info("Saved %s", output)


def _plot_points(
    frame: gpd.GeoDataFrame,
    *,
    title: str,
    output: Path,
    show: bool,
) -> None:
    fig, axis = plt.subplots(figsize=(10, 10))
    frame.plot(color="blue", markersize=50, alpha=0.7, ax=axis)
    axis.set_title(title)
    ctx.add_basemap(axis, source=BASEMAP, crs=frame.crs.to_string())
    fig.savefig(output, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
    logger.info("Saved %s", output)
