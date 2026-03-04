"""Playwright E2E tests for Characterization workflows."""

from __future__ import annotations

import os
import re
import signal
import subprocess
import time
import uuid
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import numpy as np
import pytest
from playwright.sync_api import Page, expect, sync_playwright

from core.analysis.application.analysis.physics.admittance import calculate_y11_imaginary
from core.shared.persistence import DataRecord, DatasetRecord, get_unit_of_work

_RUN_PLAYWRIGHT_E2E = os.getenv("RUN_PLAYWRIGHT_CHARACTERIZATION_E2E") == "1"

pytestmark = pytest.mark.skipif(
    not _RUN_PLAYWRIGHT_E2E,
    reason=(
        "Set RUN_PLAYWRIGHT_CHARACTERIZATION_E2E=1 to run Playwright E2E tests "
        "for Characterization."
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


def _seed_characterization_dataset(
    dataset_name: str,
    *,
    dataset_profile: dict[str, object],
    include_y11: bool,
    include_s21: bool,
) -> None:
    freq_ghz = np.linspace(4.0, 8.0, 201)
    l_jun_nh = np.linspace(0.8, 2.8, 9)
    values_matrix = [
        [
            float(
                calculate_y11_imaginary(
                    float(l_value),
                    float(freq_value),
                    Ls1_nH=0.02,
                    Ls2_nH=0.03,
                    C_pF=1.0,
                )
            )
            for l_value in l_jun_nh
        ]
        for freq_value in freq_ghz
    ]

    with get_unit_of_work() as uow:
        existing = uow.datasets.get_by_name(dataset_name)
        if existing is not None:
            uow.datasets.delete(existing)
            uow.commit()

        dataset = DatasetRecord(
            name=dataset_name,
            source_meta={"dataset_profile": dataset_profile},
            parameters={},
        )
        uow.datasets.add(dataset)
        uow.flush()
        if dataset.id is None:
            raise ValueError("Failed to allocate dataset id for Characterization E2E.")

        common_axes = [
            {"name": "Freq", "unit": "GHz", "values": [float(x) for x in freq_ghz]},
            {"name": "L_jun", "unit": "nH", "values": [float(x) for x in l_jun_nh]},
        ]
        if include_y11:
            uow.data_records.add(
                DataRecord(
                    dataset_id=int(dataset.id),
                    data_type="y_parameters",
                    parameter="Y11",
                    representation="imaginary",
                    axes=common_axes,
                    values=values_matrix,
                )
            )
            uow.data_records.add(
                DataRecord(
                    dataset_id=int(dataset.id),
                    data_type="y_parameters",
                    parameter="Y11 [om=(1,), im=(0,)]",
                    representation="imaginary",
                    axes=common_axes,
                    values=values_matrix,
                )
            )

        if include_s21:
            uow.data_records.add(
                DataRecord(
                    dataset_id=int(dataset.id),
                    data_type="s_parameters",
                    parameter="S21",
                    representation="real",
                    axes=[
                        {
                            "name": "Freq",
                            "unit": "GHz",
                            "values": [float(x) for x in freq_ghz],
                        }
                    ],
                    values=[float(v[0]) for v in values_matrix],
                )
            )
        uow.commit()


@pytest.fixture(scope="session")
def seeded_dataset_names() -> dict[str, str]:
    suffix = uuid.uuid4().hex[:8]
    return {
        "squid": f"E2E-Characterization-SQUID-{suffix}",
        "single_junction": f"E2E-Characterization-SJ-{suffix}",
        "traveling_wave": f"E2E-Characterization-TW-{suffix}",
    }


@pytest.fixture(scope="session", autouse=True)
def seed_characterization_data(seeded_dataset_names: dict[str, str]) -> None:
    _seed_characterization_dataset(
        seeded_dataset_names["squid"],
        dataset_profile={
            "schema_version": "1.0",
            "device_type": "squid",
            "capabilities": [
                "y_parameter_characterization",
                "y11_response_fitting",
                "squid_characterization",
            ],
            "source": "manual_override",
        },
        include_y11=True,
        include_s21=False,
    )
    _seed_characterization_dataset(
        seeded_dataset_names["single_junction"],
        dataset_profile={
            "schema_version": "1.0",
            "device_type": "single_junction",
            "capabilities": [
                "y_parameter_characterization",
                "y11_response_fitting",
            ],
            "source": "manual_override",
        },
        include_y11=True,
        include_s21=False,
    )
    _seed_characterization_dataset(
        seeded_dataset_names["traveling_wave"],
        dataset_profile={
            "schema_version": "1.0",
            "device_type": "traveling_wave",
            "capabilities": [
                "s_parameter_characterization",
                "traveling_wave_gain",
            ],
            "source": "manual_override",
        },
        include_y11=True,
        include_s21=True,
    )
    yield
    with get_unit_of_work() as uow:
        for dataset_name in seeded_dataset_names.values():
            existing = uow.datasets.get_by_name(dataset_name)
            if existing is None:
                continue
            uow.datasets.delete(existing)
            uow.commit()


@pytest.fixture(scope="session")
def app_base_url(tmp_path_factory: pytest.TempPathFactory) -> str:
    port = int(os.getenv("PLAYWRIGHT_CHARACTERIZATION_APP_PORT", "8094"))
    base_url = f"http://127.0.0.1:{port}"

    log_dir = tmp_path_factory.mktemp("playwright_characterization_app")
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
        _wait_for_server(f"{base_url}/characterization")
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
def page(app_base_url: str) -> Page:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1400})
        page = context.new_page()
        page.goto(f"{app_base_url}/characterization", wait_until="networkidle")
        yield page
        context.close()
        browser.close()


def _select_active_dataset(page: Page, dataset_name: str) -> None:
    active_selector = page.get_by_role("combobox", name="Active Datasets")
    if active_selector.count() == 0:
        active_selector = page.get_by_role("combobox").first
    expect(active_selector).to_be_visible(timeout=15000)
    active_selector.click()
    page.get_by_role("option", name=dataset_name, exact=True).click()
    page.keyboard.press("Escape")


def _select_option(page: Page, label: str, option_text: str, index: int = 0) -> None:
    select = page.get_by_role("combobox", name=label).nth(index)
    expect(select).to_be_visible(timeout=15000)
    select.click()
    page.get_by_role("option", name=re.compile(rf"^{re.escape(option_text)}")).first.click()


def _expect_analysis_status(page: Page, analysis_label: str, status: str) -> None:
    _select_option(page, "Analysis", analysis_label)
    expect(page.get_by_text(f"Status: {status}", exact=True)).to_be_visible(timeout=30000)


def test_characterization_runs_squid_and_y11_and_renders_results(
    page: Page,
    seeded_dataset_names: dict[str, str],
) -> None:
    _select_active_dataset(page, seeded_dataset_names["squid"])
    expect(page.get_by_text("Source Scope")).to_be_visible(timeout=30000)
    _expect_analysis_status(page, "SQUID Fitting", "Recommended")
    _expect_analysis_status(page, "Y11 Response Fit", "Recommended")

    _select_option(page, "Analysis", "SQUID Fitting")
    run_button = page.get_by_role("button", name="Run Selected Analysis")
    expect(run_button).to_be_enabled(timeout=15000)
    run_button.click()
    expect(page.get_by_text("SQUID Fitting completed.")).to_be_visible(timeout=60000)

    _select_option(page, "Analysis", "Y11 Response Fit")
    expect(run_button).to_be_enabled(timeout=15000)
    run_button.click()
    expect(page.get_by_text("Y11 Response Fit completed.")).to_be_visible(timeout=60000)

    y11_tab_label = page.get_by_text("Y11 Response Fit", exact=True).last
    expect(y11_tab_label).to_be_visible(timeout=30000)
    y11_tab_label.click()
    result_trace_mode = page.get_by_role("combobox", name="Trace Mode Filter").last
    expect(result_trace_mode).to_be_visible()
    result_trace_mode.click()
    expect(page.get_by_role("option", name="Unknown", exact=True)).to_have_count(0)
    page.keyboard.press("Escape")

    category = page.get_by_role("combobox", name="Category").last
    expect(category).to_be_visible()
    trace_box = result_trace_mode.bounding_box()
    category_box = category.bounding_box()
    assert trace_box is not None
    assert category_box is not None
    assert abs(float(trace_box["y"]) - float(category_box["y"])) < 48

    expect(page.get_by_text("Fit Parameters")).to_be_visible(timeout=30000)


def test_characterization_capability_gating_shows_unavailable_reasons(
    page: Page,
    seeded_dataset_names: dict[str, str],
) -> None:
    _select_active_dataset(page, seeded_dataset_names["single_junction"])
    expect(page.get_by_text("Source Scope")).to_be_visible(timeout=30000)
    _expect_analysis_status(page, "SQUID Fitting", "Unavailable")
    expect(page.get_by_text("Missing capability: SQUID Characterization").first).to_be_visible(
        timeout=30000
    )

    _select_active_dataset(page, seeded_dataset_names["traveling_wave"])
    expect(page.get_by_text("Source Scope")).to_be_visible(timeout=30000)
    _select_option(page, "Analysis", "S21 Resonance Fit")
    expect(page.get_by_text(re.compile(r"^Status: "))).to_be_visible(timeout=30000)
