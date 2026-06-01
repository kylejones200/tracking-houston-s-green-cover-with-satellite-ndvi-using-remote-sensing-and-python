---
author: "Kyle Jones"
date_published: "April 21, 2025"
date_exported_from_medium: "November 10, 2025"
canonical_link: "https://medium.com/@kyle-t-jones/tracking-houstons-green-cover-with-satellite-ndvi-using-remote-sensing-and-python-46320dbe3933"
---

# Tracking Houston's Green Cover with Satellite NDVI using Remote Sensing and Python Change often happens in ways we can't quite see --- until we pull back
far enough. From high above Earth, satellites watch as cities grow...

### Tracking Houston's Green Cover with Satellite NDVI using Remote Sensing and Python
Change often happens in ways we can't quite see --- until we pull back far enough. From high above Earth, satellites watch as cities grow, shift, and breathe. Thanks to the European Space Agency's Sentinel-2 satellites and freely available Copernicus data, we can now track subtle changes in urban green cover, one pixel at a time.

This post is about what happens when we look at Houston's vegetation over the course of 2021, using NDVI --- the normalized difference vegetation index. NDVI is a measure of photosynthesis, pulled from red and near-infrared bands in satellite imagery. When plants grow, they reflect NIR light and absorb red light. NDVI turns that contrast into a value between --1 and +1. The greener the area, the closer to 1.

Here's Houston, month by month, in 2021:


<figcaption>May is excluded because of complete cloud coverage.</figcaption>


What you're seeing is how green Houston gets, and where that greenness lives. Parks, rivers, undeveloped land --- they stand out in light green and aqua tones. Neighborhoods with denser trees appear less red. Freeways and industrial zones, as you might expect, barely shift across the seasons.

What's powerful here is not just the color. It's the consistency of observation. This GIF is built from twelve Sentinel-2 images, one for each month in 2021. Each is a cloud-free snapshot of Houston's core, rendered using the NDVI equation:

``` 
NDVI = (NIR - Red) / (NIR + Red)
```

In practical terms, that's Band 8 minus Band 4 divided by their sum, using Sentinel-2 Level-2A imagery. We pulled that data via openEO, an API layer that lets you access Copernicus Data Space Ecosystem (CDSE) infrastructure without ever needing to store raw imagery locally.

Each frame tells us something. In January and February, Houston's vegetation is dormant --- patches of red dominate. But by March, things start to bloom. The city breathes. We see the parks come alive. Summer holds that greenery until late September. And then, the slow fade returns.

### What Makes NDVI So Useful?
NDVI is a quantitative signal. Researchers it is typically used fo measure crop health and predict yield, detect deforestation and land conversion, and monitor urban greening initiatives.

In a place like Houston --- where development pushes outward into low-density greenfield areas --- it's a tool for tracking what we often ignore: what we build over.

### Sentinel-2 and Copernicus
There are lots of ways to get remote sensing data. Sentinel-2 is great because you get 10m resolution data for free and near-global coverage every 5 days. There are different bands (Red, NIR, SWIR) but fewer than you might get from a private service.

Copernicus openEO lets you process imagery without downloading huge files. So the barrier to entry for this kind of remote sensing is low. All you need is Python, an idea, and some patience.

### What Comes Next
This animation is just the beginning. I'm working on other examples that show the cool things you can do with remote sensing.

```python
from pathlib import Path
import openeo
import xarray as xr
import matplotlib.pyplot as plt
import imageio
import numpy as np
import os
from datetime import datetime, timedelta

# Setup folders
base_path = Path("results")
base_path.mkdir(exist_ok=True)
frames_dir = base_path / "frames"
frames_dir.mkdir(exist_ok=True)

# Connect and authenticate
eoconn = openeo.connect("openeo.dataspace.copernicus.eu")
eoconn.authenticate_oidc()

# Define Houston bounding box (smaller for speed)
bbox = [-95.40, 29.70, -95.30, 29.80]  # Downtown Houston

# Define year and monthly date ranges (10-day windows)
year = 2021
intervals = [
    (
        datetime(year, m, 1).strftime('%Y-%m-%d'),
        (datetime(year, m, 10)).strftime('%Y-%m-%d')
    ) for m in range(1, 13)
]

# Process and download each NDVI tile
all_ndvi_slices = []

for i, (start, end) in enumerate(intervals):
    print(f"\n Requesting NDVI for {start} to {end}")
    
    # Create NDVI cube
    cube = eoconn.load_collection(
        "SENTINEL2_L2A",
        temporal_extent=[start, end],
        spatial_extent=dict(zip(["west", "south", "east", "north"], bbox)),
        bands=["B04", "B08"]
    ).ndvi(red="B04", nir="B08")

    # Submit and track job
    job = cube.create_job(title=f"NDVI_{start}", out_format="NetCDF")
    job.start_and_wait()
    
    # Download result
    outfile = base_path / f"ndvi_{i:02d}.nc"
    job.download_result(outfile)

    # Load NDVI slice and store it
    ds = xr.open_dataset(outfile)
    ndvi_slice = ds["var"].isel(t=0)
    all_ndvi_slices.append((start, ndvi_slice))
    ds.close()

# Generate animation frames
frames = []
for i, (date, ndvi) in enumerate(all_ndvi_slices):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(ndvi, cmap="RdYlGn", vmin=0, vmax=1)
    ax.set_title(f"NDVI – {date}")
    ax.axis('off')
    fname = frames_dir / f"frame_{i:03d}.png"
    plt.tight_layout()
    plt.savefig(fname)
    plt.close()
    frames.append(imageio.imread(fname))

# Save animation
gif_path = base_path / "houston_ndvi_2021.gif"
imageio.mimsave(gif_path, frames, duration=1.0)
print(f"\n Saved NDVI animation: {gif_path}")
```
