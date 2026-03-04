"""Structural tests for dataset metadata UI entry points."""

from __future__ import annotations

import inspect

from app.pages import dashboard, raw_data, simulation


def test_dashboard_page_exposes_dataset_metadata_editor_controls() -> None:
    source = inspect.getsource(dashboard)

    assert 'ui.label("Dataset Metadata")' in source
    assert 'label="Device Type"' in source
    assert 'label="Capabilities"' in source
    assert '"Auto Suggest"' in source
    assert '"Save Metadata"' in source


def test_raw_data_page_hides_dataset_metadata_editor_controls() -> None:
    source = inspect.getsource(raw_data)

    assert 'ui.label("Dataset Metadata Summary")' in source
    assert '"Auto Suggest"' not in source
    assert '"Save Metadata"' not in source
    assert 'label="Device Type"' not in source
    assert 'label="Capabilities"' not in source


def test_simulation_page_hides_dataset_metadata_editor_controls() -> None:
    source = inspect.getsource(simulation)

    assert 'ui.label("Dataset Metadata Summary")' in source
    assert 'label="Target Dataset"' in source
    assert '"Auto Suggest"' not in source
    assert '"Save Metadata"' not in source
    assert 'label="Device Type"' not in source
    assert 'label="Capabilities"' not in source
