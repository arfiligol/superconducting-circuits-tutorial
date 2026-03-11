from collections.abc import Generator

import pytest
from src.app.infrastructure.runtime import reset_runtime_state


@pytest.fixture(autouse=True)
def reset_runtime_dependencies() -> Generator[None, None, None]:
    reset_runtime_state()
    yield
    reset_runtime_state()
