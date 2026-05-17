"""Generated from Jupyter notebook: 2025-04-29 Priority Areas for Electrification in Houston

Magics and shell lines are commented out. Run with a normal Python interpreter."""

import io
import zipfile

import censusdata
import contextily as ctx
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import requests
from esda.moran import Moran
from libpysal.weights import Queen


def install_required_libraries_if_necessary() -> None:
    url_tracts = "https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_48201_tract.zip"

    response = requests.get(url_tracts)

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall("houston_tracts")

    census_tracts = gpd.read_file("houston_tracts/tl_2023_48201_tract.shp")

    acs_url = "https://api.census.gov/data/2021/acs/acs5?get=B01003_001E,B19013_001E&for=tract:*&in=state:48%20county:201"

    acs_data = requests.get(acs_url).json()

    acs_df = pd.DataFrame(
        acs_data[1:], columns=["population", "median_income", "state", "county", "tract"]
    )

    acs_df["GEOID"] = acs_df["state"] + acs_df["county"] + acs_df["tract"]

    acs_df[["population", "median_income"]] = acs_df[["population", "median_income"]].astype(float)

    census_tracts = census_tracts.merge(
        acs_df[["GEOID", "population", "median_income"]], on="GEOID"
    )

    census_tracts["area_sq_miles"] = census_tracts.geometry.to_crs({"proj": "aea"}).area / 2590000.0

    census_tracts["pop_density"] = census_tracts["population"] / census_tracts["area_sq_miles"]

    aqi_url = "https://opendata.arcgis.com/api/v3/datasets/ab6153d5c9644f9a9b505b2a14ae2df5_0/downloads/data?format=shp&spatialRefId=4326"

    aqi_response = requests.get(aqi_url)

    with zipfile.ZipFile(io.BytesIO(aqi_response.content)) as z:
        z.extractall("houston_aqi")

    pollution = gpd.read_file("houston_aqi/Current_Air_Quality_Monitoring_Stations.shp").to_crs(
        census_tracts.crs
    )

    census_tracts["asthma_rate"] = pd.Series(pd.np.random.uniform(5, 15, size=len(census_tracts)))

    ax = census_tracts.plot(
        column="pop_density", cmap="OrRd", legend=True, figsize=(10, 10), edgecolor="k"
    )

    ax.set_title("Population Density by Census Tract in Houston, TX")

    ctx.add_basemap(ax, source=ctx.providers.Stamen.TonerLite, crs=census_tracts.crs.to_string())

    plt.savefig("houston_population_density.png")

    plt.show()

    ax = pollution.plot(color="blue", markersize=50, alpha=0.7, figsize=(10, 10))

    ax.set_title("Air Quality Monitoring Stations in Houston, TX")

    ctx.add_basemap(ax, source=ctx.providers.Stamen.TonerLite, crs=pollution.crs.to_string())

    plt.savefig("houston_pollution_stations.png")

    plt.show()

    census_tracts = gpd.sjoin_nearest(
        census_tracts, pollution[["geometry"]], how="left", distance_col="pollution_distance"
    )

    w = Queen.from_dataframe(census_tracts)

    w.transform = "r"

    moran = Moran(census_tracts["pop_density"], w)

    print(f"Moran's I: {moran.I:.3f}, p-value: {moran.p_norm:.4f}")

    census_tracts["priority_score"] = (
        census_tracts["pop_density"]
        * (1 / census_tracts["median_income"])
        * census_tracts["asthma_rate"]
    )

    ax = census_tracts.plot(
        column="priority_score", cmap="Reds", legend=True, figsize=(10, 10), edgecolor="k"
    )

    ax.set_title("Priority Areas for Electrification in Houston, TX")

    ctx.add_basemap(ax, source=ctx.providers.Stamen.TonerLite, crs=census_tracts.crs.to_string())

    plt.savefig("houston_priority_areas.png")

    plt.show()


def notebook_step_005() -> None:
    url_tracts = "https://www2.census.gov/geo/tiger/TIGER2022/TRACT/tl_2022_48201_tract.zip"

    response = requests.get(url_tracts, stream=True)

    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall("houston_tracts")
        print("Download and extraction successful.")
    else:
        print(f"Download failed with status code {response.status_code}")


def load_census_tracts_shapefile() -> None:
    census_tracts = gpd.read_file("path_to_census_tracts_shapefile.shp")

    population_density = pd.read_csv("path_to_population_density_data.csv")

    census_tracts = census_tracts.merge(population_density, on="tract_id")

    air_quality_stations = gpd.read_file("path_to_air_quality_stations_shapefile.shp")


def load_the_harris_county_boundary_from_the_gis_map() -> None:
    url = "https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/HCAD_Harris_County_Boundary/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=geojson"

    harris_boundary = gpd.read_file(url)

    harris_boundary.plot()


def notebook_step_008() -> None:
    county_boundary = gpd.read_file("County.shp")

    county_boundary.plot()


def tigerweb_census_tracts_for_harris_county_fips_st() -> None:
    tracts_url = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Tracts_Blocks/MapServer/3/query?where=COUNTY='201'&outFields=GEOID&outSR=4326&f=geojson"

    tracts = gpd.read_file(tracts_url)

    tracts.plot(figsize=(10, 10))


def api_request_for_acs_2021_5_year_estimates_b01003() -> None:
    acs_url = "https://api.census.gov/data/2021/acs/acs5?get=B01003_001E,B19013_001E&for=tract:*&in=state:48 county:201"

    response = pd.read_json(acs_url)

    df = pd.DataFrame(response[1:], columns=response[0])

    df["GEOID"] = df["state"] + df["county"] + df["tract"]

    df[["population", "median_income"]] = df[["B01003_001E", "B19013_001E"]].astype(float)


def notebook_step_011() -> None:
    tracts = tracts.merge(df[["GEOID", "population", "median_income"]], on="GEOID")

    tracts["pop_density"] = tracts["population"] / (tracts.geometry.area / 1000000.0)


def notebook_step_012() -> None:
    ax = tracts.plot(
        column="pop_density", cmap="OrRd", legend=True, figsize=(12, 10), edgecolor="k"
    )

    ax.set_title("Population Density by Census Tract - Harris County")

    ctx.add_basemap(ax, source=ctx.providers.Stamen.TonerLite, crs=tracts.crs.to_string())

    plt.show()


def notebook_step_013() -> None:
    data = censusdata.download(
        "acs5",
        2021,
        censusdata.censusgeo([("state", "48"), ("county", "201"), ("tract", "*")]),
        ["B01003_001E", "B19013_001E"],
    )

    data.reset_index(inplace=True)

    data["GEOID"] = data["index"].apply(lambda x: x.geo[2][1] + x.geo[3][1] + x.geo[4][1])


def main() -> None:
    install_required_libraries_if_necessary()
    notebook_step_005()
    load_census_tracts_shapefile()
    load_the_harris_county_boundary_from_the_gis_map()
    notebook_step_008()
    tigerweb_census_tracts_for_harris_county_fips_st()
    api_request_for_acs_2021_5_year_estimates_b01003()
    notebook_step_011()
    notebook_step_012()
    notebook_step_013()


if __name__ == "__main__":
    main()
