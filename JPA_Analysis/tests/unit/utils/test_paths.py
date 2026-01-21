from src.utils import DATA_DIR, PROJECT_ROOT, RAW_LAYOUT_ADMITTANCE_DIR


def test_project_root_exists():
    """Test that PROJECT_ROOT points to a valid directory."""
    assert PROJECT_ROOT.exists()
    assert PROJECT_ROOT.is_dir()
    assert (PROJECT_ROOT / "pyproject.toml").exists()


def test_data_dir_structure():
    """Test that key data directories exist."""
    # Note: This test depends on the environment having the data folder.
    # In a clean CI environment, we might need to create them or mock them.
    # For now, we test the current dev environment.

    if DATA_DIR.exists():
        assert DATA_DIR.is_dir()
        assert (DATA_DIR / "raw").exists()
        assert (DATA_DIR / "preprocessed").exists()


def test_path_relativity():
    """Test that constants are relative to PROJECT_ROOT."""
    assert RAW_LAYOUT_ADMITTANCE_DIR.is_relative_to(PROJECT_ROOT)
