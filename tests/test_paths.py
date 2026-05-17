from houston_ndvi.paths import DATA_DIR, FIGURES_DIR, FRAMES_DIR, PROJECT_ROOT


def test_project_root_has_pyproject() -> None:
    assert PROJECT_ROOT.is_dir()
    assert (PROJECT_ROOT / "pyproject.toml").is_file()


def test_output_dirs_under_outputs() -> None:
    assert DATA_DIR == PROJECT_ROOT / "outputs" / "data"
    assert FRAMES_DIR == PROJECT_ROOT / "outputs" / "frames"
    assert FIGURES_DIR == PROJECT_ROOT / "outputs" / "figures"
