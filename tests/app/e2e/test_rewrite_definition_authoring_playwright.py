"""Playwright harness for rewrite definition-authoring verification."""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import time
import uuid
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

import pytest
from playwright.sync_api import Page, Route, expect, sync_playwright
from sc_core.circuit_definitions import (
    DEFAULT_PREVIEW_ARTIFACTS,
    inspect_circuit_definition_source,
)

_RUN_PLAYWRIGHT_E2E = os.getenv("RUN_REWRITE_DEFINITION_AUTHORING_E2E") == "1"

pytestmark = pytest.mark.skipif(
    not _RUN_PLAYWRIGHT_E2E,
    reason=(
        "Set RUN_REWRITE_DEFINITION_AUTHORING_E2E=1 to run Playwright harness "
        "for rewrite definition-authoring flows."
    ),
)


def _wait_for_server(url: str, timeout_seconds: float = 60.0) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=2.0):
                return
        except URLError:
            time.sleep(0.5)
    raise TimeoutError(f"Timed out waiting for app server at {url}")


def _sample_session_payload() -> dict[str, object]:
    return {
        "session_id": "session-dev-001",
        "auth": {
            "state": "authenticated",
            "mode": "development_stub",
            "scopes": ["tasks:submit", "datasets:manage"],
            "can_submit_tasks": True,
            "can_manage_datasets": True,
        },
        "identity": {
            "user_id": "user-dev-01",
            "display_name": "Device Lab",
            "email": "device-lab@example.com",
        },
        "workspace": {
            "workspace_id": "workspace-lab",
            "slug": "device-lab",
            "display_name": "Device Lab",
            "role": "owner",
            "default_task_scope": "workspace",
            "active_dataset": None,
        },
    }


def _sample_definition_source(circuit_name: str) -> str:
    return (
        "circuit:\n"
        f"  name: {circuit_name}\n"
        "  family: fluxonium\n"
        "  elements:\n"
        "    junction:\n"
        "      ej_ghz: 8.45\n"
        "    shunt_inductor:\n"
        "      el_ghz: 0.42\n"
    )


def _build_definition_payload(
    definition_id: int,
    *,
    name: str,
    source_text: str,
    created_at: str,
) -> dict[str, object]:
    inspection = inspect_circuit_definition_source(source_text)
    warning_count = sum(1 for notice in inspection.validation_notices if notice.level == "warning")
    return {
        "definition_id": definition_id,
        "name": name,
        "created_at": created_at,
        "element_count": inspection.element_count,
        "validation_status": "warning" if warning_count else "ok",
        "preview_artifact_count": len(DEFAULT_PREVIEW_ARTIFACTS),
        "source_text": source_text,
        "normalized_output": inspection.normalized_output,
        "validation_notices": [
            {"level": notice.level, "message": notice.message}
            for notice in inspection.validation_notices
        ],
        "validation_summary": {
            "status": "warning" if warning_count else "ok",
            "notice_count": len(inspection.validation_notices),
            "warning_count": warning_count,
        },
        "preview_artifacts": list(DEFAULT_PREVIEW_ARTIFACTS),
    }


def _build_definition_summary(payload: dict[str, object]) -> dict[str, object]:
    return {
        "definition_id": payload["definition_id"],
        "name": payload["name"],
        "created_at": payload["created_at"],
        "element_count": payload["element_count"],
        "validation_status": payload["validation_status"],
        "preview_artifact_count": payload["preview_artifact_count"],
    }


def _seed_definition_state() -> dict[str, object]:
    definition = _build_definition_payload(
        18,
        name="FloatingQubitWithXYLine",
        source_text=_sample_definition_source("fluxonium_reference_a"),
        created_at="2026-03-08 18:19:42",
    )
    return {
        "next_definition_id": 19,
        "definitions": {
            18: definition,
        },
    }


def _fulfill_json(route: Route, payload: object, *, status: int = 200) -> None:
    route.fulfill(
        status=status,
        content_type="application/json",
        body=json.dumps(payload),
    )


def _replace_code_mirror_text(page: Page, value: str) -> None:
    editor = page.locator(".cm-content").first
    expect(editor).to_be_visible(timeout=15_000)
    editor.click()
    page.keyboard.press("Meta+A")
    page.keyboard.press("Backspace")
    page.keyboard.insert_text(value)


@pytest.fixture(scope="session")
def frontend_base_url(tmp_path_factory: pytest.TempPathFactory) -> str:
    port = int(os.getenv("PLAYWRIGHT_REWRITE_FRONTEND_PORT", "3104"))
    base_url = f"http://127.0.0.1:{port}"

    log_dir = tmp_path_factory.mktemp("rewrite_definition_authoring_frontend")
    log_path = log_dir / "frontend.log"
    log_file = log_path.open("w", encoding="utf-8")

    repo_root = Path(__file__).resolve().parents[3]
    process = subprocess.Popen(
        [
            "./node_modules/.bin/next",
            "dev",
            "--hostname",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=repo_root / "frontend",
        env=os.environ.copy(),
        stdout=log_file,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    try:
        _wait_for_server(base_url)
        yield base_url
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
        if not log_file.closed:
            log_file.close()


@pytest.fixture
def page(frontend_base_url: str) -> Page:
    definition_state = _seed_definition_state()

    def handle_backend(route: Route) -> None:
        request = route.request
        path = urlparse(request.url).path
        method = request.method

        if path == "/api/backend/session":
            _fulfill_json(route, _sample_session_payload())
            return

        if path == "/api/backend/tasks":
            _fulfill_json(route, [])
            return

        if path == "/api/backend/circuit-definitions":
            definitions = definition_state["definitions"]
            if method == "GET":
                payload = [
                    _build_definition_summary(definition)
                    for definition in sorted(
                        definitions.values(),
                        key=lambda item: item["created_at"],
                        reverse=True,
                    )
                ]
                _fulfill_json(route, payload)
                return

            if method == "POST":
                request_payload = request.post_data_json
                definition_id = int(definition_state["next_definition_id"])
                definition_state["next_definition_id"] = definition_id + 1
                definition = _build_definition_payload(
                    definition_id,
                    name=str(request_payload["name"]),
                    source_text=str(request_payload["source_text"]),
                    created_at="2026-03-15 09:00:00",
                )
                definitions[definition_id] = definition
                _fulfill_json(
                    route,
                    {"operation": "created", "definition": definition},
                    status=201,
                )
                return

        detail_match = re.fullmatch(r"/api/backend/circuit-definitions/(\d+)", path)
        if detail_match:
            definition_id = int(detail_match.group(1))
            definitions = definition_state["definitions"]
            definition = definitions.get(definition_id)
            if definition is None:
                _fulfill_json(
                    route,
                    {
                        "error": {
                            "error_code": "circuit_definition_not_found",
                            "category": "not_found",
                            "message": f"Circuit definition {definition_id} was not found.",
                        }
                    },
                    status=404,
                )
                return

            if method == "GET":
                _fulfill_json(route, definition)
                return

            if method == "PUT":
                request_payload = request.post_data_json
                updated_definition = _build_definition_payload(
                    definition_id,
                    name=str(request_payload["name"]),
                    source_text=str(request_payload["source_text"]),
                    created_at=str(definition["created_at"]),
                )
                definitions[definition_id] = updated_definition
                _fulfill_json(
                    route,
                    {"operation": "updated", "definition": updated_definition},
                )
                return

        route.continue_()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1600, "height": 1400})
        context.route("**/api/backend/**", handle_backend)
        page = context.new_page()
        yield page
        context.close()
        browser.close()


def test_rewrite_definition_authoring_catalog_editor_save_update_flow(
    page: Page,
    frontend_base_url: str,
) -> None:
    created_display_name = f"RewriteSmoke-{uuid.uuid4().hex[:6]}"
    updated_display_name = f"{created_display_name}-V2"
    created_source = _sample_definition_source("rewrite_definition_authoring_created")
    updated_source = _sample_definition_source("rewrite_definition_authoring_updated")

    page.goto(f"{frontend_base_url}/circuit-definition-editor?definitionId=18", wait_until="networkidle")

    expect(page.get_by_role("heading", name="Circuit Schemas")).to_be_visible(timeout=15_000)
    expect(page.get_by_text("FloatingQubitWithXYLine").first).to_be_visible(timeout=15_000)
    expect(page.get_by_text("Persisted Preview", exact=True).first).to_be_visible(timeout=15_000)

    page.get_by_role("button", name="New Circuit").click()
    expect(page.get_by_text("New Circuit Definition")).to_be_visible(timeout=10_000)
    expect(page.get_by_text("Draft Preview", exact=True).first).to_be_visible(timeout=10_000)

    page.get_by_role("textbox", name="Name").fill(created_display_name)
    _replace_code_mirror_text(page, created_source)
    expect(page.get_by_text("Unsaved Changes", exact=True).first).to_be_visible(timeout=10_000)
    expect(page.get_by_role("button", name="Save")).to_be_enabled(timeout=10_000)

    page.get_by_role("button", name="Save").click()
    expect(page.get_by_text("Circuit definition created.")).to_be_visible(timeout=10_000)
    expect(page).to_have_url(re.compile(r"definitionId=19$"), timeout=10_000)
    expect(page.get_by_text("Persisted Preview", exact=True).first).to_be_visible(timeout=10_000)
    expect(page.get_by_text(created_display_name).first).to_be_visible(timeout=10_000)
    expect(
        page.get_by_text("rewrite_definition_authoring_created", exact=False).first
    ).to_be_visible(timeout=10_000)

    page.get_by_role("textbox", name="Name").fill(updated_display_name)
    _replace_code_mirror_text(page, updated_source)
    expect(page.get_by_text("Preview Out Of Date", exact=True).first).to_be_visible(timeout=10_000)

    page.get_by_role("button", name="Save").click()
    expect(page.get_by_text("Circuit definition updated.")).to_be_visible(timeout=10_000)
    expect(page.get_by_text("Persisted Preview", exact=True).first).to_be_visible(timeout=10_000)
    expect(page.get_by_text(updated_display_name).first).to_be_visible(timeout=10_000)
    expect(
        page.get_by_text("rewrite_definition_authoring_updated", exact=False).first
    ).to_be_visible(timeout=10_000)


@pytest.mark.xfail(
    reason=(
        "Blocked by missing rewrite schemdraw authoring implementation: the current page "
        "does not expose relation config editing, Render Now, diagnostics rendering, or SVG preview."
    ),
    strict=False,
)
def test_rewrite_schemdraw_render_request_response_and_svg_preview_flow(
    page: Page,
    frontend_base_url: str,
) -> None:
    page.goto(f"{frontend_base_url}/circuit-schemdraw?definitionId=18", wait_until="networkidle")

    expect(page.get_by_role("heading", name="Circuit Schemdraw")).to_be_visible(timeout=15_000)
    expect(page.get_by_role("button", name="Render Now")).to_be_visible(timeout=5_000)
    expect(page.get_by_text("Diagnostics")).to_be_visible(timeout=5_000)
    expect(page.locator("svg").nth(0)).to_be_visible(timeout=5_000)


@pytest.mark.xfail(
    reason=(
        "Blocked by missing rewrite schemdraw preview state machine: the current page has no "
        "editable source snapshot flow, stale preview handling, or latest-only render application."
    ),
    strict=False,
)
def test_rewrite_schemdraw_latest_only_and_blocking_validation_flow(
    page: Page,
    frontend_base_url: str,
) -> None:
    page.goto(f"{frontend_base_url}/circuit-schemdraw?definitionId=18", wait_until="networkidle")

    expect(page.locator(".cm-content").first).to_be_visible(timeout=5_000)
    expect(page.get_by_text("stale preview", exact=False)).to_be_visible(timeout=5_000)
    expect(page.get_by_text("blocking", exact=False)).to_be_visible(timeout=5_000)


@pytest.mark.xfail(
    reason=(
        "Blocked by rewrite proxy / redirect configuration: Direct /api/backend/* calls "
        "rely on Next.js rewrites which are not currently verified in this harness "
        "and are reported to return 404 in certain dev environments."
    ),
    strict=False,
)
def test_rewrite_proxy_backend_reachability_flow(
    page: Page,
    frontend_base_url: str,
) -> None:
    # This test provides evidence of the blocked proxy path.
    # In a real scenario (no mock), this would check if the rewrite to the backend works.
    page.goto(f"{frontend_base_url}/api/backend/session")
    # If the proxy is broken, we expect a 404 or a redirect that doesn't reach the backend.
    expect(page.get_by_text("404")).to_be_visible(timeout=5_000)
