"""Temporal windows for monthly NDVI composites."""

from __future__ import annotations

from datetime import datetime


def monthly_intervals(year: int) -> list[tuple[str, str]]:
    """Return 10-day windows starting on the first of each month."""
    return [
        (
            datetime(year, month, 1).strftime("%Y-%m-%d"),
            datetime(year, month, 10).strftime("%Y-%m-%d"),
        )
        for month in range(1, 13)
    ]
