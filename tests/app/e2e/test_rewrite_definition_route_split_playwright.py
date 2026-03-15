from __future__ import annotations

import json
import os
import re
import signal
import socket
import subprocess
import time
import uuid
from http.client import RemoteDisconnected
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pytest
from playwright.sync_api import Page, expect, sync_playwright

_RUN_REWRITE_E2E = os.getenv("RUN_REWRITE_DEFINITION_ROUTE_SPLIT_E2E") == "1"

pytestmark = pytest.mark.skipif(
    not _RUN_REWRITE_E2E,
    reason=(
        "Set RUN_REWRITE_DEFINITION_ROUTE_SPLIT_E2E=1 to run rewrite frontend "
        "definition route split Playwright coverage."
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


def _json_request(
    url: str,
    *,
    method: str = "GET",
    payload: dict[str, object] | None = None,
) -> dict[str, object] | None:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8") if payload is not None else None,
        headers={"Content-Type": "application/json"} if payload is not None else {},
        method=method,
    )
    with urlopen(request, timeout=5.0) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if body else None


def _build_definition_source(
    name: str,
    *,
    component_count: int,
    compact: bool,
) -> str:
    components = [
        {"name": "R1", "default": 50.0, "unit": "Ohm"},
        {"name": "C1", "default": 100.0, "unit": "fF"},
        {"name": "Lj1", "default": 1000.0, "unit": "pH"},
    ]
    topology = [
        ["P1", "1", "0", 1],
        ["R1", "1", "0", "R1"],
        ["C1", "1", "2", "C1"],
        ["Lj1", "2", "0", "Lj1"],
    ]
    document = {
        "name": name,
        "components": components[:component_count],
        "topology": topology[: component_count + 1],
    }
    if compact:
        return json.dumps(document, separators=(",", ":"))
    return json.dumps(document, indent=2)


@pytest.fixture(scope="session")
def rewrite_stack(tmp_path_factory: pytest.TempPathFactory) -> dict[str, str]:
    repo_root = Path(__file__).resolve().parents[3]
    backend_dir = repo_root / "backend"
    frontend_dir = repo_root / "frontend"
    _ensure_frontend_dependencies(frontend_dir)

    backend_port = int(os.getenv("REWRITE_DEFINITION_ROUTE_SPLIT_BACKEND_PORT", "0")) or _find_free_port()
    frontend_port = int(os.getenv("REWRITE_DEFINITION_ROUTE_SPLIT_FRONTEND_PORT", "0")) or _find_free_port()
    backend_base_url = f"http://127.0.0.1:{backend_port}"
    frontend_base_url = f"http://127.0.0.1:{frontend_port}"

    log_dir = tmp_path_factory.mktemp("rewrite_definition_route_split")
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
        _wait_for_server(f"{backend_base_url}/circuit-definitions")
        _wait_for_server(f"{frontend_base_url}/schemas")
        _wait_for_server(f"{frontend_base_url}/api/backend/circuit-definitions")
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


@pytest.fixture
def seeded_definition(rewrite_stack: dict[str, str]) -> dict[str, object]:
    suffix = uuid.uuid4().hex[:8]
    name = f"RouteSplitSmoke-{suffix}"
    payload = {
        "name": name,
        "source_text": _build_definition_source(name, component_count=3, compact=False),
    }
    created = _json_request(
        f"{rewrite_stack['backend_base_url']}/circuit-definitions",
        method="POST",
        payload=payload,
    )
    assert created is not None
    definition = created["definition"]
    assert isinstance(definition, dict)
    yield definition
    _json_request(
        f"{rewrite_stack['backend_base_url']}/circuit-definitions/{definition['definition_id']}",
        method="DELETE",
    )


def _capture_console_errors(page: Page) -> list[str]:
    console_errors: list[str] = []
    ignored_messages = {
        "useInsertionEffect must not schedule updates.",
    }

    def _listener(message) -> None:  # type: ignore[no-untyped-def]
        if (
            message.type == "error"
            and not message.text.startswith("Failed to load resource:")
            and message.text not in ignored_messages
        ):
            console_errors.append(message.text)

    page.on("console", _listener)
    return console_errors


def _schemas_link_is_active(page: Page) -> bool:
    return bool(
        page.get_by_role("link", name="Schemas").evaluate(
            "(element) => element.classList.contains('text-primary')",
        )
    )


def _replace_editor_source(page: Page, source_text: str) -> None:
    editor = page.locator(".cm-editor [contenteditable='true']").first
    expect(editor).to_be_visible(timeout=30000)
    editor.click()
    page.keyboard.press("Meta+A")
    page.keyboard.insert_text(source_text)


def _normalized_output_field_value(page: Page, label: str) -> str:
    normalized_output_section = page.locator("section").filter(
        has=page.get_by_role("heading", name="Normalized Output"),
    ).first
    label_locator = normalized_output_section.get_by_text(label, exact=True).first
    value = label_locator.locator("xpath=following-sibling::p[1]").text_content()
    assert value is not None
    return value.strip()


def test_rewrite_definition_routes_split_catalog_and_editor_responsibilities(
    page: Page,
    rewrite_stack: dict[str, str],
    seeded_definition: dict[str, object],
) -> None:
    console_errors = _capture_console_errors(page)

    page.goto(f"{rewrite_stack['frontend_base_url']}/schemas", wait_until="domcontentloaded")

    expect(page.get_by_role("heading", name="Schemas")).to_be_visible(timeout=30000)
    expect(page.get_by_text("Catalog authority only", exact=True)).to_be_visible(timeout=30000)
    expect(page.get_by_role("button", name="New Circuit")).to_be_visible(timeout=30000)
    expect(page.get_by_text("Browse, search, and open saved circuit definitions.")).to_be_visible(
        timeout=30000
    )
    expect(page.get_by_text("Canonical Source", exact=True)).to_have_count(0)
    expect(page.get_by_text("Validation & Preview", exact=True)).to_have_count(0)
    expect(page.get_by_text("Catalog Rail", exact=True)).to_have_count(0)
    assert _schemas_link_is_active(page) is True

    page.get_by_role("button", name="New Circuit").click()
    page.wait_for_url(re.compile(r"/circuit-definition-editor\?definitionId=new$"))

    expect(page.get_by_role("heading", name="Schema Editor")).to_be_visible(timeout=30000)
    expect(page.get_by_text("Edit one active circuit definition and inspect the last persisted preview.")).to_be_visible(timeout=30000)
    expect(page.get_by_text("Catalog Rail", exact=True)).to_be_visible(timeout=30000)
    expect(page.get_by_text("Canonical Source", exact=True)).to_be_visible(timeout=30000)
    expect(page.get_by_text("Validation & Preview", exact=True)).to_be_visible(timeout=30000)
    expect(page.get_by_text("Catalog authority only", exact=True)).to_have_count(0)
    assert _schemas_link_is_active(page) is False

    page.goto(f"{rewrite_stack['frontend_base_url']}/schemas", wait_until="domcontentloaded")
    page.get_by_placeholder("Find by name or id").fill(str(seeded_definition["name"]))
    page.get_by_role("button", name=str(seeded_definition["name"]), exact=True).click()
    page.wait_for_url(
        re.compile(
            rf"/circuit-definition-editor\?definitionId={seeded_definition['definition_id']}$"
        )
    )

    expect(page.get_by_role("heading", name="Schema Editor")).to_be_visible(timeout=30000)
    expect(page.get_by_text(str(seeded_definition["name"]), exact=True).last).to_be_visible(
        timeout=30000
    )
    expect(page.get_by_text("Active Schema", exact=True)).to_be_visible(timeout=30000)
    assert not console_errors


def test_rewrite_editor_persisted_preview_stays_stale_until_save(
    page: Page,
    rewrite_stack: dict[str, str],
    seeded_definition: dict[str, object],
) -> None:
    console_errors = _capture_console_errors(page)
    definition_id = seeded_definition["definition_id"]
    source_name = str(seeded_definition["name"])
    edited_source = _build_definition_source(f"{source_name}-edited", component_count=2, compact=True)

    page.goto(
        f"{rewrite_stack['frontend_base_url']}/circuit-definition-editor?definitionId={definition_id}",
        wait_until="domcontentloaded",
    )

    expect(page.get_by_role("heading", name="Schema Editor")).to_be_visible(timeout=30000)
    expect(page.get_by_text("Persisted Preview", exact=True)).to_be_visible(timeout=30000)
    expect(
        page.get_by_text(
            f"Backend validation is attached to definition #{definition_id}.",
            exact=True,
        )
    ).to_be_visible(timeout=30000)

    initial_elements = _normalized_output_field_value(page, "Elements")
    _replace_editor_source(page, edited_source)

    expect(page.get_by_text("Unsaved Changes", exact=True)).to_be_visible(timeout=30000)
    expect(page.get_by_text("Preview Out Of Date", exact=True)).to_be_visible(timeout=30000)
    expect(
        page.get_by_text(
            "Panels below still show the last persisted definition. Save to refresh them.",
            exact=True,
        )
    ).to_be_visible(timeout=30000)
    assert _normalized_output_field_value(page, "Elements") == initial_elements

    page.get_by_role("button", name="Format").click()

    expect(page.get_by_text("Preview Out Of Date", exact=True)).to_be_visible(timeout=30000)
    expect(
        page.get_by_text(
            "Panels below still show the last persisted definition. Save to refresh them.",
            exact=True,
        )
    ).to_be_visible(timeout=30000)
    expect(page.get_by_text("Circuit definition updated.", exact=True)).to_have_count(0)
    assert _normalized_output_field_value(page, "Elements") == initial_elements

    page.get_by_role("button", name="Save").click()

    expect(page.get_by_text("Circuit definition updated.", exact=True)).to_be_visible(timeout=30000)
    expect(page.get_by_text("Persisted Preview", exact=True)).to_be_visible(timeout=30000)

    saved_elements = _normalized_output_field_value(page, "Elements")
    assert saved_elements != initial_elements
    assert not console_errors
