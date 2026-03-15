from __future__ import annotations

import json
import os
import re
import signal
import socket
import subprocess
import time
from http.client import RemoteDisconnected
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pytest
from playwright.sync_api import Page, expect, sync_playwright

_RUN_REWRITE_E2E = os.getenv("RUN_REWRITE_CHARACTERIZATION_REGISTRY_HISTORY_E2E") == "1"

pytestmark = pytest.mark.skipif(
    not _RUN_REWRITE_E2E,
    reason=(
        "Set RUN_REWRITE_CHARACTERIZATION_REGISTRY_HISTORY_E2E=1 to run rewrite frontend "
        "characterization registry/run-history Playwright coverage."
    ),
)


def _wait_for_server(url: str, timeout_seconds: float = 90.0) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=2.0):
                return
        except (HTTPError, RemoteDisconnected, URLError):
            time.sleep(0.5)
    raise TimeoutError(f"Timed out waiting for server at {url}")


def _json_request(url: str, payload: dict[str, object]) -> dict[str, object]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="PATCH",
    )
    with urlopen(request, timeout=5.0) as response:
        return json.loads(response.read().decode("utf-8"))


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        return int(sock.getsockname()[1])


def _ensure_frontend_dependencies(frontend_dir: Path) -> None:
    next_binary = frontend_dir / "node_modules" / ".bin" / "next"
    if next_binary.exists():
        return
    subprocess.run(["npm", "ci"], cwd=frontend_dir, check=True)


def _terminate_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)


@pytest.fixture(scope="session")
def rewrite_stack(tmp_path_factory: pytest.TempPathFactory) -> dict[str, str]:
    repo_root = Path(__file__).resolve().parents[3]
    backend_dir = repo_root / "backend"
    frontend_dir = repo_root / "frontend"
    _ensure_frontend_dependencies(frontend_dir)

    backend_port = int(os.getenv("REWRITE_CHARACTERIZATION_REGISTRY_HISTORY_BACKEND_PORT", "0")) or _find_free_port()
    frontend_port = int(os.getenv("REWRITE_CHARACTERIZATION_REGISTRY_HISTORY_FRONTEND_PORT", "0")) or _find_free_port()
    backend_base_url = f"http://127.0.0.1:{backend_port}"
    frontend_base_url = f"http://127.0.0.1:{frontend_port}"

    log_dir = tmp_path_factory.mktemp("rewrite_characterization_registry_history")
    backend_log = (log_dir / "backend.log").open("w", encoding="utf-8")
    frontend_log = (log_dir / "frontend.log").open("w", encoding="utf-8")

    backend_process = subprocess.Popen(
        [
            "uv",
            "run",
            "uvicorn",
            "src.app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(backend_port),
        ],
        cwd=backend_dir,
        env=os.environ.copy(),
        stdout=backend_log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        text=True,
    )

    frontend_env = os.environ.copy()
    frontend_env["BACKEND_BASE_URL"] = backend_base_url
    frontend_process = subprocess.Popen(
        [
            "npm",
            "run",
            "dev",
            "--",
            "--hostname",
            "127.0.0.1",
            "--port",
            str(frontend_port),
        ],
        cwd=frontend_dir,
        env=frontend_env,
        stdout=frontend_log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        text=True,
    )

    try:
        _wait_for_server(f"{backend_base_url}/session")
        _wait_for_server(f"{frontend_base_url}/characterization")
        _wait_for_server(f"{frontend_base_url}/api/backend/session")
        yield {
            "backend_base_url": backend_base_url,
            "frontend_base_url": frontend_base_url,
        }
    finally:
        _terminate_process(frontend_process)
        _terminate_process(backend_process)
        backend_log.close()
        frontend_log.close()


@pytest.fixture
def page(rewrite_stack: dict[str, str]) -> Page:
    _ = rewrite_stack
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1600})
        page = context.new_page()
        yield page
        context.close()
        browser.close()


@pytest.fixture(autouse=True)
def reset_shell_session(rewrite_stack: dict[str, str]) -> None:
    backend_base_url = rewrite_stack["backend_base_url"]
    _json_request(
        f"{backend_base_url}/session/active-workspace",
        {"workspace_id": "ws-device-lab"},
    )
    _json_request(
        f"{backend_base_url}/session/active-dataset",
        {"dataset_id": "fluxonium-2025-031"},
    )


def _capture_console_errors(page: Page) -> list[str]:
    console_errors: list[str] = []
    ignored_prefixes = ("Failed to load resource:",)
    ignored_substrings = ("useInsertionEffect must not schedule updates.",)

    def _listener(message) -> None:  # type: ignore[no-untyped-def]
        if message.type != "error":
            return
        if message.text.startswith(ignored_prefixes):
            return
        if any(segment in message.text for segment in ignored_substrings):
            return
        console_errors.append(message.text)

    page.on("console", _listener)
    return console_errors


def _dataset_trigger_pattern(dataset_name: str) -> re.Pattern[str]:
    return re.compile(
        rf"ACTIVE DATASET\s+{re.escape(dataset_name)}",
        re.IGNORECASE | re.DOTALL,
    )


def _surface_panel(page: Page, title: str):
    return page.locator("section").filter(has=page.get_by_text(title, exact=True)).first


def _assert_no_queue_substitute_controls(run_history_panel) -> None:
    expect(run_history_panel.get_by_role("button", name=re.compile(r"Attach", re.IGNORECASE))).to_have_count(0)
    expect(run_history_panel.get_by_role("button", name=re.compile(r"Cancel", re.IGNORECASE))).to_have_count(0)
    expect(run_history_panel.get_by_role("button", name=re.compile(r"Terminate", re.IGNORECASE))).to_have_count(0)
    expect(run_history_panel.get_by_role("button", name=re.compile(r"Retry", re.IGNORECASE))).to_have_count(0)


def test_rewrite_characterization_registry_filters_run_history_and_stays_read_only(
    page: Page,
    rewrite_stack: dict[str, str],
) -> None:
    console_errors = _capture_console_errors(page)

    page.goto(f"{rewrite_stack['frontend_base_url']}/characterization", wait_until="domcontentloaded")

    expect(
        page.get_by_role(
            "button",
            name=_dataset_trigger_pattern("Fluxonium sweep 031"),
        )
    ).to_be_visible(timeout=30000)

    registry_panel = _surface_panel(page, "Analysis Registry")
    run_history_panel = _surface_panel(page, "Run History")
    detail_panel = _surface_panel(page, "Persisted Result Detail")

    expect(registry_panel.get_by_text("does not submit or attach analyses", exact=False)).to_be_visible(
        timeout=30000
    )
    expect(
        run_history_panel.get_by_text("does not replace the shared task queue", exact=False)
    ).to_be_visible(timeout=30000)
    _assert_no_queue_substitute_controls(run_history_panel)
    expect(page.get_by_role("main").get_by_role("button", name=re.compile(r"Run Analysis", re.IGNORECASE))).to_have_count(0)
    expect(page.get_by_role("main").get_by_role("button", name="Save Profile")).to_have_count(0)

    expect(registry_panel.get_by_text("Trace context 2", exact=False)).to_be_visible(timeout=30000)
    registry_panel.get_by_role(
        "button",
        name=re.compile(r"Sideband Comparison\s+sideband_comparison", re.IGNORECASE | re.DOTALL),
    ).click()

    expect(run_history_panel.get_by_text("Sideband Comparison", exact=True)).to_be_visible(
        timeout=30000
    )
    expect(run_history_panel.get_by_text("Filtered", exact=True)).to_be_visible(timeout=30000)
    expect(
        run_history_panel.get_by_role(
            "button",
            name=re.compile(r"Flux Scan A sideband comparison", re.IGNORECASE),
        )
    ).to_be_visible(timeout=30000)
    expect(run_history_panel.get_by_text("Flux Scan A admittance fit", exact=True)).to_have_count(0)
    expect(
        detail_panel.get_by_role(
            "heading",
            name=re.compile(r"Flux Scan A admittance fit", re.IGNORECASE),
        )
    ).to_be_visible(timeout=30000)
    assert not console_errors


def test_rewrite_characterization_run_history_row_binds_existing_result_detail(
    page: Page,
    rewrite_stack: dict[str, str],
) -> None:
    console_errors = _capture_console_errors(page)

    page.goto(f"{rewrite_stack['frontend_base_url']}/characterization", wait_until="domcontentloaded")

    registry_panel = _surface_panel(page, "Analysis Registry")
    run_history_panel = _surface_panel(page, "Run History")
    result_panel = _surface_panel(page, "Result Summary List")
    detail_panel = _surface_panel(page, "Persisted Result Detail")

    expect(registry_panel.get_by_text("Trace context 2", exact=False)).to_be_visible(timeout=30000)
    run_history_panel.get_by_role(
        "button",
        name=re.compile(r"Flux Scan A sideband comparison", re.IGNORECASE),
    ).click()

    expect(
        detail_panel.get_by_role(
            "heading",
            name=re.compile(r"Flux Scan A sideband comparison", re.IGNORECASE),
        )
    ).to_be_visible(timeout=30000)
    expect(detail_panel.get_by_text("sideband_comparison", exact=False)).to_be_visible(timeout=30000)
    expect(detail_panel.get_by_text("sideband_peak_missing", exact=True)).to_be_visible(timeout=30000)
    expect(
        run_history_panel.get_by_text(
            "Open persisted detail char-sideband-flux-a-02",
            exact=False,
        )
    ).to_be_visible(timeout=30000)
    expect(registry_panel.get_by_text("Trace context 1", exact=False)).to_be_visible(timeout=30000)
    expect(
        result_panel.get_by_role(
            "button",
            name=re.compile(r"Flux Scan A sideband comparison", re.IGNORECASE),
        )
    ).to_be_visible(timeout=30000)
    assert not console_errors
