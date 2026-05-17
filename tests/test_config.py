from houston_ndvi.config import load_config


def test_load_default_config() -> None:
    config = load_config()
    assert config["openeo"]["collection"] == "SENTINEL2_L2A"
    assert len(config["aoi"]["bbox"]) == 4
    assert config["analysis"]["compare_years"] == [2017, 2023]
