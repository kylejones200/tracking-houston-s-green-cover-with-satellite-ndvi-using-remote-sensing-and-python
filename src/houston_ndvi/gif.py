"""Build side-by-side NDVI comparison frames and animated GIFs."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import imageio
import matplotlib.pyplot as plt
import xarray as xr

logger = logging.getLogger(__name__)


def render_comparison_frame(
    slices_by_year: dict[int, list[tuple[str, xr.DataArray]]],
    years: list[int],
    month_index: int,
    output_path: Path,
    *,
    cmap: str,
    vmin: float,
    vmax: float,
    figsize: tuple[float, float],
) -> Path:
    """Save a two-panel PNG comparing NDVI for the same month across years."""
    fig, axes = plt.subplots(1, len(years), figsize=figsize)
    if len(years) == 1:
        axes = [axes]

    for axis, year in zip(axes, years, strict=True):
        start_date, ndvi = slices_by_year[year][month_index]
        axis.imshow(ndvi, cmap=cmap, vmin=vmin, vmax=vmax)
        axis.set_title(f"{year} – {start_date}")
        axis.axis("off")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    return output_path


def build_comparison_gif(
    slices_by_year: dict[int, list[tuple[str, xr.DataArray]]],
    years: list[int],
    frames_dir: Path,
    gif_path: Path,
    config: dict[str, Any],
) -> Path:
    """Render monthly frames and assemble a side-by-side comparison GIF."""
    gif_cfg = config["gif"]
    frames: list = []

    for month_index in range(12):
        frame_path = frames_dir / f"frame_{month_index:03d}.png"
        render_comparison_frame(
            slices_by_year,
            years,
            month_index,
            frame_path,
            cmap=gif_cfg["cmap"],
            vmin=gif_cfg["vmin"],
            vmax=gif_cfg["vmax"],
            figsize=tuple(gif_cfg["figsize"]),
        )
        frames.append(imageio.imread(frame_path))

    gif_path.parent.mkdir(parents=True, exist_ok=True)
    imageio.mimsave(gif_path, frames, duration=gif_cfg["duration_seconds"])
    logger.info("Saved comparison GIF: %s", gif_path)
    return gif_path
