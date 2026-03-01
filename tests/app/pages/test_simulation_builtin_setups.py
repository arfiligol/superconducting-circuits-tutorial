"""Tests for built-in simulation setup seeds on the simulation page."""

import ast
import importlib.util
from pathlib import Path

from app.pages.simulation import (
    _builtin_saved_setups_for_schema,
    _extract_available_port_indices,
    _merge_saved_setups_with_builtin,
)
from core.simulation.domain.circuit import CircuitDefinition


def _load_seed_module():
    module_path = (
        Path(__file__).resolve().parents[3] / "tmp" / "seed_josephson_circuits_examples.py"
    )
    spec = importlib.util.spec_from_file_location("seed_josephson_circuits_examples", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_builtin_saved_setups_for_jpa_returns_official_example() -> None:
    setups = _builtin_saved_setups_for_schema(
        "JosephsonCircuits Examples: Josephson Parametric Amplifier (JPA)"
    )

    assert len(setups) == 1
    setup = setups[0]
    assert setup["name"] == "Official Example"
    assert setup["saved_at"] == "builtin"
    assert setup["payload"]["freq_range"]["start_ghz"] == 4.5
    assert setup["payload"]["freq_range"]["stop_ghz"] == 5.0
    assert setup["payload"]["harmonics"]["n_modulation_harmonics"] == 8
    assert setup["payload"]["harmonics"]["n_pump_harmonics"] == 16


def test_builtin_saved_setups_for_double_pumped_jpa_has_two_sources() -> None:
    setups = _builtin_saved_setups_for_schema(
        "JosephsonCircuits Examples: Double-pumped Josephson Parametric Amplifier (JPA)"
    )

    assert len(setups) == 1
    sources = setups[0]["payload"]["sources"]
    assert len(sources) == 2
    assert sources[0]["pump_freq_ghz"] == 4.65001
    assert sources[1]["pump_freq_ghz"] == 4.85001
    assert sources[0]["mode"] == [1, 0]
    assert sources[1]["mode"] == [0, 1]


def test_builtin_saved_setups_for_snail_matches_official_dual_source_bias_example() -> None:
    setups = _builtin_saved_setups_for_schema(
        "JosephsonCircuits Examples: SNAIL Parametric Amplifier"
    )

    assert len(setups) == 1
    payload = setups[0]["payload"]
    assert payload["freq_range"] == {"start_ghz": 7.8, "stop_ghz": 8.2, "points": 401}
    assert payload["harmonics"] == {"n_modulation_harmonics": 8, "n_pump_harmonics": 16}
    assert payload["advanced"]["include_dc"] is True
    assert payload["advanced"]["enable_three_wave_mixing"] is True
    assert payload["sources"] == [
        {"pump_freq_ghz": 16.0, "port": 2, "current_amp": 0.000159, "mode": [0]},
        {"pump_freq_ghz": 16.0, "port": 2, "current_amp": 4.4e-6, "mode": [1]},
    ]


def test_all_builtin_saved_setups_target_ports_declared_by_seeded_examples() -> None:
    seed_module = _load_seed_module()
    definitions = {
        name: CircuitDefinition.model_validate(ast.literal_eval(definition))
        for name, definition in seed_module.build_all()
    }

    for schema_name in definitions:
        setups = _builtin_saved_setups_for_schema(schema_name)
        assert len(setups) == 1

        payload = setups[0]["payload"]
        ports = _extract_available_port_indices(definitions[schema_name])
        for source in payload["sources"]:
            assert source["port"] in ports


def test_merge_saved_setups_with_builtin_keeps_user_setup() -> None:
    builtin = _builtin_saved_setups_for_schema(
        "JosephsonCircuits Examples: Josephson Parametric Amplifier (JPA)"
    )
    user_setup = {
        "id": "user:custom",
        "name": "My Sweep",
        "saved_at": "2026-03-01T00:00:00",
        "payload": {"freq_range": {"start_ghz": 4.4, "stop_ghz": 5.1, "points": 701}},
    }

    merged = _merge_saved_setups_with_builtin([user_setup], builtin)

    assert merged[0]["saved_at"] == "builtin"
    assert merged[1]["id"] == "user:custom"
