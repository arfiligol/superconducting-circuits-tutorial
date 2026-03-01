"""Tests for schema editor formatting persistence helpers."""

from app.pages.schema_editor import _editor_text_from_record, _stored_schema_text_from_editor
from core.simulation.domain.circuit import (
    format_circuit_definition,
    migrate_legacy_circuit_definition,
    parse_circuit_definition_source,
)


def test_stored_schema_text_from_editor_preserves_exact_editor_content() -> None:
    editor_text = """{
    "schema_version": "0.1",
    "name": "SmokeStableSeriesLC",
    "parameters": {
        "R_port": {"default": 50.0, "unit": "Ohm"},
    },
}"""

    assert _stored_schema_text_from_editor(editor_text) == editor_text


def test_editor_text_from_record_preserves_non_legacy_saved_format() -> None:
    saved_text = """{
    "schema_version": "0.1",
    "name": "SmokeStableSeriesLC",
    "parameters": {
        "R_port": {"default": 50.0, "unit": "Ohm"},
    },
    "ports": [],
    "instances": [],
}"""

    editor_text, migrated = _editor_text_from_record(saved_text)

    assert migrated is False
    assert editor_text == saved_text


def test_editor_text_from_record_reformats_legacy_payloads() -> None:
    legacy_payload = {
        "name": "Legacy",
        "parameters": {"R_port": {"default": 50.0, "unit": "Ohm"}},
        "topology": [("P1", "1", "0", 1), ("R1", "1", "0", "R_port")],
    }

    migrated_text, migrated = _editor_text_from_record(str(legacy_payload))
    migrated_payload = migrate_legacy_circuit_definition(legacy_payload)
    migrated_circuit, _ = parse_circuit_definition_source(migrated_payload)

    assert migrated is True
    assert migrated_text == format_circuit_definition(migrated_circuit)
