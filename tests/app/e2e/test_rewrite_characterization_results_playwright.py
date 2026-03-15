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

_RUN_REWRITE_E2E = os.getenv("RUN_REWRITE_CHARACTERIZATION_RESULTS_E2E") == "1"

pytestmark = pytest.mark.skipif(
    not _RUN_REWRITE_E2E,
    reason=(
        "Set RUN_REWRITE_CHARACTERIZATION_RESULTS_E2E=1 to run rewrite frontend "
        "characterization results Playwright coverage."
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

    backend_port = int(os.getenv("REWRITE_CHARACTERIZATION_RESULTS_BACKEND_PORT", "0")) or _find_free_port()
    frontend_port = int(os.getenv("REWRITE_CHARACTERIZATION_RESULTS_FRONTEND_PORT", "0")) or _find_free_port()
    backend_base_url = f"http://127.0.0.1:{backend_port}"
    frontend_base_url = f"http://127.0.0.1:{frontend_port}"

    log_dir = tmp_path_factory.mktemp("rewrite_characterization_results")
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


def _dataset_trigger_pattern(dataset_name: str, badge: str) -> re.Pattern[str]:
    return re.compile(
        rf"ACTIVE DATASET\s+{re.escape(dataset_name)}\s+{re.escape(badge)}",
        re.IGNORECASE | re.DOTALL,
    )


def _no_dataset_trigger_pattern() -> re.Pattern[str]:
    return re.compile(
        r"ACTIVE DATASET\s+No active dataset\s+Select one from Raw Data to attach it to the session\.",
        re.IGNORECASE | re.DOTALL,
    )


def _open_dataset_panel(page: Page) -> None:
    search_input = page.get_by_placeholder("Search by name, id, family, owner, or device")
    if search_input.is_visible():
        return
    page.get_by_role("button", name=re.compile(r"ACTIVE DATASET", re.IGNORECASE)).click()
    expect(search_input).to_be_visible(timeout=30000)


def _assert_no_execution_controls(page: Page) -> None:
    main = page.get_by_role("main")
    expect(main.get_by_role("button", name=re.compile(r"Run Analysis", re.IGNORECASE))).to_have_count(0)
    expect(main.get_by_role("button", name=re.compile(r"Attach Task", re.IGNORECASE))).to_have_count(0)
    expect(main.get_by_role("button", name=re.compile(r"Rerun", re.IGNORECASE))).to_have_count(0)


def _surface_panel(page: Page, title: str):
    return page.locator("section").filter(has=page.get_by_text(title, exact=True)).first


def test_rewrite_characterization_requires_active_dataset_then_binds_persisted_results(
    page: Page,
    rewrite_stack: dict[str, str],
) -> None:
    console_errors = _capture_console_errors(page)
    _json_request(
        f"{rewrite_stack['backend_base_url']}/session/active-dataset",
        {"dataset_id": None},
    )

    page.goto(f"{rewrite_stack['frontend_base_url']}/characterization", wait_until="domcontentloaded")

    expect(page.get_by_role("heading", name="Characterization")).to_be_visible(timeout=30000)
    expect(page.get_by_text("Persisted Results", exact=True)).to_be_visible(timeout=30000)
    expect(page.get_by_text("Attach Active Dataset", exact=True)).to_be_visible(timeout=30000)
    expect(
        page.get_by_text(
            "Characterization results are always scoped to the shared shell active dataset.",
            exact=False,
        )
    ).to_be_visible(timeout=30000)
    expect(page.get_by_role("button", name=_no_dataset_trigger_pattern())).to_be_visible(
        timeout=30000
    )
    _assert_no_execution_controls(page)

    _open_dataset_panel(page)
    page.get_by_placeholder("Search by name, id, family, owner, or device").fill("fluxonium")
    page.get_by_role(
        "button",
        name=re.compile(r"Fluxonium sweep 031\s+FLUXONIUM-2025-031", re.IGNORECASE | re.DOTALL),
    ).click()

    expect(
        page.get_by_text("Active dataset switched to Fluxonium sweep 031.", exact=False)
    ).to_be_visible(timeout=30000)
    expect(
        page.get_by_role(
            "button",
            name=_dataset_trigger_pattern("Fluxonium sweep 031", "READY"),
        )
    ).to_be_visible(timeout=30000)
    design_panel = _surface_panel(page, "Design Scope")
    result_panel = _surface_panel(page, "Result Summary List")
    detail_panel = _surface_panel(page, "Persisted Result Detail")

    expect(page.get_by_text("Design Scope", exact=True)).to_be_visible(timeout=30000)
    expect(
        design_panel.get_by_role(
            "button",
            name=re.compile(r"Flux Scan A\s+design_flux_scan_a", re.IGNORECASE | re.DOTALL),
        )
    ).to_be_visible(
        timeout=30000
    )
    expect(page.get_by_text("Result Summary List", exact=True)).to_be_visible(timeout=30000)
    expect(result_panel.get_by_role("button", name=re.compile(r"Flux Scan A admittance fit", re.IGNORECASE))).to_be_visible(timeout=30000)
    expect(page.get_by_text("Persisted Result Detail", exact=True)).to_be_visible(timeout=30000)
    expect(
        detail_panel.get_by_role("heading", name=re.compile(r"Flux Scan A admittance fit", re.IGNORECASE))
    ).to_be_visible(timeout=30000)
    expect(detail_panel.get_by_text("Fit table", exact=True)).to_be_visible(timeout=30000)
    expect(detail_panel.get_by_text("Admittance overlay", exact=True)).to_be_visible(timeout=30000)
    expect(detail_panel.get_by_text('"parameter": "f01"', exact=False)).to_be_visible(timeout=30000)
    _assert_no_execution_controls(page)
    assert not console_errors


def test_rewrite_characterization_dataset_switch_rebinds_design_and_result_context(
    page: Page,
    rewrite_stack: dict[str, str],
) -> None:
    console_errors = _capture_console_errors(page)

    page.goto(f"{rewrite_stack['frontend_base_url']}/characterization", wait_until="domcontentloaded")

    expect(
        page.get_by_role(
            "button",
            name=_dataset_trigger_pattern("Fluxonium sweep 031", "READY"),
        )
    ).to_be_visible(timeout=30000)
    result_panel = _surface_panel(page, "Result Summary List")
    detail_panel = _surface_panel(page, "Persisted Result Detail")
    design_panel = _surface_panel(page, "Design Scope")

    result_panel.get_by_role(
        "button",
        name=re.compile(r"Flux Scan A sideband comparison", re.IGNORECASE),
    ).click()

    expect(
        detail_panel.get_by_role(
            "heading",
            name=re.compile(r"Flux Scan A sideband comparison", re.IGNORECASE),
        )
    ).to_be_visible(
        timeout=30000
    )
    expect(detail_panel.get_by_text("sideband_peak_missing", exact=True)).to_be_visible(timeout=30000)
    expect(
        detail_panel.get_by_text(
            "No stable sideband peak was detected in the selected trace bundle.",
            exact=True,
        )
    ).to_be_visible(timeout=30000)

    _open_dataset_panel(page)
    page.get_by_placeholder("Search by name, id, family, owner, or device").fill("resonator")
    page.get_by_role(
        "button",
        name=re.compile(
            r"Readout resonator validation 002\s+RESONATOR-CHIP-002",
            re.IGNORECASE | re.DOTALL,
        ),
    ).click()

    expect(
        page.get_by_text("Active dataset switched to Readout resonator validation 002.", exact=False)
    ).to_be_visible(timeout=30000)
    expect(
        page.get_by_role(
            "button",
            name=_dataset_trigger_pattern("Readout resonator validation 002", "QUEUED"),
        )
    ).to_be_visible(timeout=30000)
    expect(
        design_panel.get_by_role(
            "button",
            name=re.compile(
                r"Temperature Sweep\s+design_resonator_temp",
                re.IGNORECASE | re.DOTALL,
            ),
        )
    ).to_be_visible(timeout=30000)
    expect(
        detail_panel.get_by_role(
            "heading",
            name=re.compile(r"Temperature sweep quality factor fit", re.IGNORECASE),
        )
    ).to_be_visible(timeout=30000)
    expect(detail_panel.get_by_text("Flux Scan A sideband comparison", exact=True)).to_have_count(0)
    expect(
        detail_panel.get_by_text(
            "No diagnostics were attached to this persisted result detail.",
            exact=True,
        )
    ).to_be_visible(timeout=30000)
    expect(detail_panel.get_by_text("Quality factor table", exact=True)).to_be_visible(timeout=30000)
    expect(detail_panel.get_by_text("Temperature fit plot", exact=True)).to_be_visible(timeout=30000)
    _assert_no_execution_controls(page)

    _open_dataset_panel(page)
    page.get_by_role("button", name=re.compile(r"clear dataset", re.IGNORECASE)).click()

    expect(
        page.get_by_text("Active dataset cleared for the current workspace.", exact=False)
    ).to_be_visible(timeout=30000)
    expect(page.get_by_role("button", name=_no_dataset_trigger_pattern())).to_be_visible(
        timeout=30000
    )
    expect(page.get_by_text("Attach Active Dataset", exact=True)).to_be_visible(timeout=30000)
    expect(detail_panel.get_by_text("Temperature sweep quality factor fit", exact=True)).to_have_count(0)
    _assert_no_execution_controls(page)
    assert not console_errors
