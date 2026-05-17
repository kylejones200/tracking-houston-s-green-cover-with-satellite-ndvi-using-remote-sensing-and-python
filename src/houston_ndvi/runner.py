"""Command-line interface for Houston NDVI analysis."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any

from houston_ndvi import __version__
from houston_ndvi.agreement import monthly_kappa_series
from houston_ndvi.config import load_config
from houston_ndvi.electrification import run_electrification_analysis
from houston_ndvi.gif import build_comparison_gif
from houston_ndvi.io_disk import load_years_from_disk
from houston_ndvi.openeo_fetch import connect_openeo, download_years
from houston_ndvi.paths import PROJECT_ROOT, ensure_output_dirs
from houston_ndvi.plotting import (
    plot_kappa_series,
    plot_monthly_comparison,
    plot_ndvi_delta,
    plot_ndvi_timeseries,
)
from houston_ndvi.timeseries import (
    annual_means,
    load_mean_ndvi_series,
    months_above_threshold,
    pivot_monthly,
)

logger = logging.getLogger(__name__)


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")


def resolve_paths(
    config: dict[str, Any], output_root: Path | None
) -> tuple[Path, Path, Path]:
    root = output_root or PROJECT_ROOT
    data_dir = root / config["output"]["data_dir"]
    frames_dir = root / config["output"]["frames_dir"]
    figures_dir = root / config["output"]["figures_dir"]
    for path in (data_dir, frames_dir, figures_dir):
        path.mkdir(parents=True, exist_ok=True)
    return data_dir, frames_dir, figures_dir


def run_fetch(config: dict[str, Any], data_dir: Path) -> None:
    """Download Sentinel-2 NDVI via openEO (requires OIDC authentication)."""
    connection = connect_openeo(config["openeo"]["endpoint"])
    download_years(connection, config["analysis"]["years"], config, data_dir)


def run_gif(config: dict[str, Any], data_dir: Path, frames_dir: Path) -> Path:
    """Build comparison GIF from NetCDF files on disk."""
    years = config["analysis"]["compare_years"]
    slices = load_years_from_disk(years, data_dir)
    gif_path = data_dir.parent / f"houston_ndvi_{years[0]}_vs_{years[1]}.gif"
    return build_comparison_gif(slices, years, frames_dir, gif_path, config)


def run_analyze(
    config: dict[str, Any], data_dir: Path, figures_dir: Path, *, show: bool
) -> None:
    """Generate NDVI time-series and comparison figures."""
    frame = load_mean_ndvi_series(data_dir)
    if frame.empty:
        raise FileNotFoundError(f"No NetCDF files matching ndvi_*.nc in {data_dir}")

    years = config["analysis"]["compare_years"]
    threshold = config["analysis"]["green_threshold"]
    pivot = pivot_monthly(frame)

    plot_ndvi_timeseries(frame, figures_dir / "ndvi_timeseries.png", show=show)
    plot_monthly_comparison(pivot, figures_dir / "ndvi_monthly_comparison.png", show=show)
    plot_monthly_comparison(
        pivot,
        figures_dir / "ndvi_monthly_comparison_minimalist.png",
        minimalist=True,
        show=show,
    )
    if len(years) >= 2:
        plot_ndvi_delta(
            pivot,
            tuple(years[:2]),
            figures_dir / f"ndvi_delta_{years[1]}_minus_{years[0]}.png",
            show=show,
        )

    means = annual_means(pivot)
    logger.info("Annual NDVI means:\n%s", means.to_string())
    if len(years) >= 2:
        logger.info(
            "Change in annual mean NDVI: %.4f",
            means[years[1]] - means[years[0]],
        )
    logger.info(
        "Months with NDVI > %.2f:\n%s",
        threshold,
        months_above_threshold(pivot, threshold).to_string(),
    )


def run_kappa(
    config: dict[str, Any], data_dir: Path, figures_dir: Path, *, show: bool
) -> None:
    """Compute and plot Cohen's kappa for vegetation class agreement."""
    years = config["analysis"]["compare_years"]
    if len(years) < 2:
        raise ValueError("compare_years must include two years for kappa analysis")

    analysis = config["analysis"]
    kappa_frame = monthly_kappa_series(
        data_dir,
        (years[0], years[1]),
        low=analysis["ndvi_low"],
        medium=analysis["ndvi_medium"],
    )
    if kappa_frame.empty:
        raise FileNotFoundError(f"No paired NetCDF files for {years} in {data_dir}")

    plot_kappa_series(kappa_frame, figures_dir / "ndvi_kappa_timeseries.png", show=show)
    plot_kappa_series(
        kappa_frame,
        figures_dir / "ndvi_kappa_minimalist.png",
        minimalist=True,
        show=show,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Track Houston green cover with Sentinel-2 NDVI (openEO + Python)",
    )
    parser.add_argument(
        "command",
        choices=["fetch", "gif", "analyze", "kappa", "electrification", "all"],
        help="Pipeline step to run",
    )
    parser.add_argument("--config", type=Path, default=None, help="Path to config.yaml")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Override project root for outputs (default: repository root)",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display matplotlib figures interactively",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args()

    configure_logging(args.verbose)
    config = load_config(args.config)
    ensure_output_dirs()
    data_dir, frames_dir, figures_dir = resolve_paths(config, args.output_dir)

    if args.command == "fetch":
        run_fetch(config, data_dir)
    elif args.command == "gif":
        run_gif(config, data_dir, frames_dir)
    elif args.command == "analyze":
        run_analyze(config, data_dir, figures_dir, show=args.show)
    elif args.command == "kappa":
        run_kappa(config, data_dir, figures_dir, show=args.show)
    elif args.command == "electrification":
        cache_dir = data_dir / "cache"
        run_electrification_analysis(config, cache_dir, show=args.show)
    else:
        run_gif(config, data_dir, frames_dir)
        run_analyze(config, data_dir, figures_dir, show=args.show)
        run_kappa(config, data_dir, figures_dir, show=args.show)


if __name__ == "__main__":
    main()
