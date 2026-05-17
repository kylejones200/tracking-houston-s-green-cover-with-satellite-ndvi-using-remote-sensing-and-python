# Tracking Houston's Green Cover with Satellite NDVI

Published: 2025-04-21  
Medium: [Tracking Houston's Green Cover with Satellite NDVI using Remote Sensing and Python](https://medium.com/@kyle-t-jones/tracking-houston-s-green-cover-with-satellite-ndvi-using-remote-sensing-and-python-46320dbe3933)

Companion code for the article (`article.md`). Downloads Sentinel-2 NDVI over downtown Houston via [Copernicus openEO](https://openeo.dataspace.copernicus.eu/), builds year-over-year comparison GIFs, and analyzes seasonal greenness and vegetation-class agreement.

## Quick start

Requires [uv](https://docs.astral.sh/uv/) and a free Copernicus Data Space account for satellite downloads.

```bash
uv sync
```

### 1. Download NDVI (interactive OIDC login on first run)

```bash
uv run houston-ndvi fetch
```

NetCDF files are saved under `outputs/data/` as `ndvi_{year}_{month}.nc`.

### 2. Analyze, plot, and build GIF (offline, uses downloaded files)

```bash
uv run houston-ndvi all
```

Or run steps individually:

```bash
uv run houston-ndvi gif
uv run houston-ndvi analyze
uv run houston-ndvi kappa
```

### 3. Electrification priority maps (separate geospatial workflow)

```bash
uv run houston-ndvi electrification
```

## Outputs

| Command | Outputs |
|---------|---------|
| `fetch` | `outputs/data/ndvi_*.nc` |
| `gif` | `outputs/frames/frame_*.png`, `outputs/houston_ndvi_2017_vs_2023.gif` |
| `analyze` | `outputs/figures/ndvi_*.png` |
| `kappa` | `outputs/figures/ndvi_kappa_*.png` |
| `electrification` | `outputs/figures/houston_*.png` |
| `all` | GIF + analyze + kappa (no download) |

## Configuration

Edit `config.yaml` to change:

- AOI bounding box (`aoi.bbox`)
- Years to download or compare (`analysis.years`, `analysis.compare_years`)
- NDVI classification thresholds (`analysis.ndvi_low`, `analysis.ndvi_medium`)
- Output directories (`output.*`)

## Project layout

```
pyproject.toml / uv.lock / config.yaml
src/houston_ndvi/     # package: openEO fetch, GIF, time series, kappa, electrification
outputs/
  data/               # NetCDF downloads (gitignored)
  frames/             # GIF frame PNGs (gitignored)
  figures/            # analysis plots (gitignored)
legacy/               # original notebook exports and scripts
tests/
article.md
```

## Development

```bash
uv sync --extra dev
uv run pytest
uv run ruff check src tests
```

## Disclaimer

Educational/demo code only. Not financial, safety, or engineering advice. Use at your own risk. Verify results independently before any production or operational use.

## License

MIT — see [LICENSE](LICENSE).
