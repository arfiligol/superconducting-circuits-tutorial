import sys
from pathlib import Path

import pytest

# Ensure src is in pythonpath
SRC_PATH = Path(__file__).parent.parent / "src"
sys.path.append(str(SRC_PATH))


@pytest.fixture
def sample_data_dir():
    """Return path to sample data directory (if we create one)."""
    return Path(__file__).parent / "data"
