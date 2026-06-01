"""Load project configuration from YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from houston_ndvi.paths import PROJECT_ROOT

DEFAULT_CONFIG = PROJECT_ROOT / "config.yaml"


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load and return the project configuration dictionary."""
    path = config_path or DEFAULT_CONFIG
    with path.open() as handle:
        return yaml.safe_load(handle)
