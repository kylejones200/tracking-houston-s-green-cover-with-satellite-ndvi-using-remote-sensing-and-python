"""Repository root and default output paths."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUTS_DIR = PROJECT_ROOT / "outputs"
DATA_DIR = OUTPUTS_DIR / "data"
FRAMES_DIR = OUTPUTS_DIR / "frames"
FIGURES_DIR = OUTPUTS_DIR / "figures"


def ensure_output_dirs() -> None:
    """Create standard output directories if they do not exist."""
    for path in (DATA_DIR, FRAMES_DIR, FIGURES_DIR):
        path.mkdir(parents=True, exist_ok=True)


def figure_path(name: str) -> Path:
    """Return path under outputs/figures/, creating the directory if needed."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    return FIGURES_DIR / name


def data_path(name: str) -> Path:
    """Return path under outputs/data/, creating the directory if needed."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR / name
