from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolate_cli_runtime_store(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from sc_cli.runtime import reset_runtime_state

    runtime_root = tmp_path / "sc-runtime"
    monkeypatch.setenv("SC_CLI_RUNTIME_ROOT", str(runtime_root))
    reset_runtime_state()
    yield
    reset_runtime_state()
