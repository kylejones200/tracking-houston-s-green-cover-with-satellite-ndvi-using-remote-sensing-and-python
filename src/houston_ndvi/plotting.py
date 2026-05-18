"""Matplotlib figures for NDVI time series and agreement analysis."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _minimal_axes(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(direction="out", length=4, width=0.5)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontfamily("serif")
        label.set_fontsize(10)


def plot_ndvi_timeseries(
    frame: pd.DataFrame,
    output_path: Path,
    *,
    dpi: int = 300,
    show: bool = False,
) -> Path:
    """Plot mean NDVI over time."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(frame["date"], frame["ndvi"], marker="o", color="forestgreen")
    ax.set_title("Monthly Mean NDVI")
    ax.set_xlabel("Date")
    ax.set_ylabel("Mean NDVI")
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    if show:
        plt.show()
    else:
        plt.close(fig)
    return output_path


def plot_monthly_comparison(
    pivot: pd.DataFrame,
    output_path: Path,
    *,
    dpi: int = 300,
    minimalist: bool = False,
    show: bool = False,
) -> Path:
    """Plot month-by-month NDVI for each year in the pivot table."""
    fig, ax = plt.subplots(figsize=(10, 4 if minimalist else 6))
    if minimalist:
        for year in pivot.columns:
            ax.plot(pivot.index, pivot[year], linewidth=1, label=str(year))
        _minimal_axes(ax)
        ax.legend(frameon=False, prop={"family": "serif", "size": 10})
        ax.set_title("NDVI by Month (2017 v 2023)")
    else:
        pivot.plot(marker="o", ax=ax, title="Monthly Mean NDVI – 2017 vs 2023")
        ax.set_ylabel("NDVI")
        ax.set_xlabel("Month")
        ax.grid(True)

    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    if show:
        plt.show()
    else:
        plt.close(fig)
    return output_path


def plot_ndvi_delta(
    pivot: pd.DataFrame,
    years: tuple[int, int],
    output_path: Path,
    *,
    dpi: int = 300,
    show: bool = False,
) -> Path:
    """Plot the difference in monthly mean NDVI between two years."""
    year_new, year_old = years[1], years[0]
    delta = pivot[year_new] - pivot[year_old]
    fig, ax = plt.subplots(figsize=(10, 5))
    delta.plot(marker="o", color="darkred", ax=ax, title=f"NDVI Change ({year_new} – {year_old})")
    ax.axhline(0, color="gray", linestyle="--")
    ax.set_ylabel("Δ NDVI")
    ax.set_xlabel("Month")
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    if show:
        plt.show()
    else:
        plt.close(fig)
    return output_path


def plot_kappa_series(
    kappa_frame: pd.DataFrame,
    output_path: Path,
    *,
    dpi: int = 300,
    minimalist: bool = False,
    show: bool = False,
) -> Path:
    """Plot Cohen's kappa by month."""
    fig, ax = plt.subplots(figsize=(10, 4 if minimalist else 5))
    color = "black" if minimalist else "purple"
    ax.plot(kappa_frame["month"], kappa_frame["kappa"], marker="o", color=color, linewidth=1)
    ax.axhline(0, linestyle="--", color="gray" if not minimalist else "black", linewidth=0.5)
    ax.set_xlabel("Month")
    ax.set_ylabel("Kappa Score")
    ax.grid(True)
    if minimalist:
        _minimal_axes(ax)
        title = "Cohen’s Kappa: Month vs Month NDVI Class Agreement (2017 vs 2023)"
    else:
        title = "Cohen’s Kappa: NDVI Class Agreement (2017 vs 2023)"

    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    if show:
        plt.show()
    else:
        plt.close(fig)
    return output_path
