"""Playwright E2E smoke tests for JosephsonCircuits-style simulation examples."""

from __future__ import annotations

import os
import re
import signal
import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import pytest
from playwright.sync_api import Page, expect, sync_playwright

from core.shared.persistence import get_unit_of_work
from core.shared.persistence.models import CircuitRecord

_RUN_PLAYWRIGHT_E2E = os.getenv("RUN_PLAYWRIGHT_JOSEPHSON_E2E") == "1"

pytestmark = pytest.mark.skipif(
    not _RUN_PLAYWRIGHT_E2E,
    reason=(
        "Set RUN_PLAYWRIGHT_JOSEPHSON_E2E=1 to run Playwright E2E smoke tests "
        "for JosephsonCircuits-style examples."
    ),
)


@dataclass(frozen=True)
class ExampleCase:
    """One simulation flow to execute through the browser UI."""

    slug: str
    schema_name: str
    definition: str
    start_ghz: float
    stop_ghz: float
    points: int
    n_mod: int
    n_pump: int
    sources: tuple[tuple[float, int, float], ...]


def _stable_series_lc_definition() -> str:
    return str(
        {
            "name": "E2E Stable Series LC",
            "components": [
                {"name": "R50", "default": 50.0, "unit": "Ohm"},
                {"name": "L1", "default": 10.0, "unit": "nH"},
                {"name": "C1", "default": 1.0, "unit": "pF"},
            ],
            "topology": [
                ("P1", "1", "0", 1),
                ("R50", "1", "0", "R50"),
                ("L1", "1", "2", "L1"),
                ("C1", "2", "0", "C1"),
            ],
        }
    )


def _jpa_definition() -> str:
    return str(
        {
            "name": "E2E JPA Core",
            "components": [
                {"name": "R1", "default": 50.0, "unit": "Ohm"},
                {"name": "Cc", "default": 100.0, "unit": "fF"},
                {"name": "Lj", "default": 1000.0, "unit": "pH"},
                {"name": "Cj", "default": 1000.0, "unit": "fF"},
            ],
            "topology": [
                ("P1", "1", "0", 1),
                ("R1", "1", "0", "R1"),
                ("C1", "1", "2", "Cc"),
                ("Lj1", "2", "0", "Lj"),
                ("C2", "2", "0", "Cj"),
            ],
        }
    )


def _two_port_compensation_definition() -> str:
    return str(
        {
            "name": "E2E Two Port Compensation",
            "components": [
                {"name": "R50", "default": 50.0, "unit": "Ohm"},
                {"name": "R100", "default": 100.0, "unit": "Ohm"},
                {"name": "C12", "default": 200.0, "unit": "fF"},
            ],
            "topology": [
                ("P1", "1", "0", 1),
                ("P2", "2", "0", 2),
                ("R1", "1", "0", "R50"),
                ("R2", "2", "0", "R100"),
                ("C1", "1", "2", "C12"),
            ],
        }
    )


def _three_port_basis_definition() -> str:
    return str(
        {
            "name": "E2E Three Port Basis Labels",
            "components": [
                {"name": "R50", "default": 50.0, "unit": "Ohm"},
                {"name": "C12", "default": 120.0, "unit": "fF"},
                {"name": "C23", "default": 80.0, "unit": "fF"},
                {"name": "Cg1", "default": 30.0, "unit": "fF"},
                {"name": "Cg2", "default": 35.0, "unit": "fF"},
            ],
            "topology": [
                ("P1", "1", "0", 1),
                ("P2", "2", "0", 2),
                ("P3", "3", "0", 3),
                ("R1", "1", "0", "R50"),
                ("R2", "2", "0", "R50"),
                ("R3", "3", "0", "R50"),
                ("C12", "1", "2", "C12"),
                ("C23", "2", "3", "C23"),
                ("Cg1", "1", "0", "Cg1"),
                ("Cg2", "2", "0", "Cg2"),
            ],
        }
    )


@pytest.fixture(scope="session")
def example_cases() -> tuple[ExampleCase, ...]:
    """Representative example categories from JosephsonCircuits README usage."""
    suffix = uuid.uuid4().hex[:8]

    single_ip = 0.00565e-6
    double_ip = single_ip * 1.7

    return (
        ExampleCase(
            slug="linear_series_lc",
            schema_name=f"E2E-{suffix}-LinearSeriesLC",
            definition=_stable_series_lc_definition(),
            start_ghz=1.0,
            stop_ghz=5.0,
            points=201,
            n_mod=8,
            n_pump=8,
            sources=((5.0, 1, 0.0),),
        ),
        ExampleCase(
            slug="jpa_single_pump",
            schema_name=f"E2E-{suffix}-JPASinglePump",
            definition=_jpa_definition(),
            start_ghz=4.5,
            stop_ghz=5.0,
            points=201,
            n_mod=8,
            n_pump=16,
            sources=((4.75001, 1, single_ip),),
        ),
        ExampleCase(
            slug="jpa_double_pump",
            schema_name=f"E2E-{suffix}-JPADoublePump",
            definition=_jpa_definition(),
            start_ghz=4.5,
            stop_ghz=5.0,
            points=101,
            n_mod=4,
            n_pump=4,
            sources=((4.65001, 1, double_ip), (4.85001, 1, double_ip)),
        ),
        ExampleCase(
            slug="two_port_compensation",
            schema_name=f"E2E-{suffix}-TwoPortCompensation",
            definition=_two_port_compensation_definition(),
            start_ghz=4.8,
            stop_ghz=5.2,
            points=201,
            n_mod=6,
            n_pump=6,
            sources=((5.0, 1, 0.0),),
        ),
        ExampleCase(
            slug="three_port_basis_labels",
            schema_name=f"E2E-{suffix}-ThreePortBasisLabels",
            definition=_three_port_basis_definition(),
            start_ghz=4.8,
            stop_ghz=5.2,
            points=121,
            n_mod=4,
            n_pump=4,
            sources=((5.0, 1, 0.0),),
        ),
    )


@pytest.fixture(scope="session", autouse=True)
def seed_example_schemas(example_cases: tuple[ExampleCase, ...]) -> None:
    """Insert/update required schemas so UI tests do not depend on editor interactions."""
    created_schema_names: list[str] = []
    with get_unit_of_work() as uow:
        for case in example_cases:
            existing = uow.circuits.get_by_name(case.schema_name)
            if existing is None:
                uow.circuits.add(
                    CircuitRecord(name=case.schema_name, definition_json=case.definition)
                )
                created_schema_names.append(case.schema_name)
            else:
                existing.definition_json = case.definition
                uow.circuits.update(existing)
        uow.commit()
    yield
    with get_unit_of_work() as uow:
        for schema_name in created_schema_names:
            existing = uow.circuits.get_by_name(schema_name)
            if existing is not None and existing.id is not None:
                uow.circuits.delete(existing.id)
        uow.commit()


def _wait_for_server(url: str, timeout_seconds: float = 60.0) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=2.0):
                return
        except URLError:
            time.sleep(0.5)
    raise TimeoutError(f"Timed out waiting for app server at {url}")


@pytest.fixture(scope="session")
def app_base_url(tmp_path_factory: pytest.TempPathFactory) -> str:
    """Start the NiceGUI app once for all Playwright example tests."""
    port = int(os.getenv("PLAYWRIGHT_SC_APP_PORT", "8093"))
    base_url = f"http://127.0.0.1:{port}"

    log_dir = tmp_path_factory.mktemp("playwright_sc_app")
    log_path = log_dir / "sc_app.log"
    log_file = log_path.open("w", encoding="utf-8")

    env = os.environ.copy()
    env["SC_APP_PORT"] = str(port)
    env["NICEGUI_SCREEN_TEST_PORT"] = str(port)
    process = subprocess.Popen(
        ["uv", "run", "sc-app"],
        cwd=Path(__file__).resolve().parents[3],
        env=env,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    try:
        _wait_for_server(f"{base_url}/simulation")
        yield base_url
    except Exception as err:
        log_file.flush()
        log_file.close()
        details = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
        raise RuntimeError(f"Failed to start app server. Log:\n{details}") from err
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
def page(app_base_url: str) -> Page:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1400})
        page = context.new_page()
        page.goto(f"{app_base_url}/simulation", wait_until="networkidle")
        yield page
        context.close()
        browser.close()


def _set_spinbutton_value(page: Page, label: str, value: float | int | str, index: int = 0) -> None:
    target = page.get_by_role("spinbutton", name=label).nth(index)
    expect(target).to_be_visible(timeout=15000)
    target.click()
    target.fill(str(value))
    target.press("Enter")


def _choose_schema(page: Page, schema_name: str) -> None:
    schema_select = page.get_by_role("combobox").nth(1)
    expect(schema_select).to_be_visible(timeout=15000)
    schema_select.click()
    page.get_by_role("option", name=schema_name, exact=True).click()


def _configure_sources(page: Page, sources: tuple[tuple[float, int, float], ...]) -> None:
    existing_count = page.get_by_text(re.compile(r"^Source \d+$")).count()
    while existing_count < len(sources):
        page.get_by_role("button", name="Add Source").click()
        existing_count += 1

    for idx, (pump_freq_ghz, port, current_amp) in enumerate(sources):
        _set_spinbutton_value(page, "Pump Freq (GHz)", pump_freq_ghz, index=idx)
        _set_spinbutton_value(page, "Source Port", port, index=idx)
        _set_spinbutton_value(page, "Source Current Ip (A)", current_amp, index=idx)


def _run_and_expect_success(page: Page, *, allow_long_running: bool = False) -> bool:
    page.get_by_role("button", name="Run Simulation").click()
    success_banner = page.get_by_text("Simulation completed successfully")

    if allow_long_running:
        try:
            expect(success_banner).to_be_visible(timeout=20000)
            expect(page.get_by_text("Numerical solver error", exact=False)).to_have_count(0)
            return True
        except AssertionError:
            try:
                expect(page.get_by_text("Submitting job to Julia worker...")).to_be_visible(
                    timeout=15000
                )
            except AssertionError:
                expect(
                    page.get_by_text("Julia worker still running...", exact=False)
                ).to_be_visible(timeout=20000)
            expect(page.get_by_text("Numerical solver error", exact=False)).to_have_count(0)
            return False

    expect(success_banner).to_be_visible(timeout=180000)
    expect(page.get_by_text("Numerical solver error", exact=False)).to_have_count(0)
    return True


def _run_post_processing_and_expect_output(page: Page) -> None:
    ready_text = "Pipeline output ready. Post Processing Result View is updated."
    post_results_card = _card_by_testid(
        page,
        "post-processing-results-card",
        fallback_text="Post Processing Results",
    )
    post_input_card = _card_by_testid(
        page,
        "post-processing-input-card",
        fallback_text="Run Post Processing",
    )
    run_button = _locator_by_testid(
        page,
        "post-processing-run-button",
        fallback=page.get_by_role("button", name="Run Post Processing"),
    )
    save_button = _locator_by_testid(
        page,
        "post-result-view-save-button",
        fallback=page.get_by_role("button", name="Save Post-Processed Results"),
    )
    post_setup_name = f"E2E Post Setup {uuid.uuid4().hex[:6]}"

    expect(run_button).to_be_visible(timeout=30000)
    expect(save_button).to_be_visible(timeout=30000)
    expect(save_button).to_be_disabled()
    expect(post_input_card.get_by_role("button", name="Save Post-Processed Results")).to_have_count(
        0
    )
    expect(
        post_results_card.get_by_role("button", name="Save Post-Processed Results")
    ).to_have_count(1)

    post_setup_select = post_input_card.get_by_role("combobox", name="Post-Processing Setup")
    expect(post_setup_select).to_be_visible(timeout=30000)
    post_input_card.get_by_role("button", name="Save Setup").click()
    save_setup_dialog = page.get_by_text("Save Post-Processing Setup")
    expect(save_setup_dialog).to_be_visible(timeout=30000)
    setup_name_input = page.get_by_role("textbox", name="Setup Name")
    setup_name_input.click()
    setup_name_input.fill(post_setup_name)
    page.get_by_role("button", name="Save").last.click()
    expect(save_setup_dialog).to_have_count(0, timeout=30000)

    step_type_select = post_input_card.get_by_role("combobox", name="Step Type")
    step_type_select.click()
    page.get_by_role("option", name="Kron Reduction").click()
    post_input_card.get_by_role("button", name="Add Step").click()

    keep_basis_text = page.get_by_text("Keep Basis Labels")
    select_all_button = page.get_by_role("button", name="Select All").first
    clear_button = page.get_by_role("button", name="Clear").first
    expect(keep_basis_text).to_be_visible(timeout=30000)
    expect(select_all_button).to_be_visible(timeout=30000)
    expect(clear_button).to_be_visible(timeout=30000)
    select_all_button.click()
    clear_button.click()
    select_all_button.click()

    run_button.click()
    expect(page.get_by_text(ready_text)).to_be_visible(timeout=30000)
    expect(save_button).to_be_enabled(timeout=30000)

    post_results_card.get_by_role("tab", name="Impedance (Z)").click()
    metric_select = post_results_card.get_by_role("combobox", name="Metric")
    metric_select.click()
    metric_select.press("ArrowDown")
    metric_select.press("Enter")

    post_results_card.get_by_role("button", name="Add Trace").click()
    expect(post_results_card.locator(".js-plotly-plot")).to_have_count(1, timeout=30000)


def _select_card_option(
    page: Page,
    card,
    label: str,
    option_text: str,
    index: int = 0,
) -> None:  # type: ignore[no-untyped-def]
    select = card.get_by_role("combobox", name=label).nth(index)
    expect(select).to_be_visible(timeout=15000)
    controls_id = select.get_attribute("aria-controls")
    select.click()
    desired = re.sub(r"\s+", "", option_text).lower()
    page.keyboard.type(option_text)
    page.keyboard.press("Enter")
    current_value = (select.input_value() or "").strip()
    current_normalized = re.sub(r"\s+", "", current_value).lower()
    if current_normalized == desired or desired in current_normalized:
        return

    select.click()
    option_scope = page.locator(f"#{controls_id}") if controls_id else page.locator("body")
    options = option_scope.get_by_role("option")
    for idx_option in range(options.count()):
        option_text_value = options.nth(idx_option).inner_text()
        normalized = re.sub(r"\s+", "", option_text_value).lower()
        if normalized == desired or desired in normalized:
            options.nth(idx_option).click()
            return

    option_pattern = re.compile(re.escape(option_text))
    options.filter(has_text=option_pattern).first.click()


def _locator_by_testid(page: Page, testid: str, *, fallback):  # type: ignore[no-untyped-def]
    candidate = page.locator(f"[data-testid='{testid}']")
    if candidate.count() > 0:
        return candidate.first
    return fallback


def _card_by_testid(page: Page, testid: str, *, fallback_text: str):  # type: ignore[no-untyped-def]
    return _locator_by_testid(
        page,
        testid,
        fallback=page.locator(".q-card").filter(has_text=fallback_text).first,
    )


def _post_plot_title_and_legend(post_results_card) -> tuple[str, list[str]]:  # type: ignore[no-untyped-def]
    plot = post_results_card.locator(".js-plotly-plot").first
    expect(plot).to_be_visible(timeout=30000)
    payload = plot.evaluate(
        "el => ({ title: String(el.layout?.title?.text || ''), "
        "legend: (el.data || []).map(trace => String(trace.name || '')) })"
    )
    title = str(payload.get("title", ""))
    legend = [str(item) for item in payload.get("legend", [])]
    return (title, legend)


def _plot_y_axis_title(card) -> str:  # type: ignore[no-untyped-def]
    plot = card.locator(".js-plotly-plot").first
    expect(plot).to_be_visible(timeout=30000)
    value = plot.evaluate("el => String(el.layout?.yaxis?.title?.text || '')")
    return str(value)


def _expect_plot_y_axis_title(card, expected: str, *, timeout_seconds: float = 12.0) -> None:  # type: ignore[no-untyped-def]
    deadline = time.time() + timeout_seconds
    latest = ""
    while time.time() < deadline:
        latest = _plot_y_axis_title(card)
        if latest == expected:
            return
        time.sleep(0.2)
    raise AssertionError(f"Expected y-axis title {expected!r}, got {latest!r}")


def _nudge_combobox_option(
    page: Page,
    card,
    label: str,
    *,
    direction: str,
    steps: int,
    index: int = 0,
) -> None:  # type: ignore[no-untyped-def]
    select = card.get_by_role("combobox", name=label).nth(index)
    expect(select).to_be_visible(timeout=15000)
    select.click()
    key = "ArrowUp" if direction == "up" else "ArrowDown"
    for _ in range(max(1, steps)):
        page.keyboard.press(key)
    page.keyboard.press("Enter")


def _configure_raw_result_to_y22_real(page: Page) -> None:
    raw_results_card = _card_by_testid(
        page,
        "simulation-results-card",
        fallback_text="Raw Simulation Results",
    )
    raw_results_card.get_by_role("tab", name="Admittance (Y)").click()
    output_port_select = raw_results_card.get_by_role("combobox", name="Output Port")
    output_port_select.click()
    output_port_select.press("ArrowDown")
    output_port_select.press("Enter")
    input_port_select = raw_results_card.get_by_role("combobox", name="Input Port")
    input_port_select.click()
    input_port_select.press("ArrowDown")
    input_port_select.press("Enter")
    expect(raw_results_card.locator(".js-plotly-plot")).to_have_count(1, timeout=30000)


def _read_first_plot_y_value(page: Page) -> float:
    raw_results_card = _card_by_testid(
        page,
        "simulation-results-card",
        fallback_text="Raw Simulation Results",
    )
    plot = raw_results_card.locator(".js-plotly-plot").first
    expect(plot).to_be_visible(timeout=30000)
    value = plot.evaluate("el => el.data[0].y[0]")
    return float(value)


def _configure_termination_mode_auto(page: Page) -> None:
    term_card = _card_by_testid(
        page,
        "termination-compensation-card",
        fallback_text="Port Termination Compensation (Optional)",
    )
    expect(term_card).to_be_visible(timeout=30000)
    enable_switch = term_card.get_by_role("switch", name="Enable")
    if enable_switch.count() == 0:
        enable_switch = term_card.get_by_role("checkbox", name="Enable")
    if enable_switch.count() > 0:
        if not enable_switch.first.is_checked():
            enable_switch.first.click()
    else:
        toggle = term_card.locator(".q-toggle").first
        expect(toggle).to_be_visible(timeout=30000)
        classes = str(toggle.get_attribute("class") or "")
        if "q-toggle--truthy" not in classes:
            toggle.click()
    mode_select = term_card.get_by_role("combobox", name="Mode")
    mode_select.click()
    page.get_by_role("option", name="Auto (Schema infer)").click()
    expect(term_card.get_by_text("mode=auto", exact=False).first).to_be_visible(timeout=30000)
    expect(term_card.get_by_text("ports=[1, 2]", exact=False).first).to_be_visible(timeout=30000)


def _configure_termination_mode_manual_custom(page: Page) -> None:
    term_card = _card_by_testid(
        page,
        "termination-compensation-card",
        fallback_text="Port Termination Compensation (Optional)",
    )
    mode_select = term_card.get_by_role("combobox", name="Mode")
    mode_select.click()
    page.get_by_role("option", name="Manual").click()
    port1_resistance = term_card.get_by_role("spinbutton", name=re.compile(r"Port 1 .*Manual R"))
    expect(port1_resistance).to_be_visible(timeout=30000)
    port1_resistance.click()
    port1_resistance.fill("75")
    port1_resistance.press("Enter")
    expect(term_card.get_by_text("mode=manual", exact=False).first).to_be_visible(timeout=30000)
    expect(term_card.get_by_text("p1=75 Ohm (manual)", exact=False).first).to_be_visible(
        timeout=30000
    )


@pytest.mark.parametrize(
    "example_case",
    ["linear_series_lc", "jpa_single_pump", "jpa_double_pump"],
)
def test_josephson_example_runs_in_ui(
    page: Page,
    example_cases: tuple[ExampleCase, ...],
    example_case: str,
) -> None:
    """Run each example category through the Simulation UI and assert successful completion."""
    case = next(c for c in example_cases if c.slug == example_case)

    _choose_schema(page, case.schema_name)

    _set_spinbutton_value(page, "Start Freq (GHz)", case.start_ghz)
    _set_spinbutton_value(page, "Stop Freq (GHz)", case.stop_ghz)
    _set_spinbutton_value(page, "Points", case.points)
    _set_spinbutton_value(page, "Nmodulation Harmonics", case.n_mod)
    _set_spinbutton_value(page, "Npump Harmonics", case.n_pump)
    _configure_sources(page, case.sources)

    simulation_completed = _run_and_expect_success(
        page,
        allow_long_running=(case.slug == "jpa_double_pump"),
    )
    if simulation_completed:
        _run_post_processing_and_expect_output(page)


def test_port_termination_compensation_modes_in_ui(
    page: Page,
    example_cases: tuple[ExampleCase, ...],
    tmp_path: Path,
) -> None:
    case = next(c for c in example_cases if c.slug == "two_port_compensation")

    _choose_schema(page, case.schema_name)
    _set_spinbutton_value(page, "Start Freq (GHz)", case.start_ghz)
    _set_spinbutton_value(page, "Stop Freq (GHz)", case.stop_ghz)
    _set_spinbutton_value(page, "Points", case.points)
    _set_spinbutton_value(page, "Nmodulation Harmonics", case.n_mod)
    _set_spinbutton_value(page, "Npump Harmonics", case.n_pump)
    _configure_sources(page, case.sources)

    assert _run_and_expect_success(page) is True
    raw_results_card = _card_by_testid(
        page,
        "simulation-results-card",
        fallback_text="Raw Simulation Results",
    )
    expect(raw_results_card.locator(".js-plotly-plot")).to_have_count(1, timeout=30000)
    baseline_raw_s = _read_first_plot_y_value(page)
    baseline_log_count = page.get_by_text(
        "Simulation completed successfully",
        exact=False,
    ).count()
    page.screenshot(path=str(tmp_path / "termination_case_baseline.png"), full_page=True)

    _configure_termination_mode_auto(page)
    auto_raw_s = _read_first_plot_y_value(page)
    assert auto_raw_s == pytest.approx(baseline_raw_s, abs=1e-9)
    assert (
        page.get_by_text("Simulation completed successfully", exact=False).count()
        == baseline_log_count
    )
    expect(
        page.get_by_text("Termination compensation updated without Julia rerun", exact=False)
    ).to_be_visible(timeout=30000)
    page.screenshot(path=str(tmp_path / "termination_case_auto.png"), full_page=True)

    raw_results_card.get_by_role("tab", name="Admittance (Y)").click()
    _select_card_option(page, raw_results_card, "Output Port", "1")
    _select_card_option(page, raw_results_card, "Input Port", "1")
    _select_card_option(page, raw_results_card, "Y Source", "Raw Y")
    y_source_select = raw_results_card.get_by_role("combobox", name="Y Source")
    assert y_source_select.input_value() == "Raw Y"
    y_source_select.click()
    y_source_select.press("ArrowDown")
    y_source_select.press("Enter")
    assert y_source_select.input_value() in {"Raw Y", "PTC Y"}

    _configure_termination_mode_manual_custom(page)
    assert y_source_select.input_value() in {"Raw Y", "PTC Y"}

    raw_results_card.get_by_role("tab", name="Impedance (Z)").click()
    _select_card_option(page, raw_results_card, "Output Port", "1")
    _select_card_option(page, raw_results_card, "Input Port", "1")
    _select_card_option(page, raw_results_card, "Z Source", "Raw Z")
    z_source_select = raw_results_card.get_by_role("combobox", name="Z Source")
    assert z_source_select.input_value() == "Raw Z"
    z_source_select.click()
    z_source_select.press("ArrowDown")
    z_source_select.press("Enter")
    assert z_source_select.input_value() in {"Raw Z", "PTC Z"}
    assert (
        page.get_by_text("Simulation completed successfully", exact=False).count()
        == baseline_log_count
    )
    page.screenshot(path=str(tmp_path / "termination_case_manual.png"), full_page=True)

    _run_post_processing_and_expect_output(page)
    post_results_card = _card_by_testid(
        page,
        "post-processing-results-card",
        fallback_text="Post Processing Results",
    )
    expect(post_results_card.locator(".js-plotly-plot")).to_have_count(1, timeout=30000)
    page.screenshot(path=str(tmp_path / "termination_case_post_processing.png"), full_page=True)


def test_post_processing_hfss_comparable_status(
    page: Page,
    example_cases: tuple[ExampleCase, ...],
) -> None:
    case = next(c for c in example_cases if c.slug == "two_port_compensation")
    _choose_schema(page, case.schema_name)
    _set_spinbutton_value(page, "Start Freq (GHz)", case.start_ghz)
    _set_spinbutton_value(page, "Stop Freq (GHz)", case.stop_ghz)
    _set_spinbutton_value(page, "Points", case.points)
    _set_spinbutton_value(page, "Nmodulation Harmonics", case.n_mod)
    _set_spinbutton_value(page, "Npump Harmonics", case.n_pump)
    _configure_sources(page, case.sources)

    assert _run_and_expect_success(page) is True
    _configure_termination_mode_auto(page)

    post_input_card = _card_by_testid(
        page,
        "post-processing-input-card",
        fallback_text="Run Post Processing",
    )
    _select_card_option(page, post_input_card, "Input Y Source", "Raw Y")
    _locator_by_testid(
        page,
        "post-processing-run-button",
        fallback=post_input_card.get_by_role("button", name="Run Post Processing"),
    ).click()
    expect(page.get_by_text("HFSS Comparable: No", exact=False)).to_be_visible(timeout=30000)
    expect(
        page.get_by_text("Coordinate Transformation step is missing", exact=False).first
    ).to_be_visible(timeout=30000)

    input_source_select = post_input_card.get_by_role("combobox", name="Input Y Source")
    input_source_select.click()
    input_source_select.press("ArrowDown")
    input_source_select.press("Enter")
    assert input_source_select.input_value() in {"Raw Y", "PTC Y"}
    _select_card_option(page, post_input_card, "Step Type", "Coordinate Transformation")
    post_input_card.get_by_role("button", name="Add Step").click()
    expect(page.get_by_text("Step 1 · Coordinate Transformation", exact=False).first).to_be_visible(
        timeout=30000
    )


def test_post_processed_result_view_uses_trace_card_port_labels_for_matrix_names(
    page: Page,
    example_cases: tuple[ExampleCase, ...],
    tmp_path: Path,
) -> None:
    case = next(c for c in example_cases if c.slug == "three_port_basis_labels")

    _choose_schema(page, case.schema_name)
    _set_spinbutton_value(page, "Start Freq (GHz)", case.start_ghz)
    _set_spinbutton_value(page, "Stop Freq (GHz)", case.stop_ghz)
    _set_spinbutton_value(page, "Points", case.points)
    _set_spinbutton_value(page, "Nmodulation Harmonics", case.n_mod)
    _set_spinbutton_value(page, "Npump Harmonics", case.n_pump)
    _configure_sources(page, case.sources)
    assert _run_and_expect_success(page) is True

    post_input_card = _card_by_testid(
        page,
        "post-processing-input-card",
        fallback_text="Run Post Processing",
    )
    _select_card_option(page, post_input_card, "Step Type", "Coordinate Transformation")
    post_input_card.get_by_role("button", name="Add Step").click()

    _locator_by_testid(
        page,
        "post-processing-run-button",
        fallback=post_input_card.get_by_role("button", name="Run Post Processing"),
    ).click()
    post_results_card = _card_by_testid(
        page,
        "post-processing-results-card",
        fallback_text="Post Processing Results",
    )
    expect(post_results_card.locator(".js-plotly-plot")).to_have_count(1, timeout=60000)
    post_results_card.get_by_role("tab", name="Impedance (Z)").click()

    def _assert_name(expected_name: str, screenshot_suffix: str) -> None:
        deadline = time.time() + 12.0
        matched = False
        title = ""
        legend: list[str] = []
        while time.time() < deadline:
            title, legend = _post_plot_title_and_legend(post_results_card)
            if expected_name in title and expected_name in legend:
                matched = True
                break
            time.sleep(0.25)
        assert matched, (
            f"Expected {expected_name} in title+legend, got title={title!r}, legend={legend!r}"
        )
        page.screenshot(
            path=str(tmp_path / f"post_processed_matrix_name_{screenshot_suffix}.png"),
            full_page=True,
        )

    _nudge_combobox_option(
        page,
        post_results_card,
        "Output Port",
        direction="down",
        steps=1,
    )
    _nudge_combobox_option(
        page,
        post_results_card,
        "Input Port",
        direction="down",
        steps=1,
    )
    _assert_name("Z_dm_dm", "dm_to_dm")
    _nudge_combobox_option(
        page,
        post_results_card,
        "Input Port",
        direction="up",
        steps=1,
    )
    _assert_name("Z_dm_cm", "dm_to_cm")
    _nudge_combobox_option(
        page,
        post_results_card,
        "Input Port",
        direction="down",
        steps=2,
    )
    _assert_name("Z_dm_3", "dm_to_3")


def test_result_view_axis_titles_follow_y_z_family_switches(
    page: Page,
    example_cases: tuple[ExampleCase, ...],
) -> None:
    case = next(c for c in example_cases if c.slug == "three_port_basis_labels")
    _choose_schema(page, case.schema_name)
    _set_spinbutton_value(page, "Start Freq (GHz)", case.start_ghz)
    _set_spinbutton_value(page, "Stop Freq (GHz)", case.stop_ghz)
    _set_spinbutton_value(page, "Points", case.points)
    _set_spinbutton_value(page, "Nmodulation Harmonics", case.n_mod)
    _set_spinbutton_value(page, "Npump Harmonics", case.n_pump)
    _configure_sources(page, case.sources)
    assert _run_and_expect_success(page) is True

    raw_results_card = _card_by_testid(
        page,
        "simulation-results-card",
        fallback_text="Raw Simulation Results",
    )
    raw_results_card.get_by_role("tab", name="Admittance (Y)").click()
    _select_card_option(page, raw_results_card, "Metric", "Real")
    _expect_plot_y_axis_title(raw_results_card, "Real (S)")
    raw_results_card.get_by_role("tab", name="Impedance (Z)").click()
    _select_card_option(page, raw_results_card, "Metric", "Real")
    _expect_plot_y_axis_title(raw_results_card, "Real (Ohm)")
    raw_results_card.get_by_role("tab", name="Admittance (Y)").click()
    _select_card_option(page, raw_results_card, "Metric", "Real")
    _expect_plot_y_axis_title(raw_results_card, "Real (S)")

    post_input_card = _card_by_testid(
        page,
        "post-processing-input-card",
        fallback_text="Run Post Processing",
    )
    _select_card_option(page, post_input_card, "Step Type", "Coordinate Transformation")
    post_input_card.get_by_role("button", name="Add Step").click()
    _locator_by_testid(
        page,
        "post-processing-run-button",
        fallback=post_input_card.get_by_role("button", name="Run Post Processing"),
    ).click()

    post_results_card = _card_by_testid(
        page,
        "post-processing-results-card",
        fallback_text="Post Processing Results",
    )
    expect(post_results_card.locator(".js-plotly-plot")).to_have_count(1, timeout=60000)
    post_results_card.get_by_role("tab", name="Admittance (Y)").click()
    _select_card_option(page, post_results_card, "Metric", "Real")
    _expect_plot_y_axis_title(post_results_card, "Real (S)")
    post_results_card.get_by_role("tab", name="Impedance (Z)").click()
    _select_card_option(page, post_results_card, "Metric", "Real")
    _expect_plot_y_axis_title(post_results_card, "Real (Ohm)")
    post_results_card.get_by_role("tab", name="Admittance (Y)").click()
    _select_card_option(page, post_results_card, "Metric", "Real")
    _expect_plot_y_axis_title(post_results_card, "Real (S)")
