"""Tests for simulation result view helpers."""

import inspect

import numpy as np

import app.pages.simulation as simulation_page
from app.pages.simulation import (
    _Z0_CONTROL_CLASSES,
    _Z0_CONTROL_PROPS,
    _build_post_processed_result_payload,
    _build_post_processed_y_data_records,
    _build_result_bundle_data_records,
    _build_s_parameter_data_records,
    _build_simulation_result_figure,
    _build_termination_compensation_plan,
    _can_save_post_processed_results,
    _coordinate_weight_fields_editable,
    _hash_schema_source,
    _hash_stable_json,
    _load_saved_post_process_setups_for_schema,
    _load_saved_setups_for_schema,
    _load_selected_post_process_setup_id,
    _matrix_element_name,
    _normalize_termination_mode,
    _normalize_termination_selected_ports,
    _normalized_simulation_setup_snapshot,
    _result_metric_options_for_family,
    _result_mode_options,
    _result_port_options,
    _result_trace_options_for_family,
    _save_saved_post_process_setups_for_schema,
    _save_saved_setups_for_schema,
    _save_selected_post_process_setup_id,
)
from core.simulation.application.post_processing import PortMatrixSweep
from core.simulation.domain.circuit import (
    DriveSourceConfig,
    FrequencyRange,
    SimulationConfig,
    SimulationResult,
)


def _sample_result() -> SimulationResult:
    return SimulationResult(
        frequencies_ghz=[4.9, 5.0, 5.1],
        s11_real=[0.2, 0.0, -0.2],
        s11_imag=[0.0, 0.1, 0.0],
        port_indices=[1, 2],
        mode_indices=[(0,), (1,)],
        s_parameter_real={
            "S11": [0.2, 0.0, -0.2],
            "S21": [1.5, 1.6, 1.7],
            "S22": [0.1, 0.1, 0.1],
        },
        s_parameter_imag={
            "S11": [0.0, 0.1, 0.0],
            "S21": [0.0, 0.0, 0.0],
            "S22": [0.0, 0.0, 0.0],
        },
        s_parameter_mode_real={
            "om=0|op=1|im=0|ip=1": [0.2, 0.0, -0.2],
            "om=0|op=2|im=0|ip=1": [1.5, 1.6, 1.7],
            "om=1|op=2|im=0|ip=1": [0.9, 1.0, 1.1],
            "om=0|op=2|im=0|ip=2": [0.1, 0.1, 0.1],
        },
        s_parameter_mode_imag={
            "om=0|op=1|im=0|ip=1": [0.0, 0.1, 0.0],
            "om=0|op=2|im=0|ip=1": [0.0, 0.0, 0.0],
            "om=1|op=2|im=0|ip=1": [0.1, 0.0, -0.1],
            "om=0|op=2|im=0|ip=2": [0.0, 0.0, 0.0],
        },
        z_parameter_mode_real={"om=0|op=2|im=0|ip=2": [100.0, 110.0, 120.0]},
        z_parameter_mode_imag={"om=0|op=2|im=0|ip=2": [0.0, 1.0, 2.0]},
        y_parameter_mode_real={"om=0|op=2|im=0|ip=2": [0.01, 0.009, 0.008]},
        y_parameter_mode_imag={"om=0|op=2|im=0|ip=2": [0.0, -0.001, -0.002]},
        qe_parameter_mode={"om=1|op=2|im=0|ip=1": [0.8, 0.82, 0.84]},
        qe_ideal_parameter_mode={"om=1|op=2|im=0|ip=1": [0.9, 0.91, 0.92]},
        cm_parameter_mode={"om=1|op=2": [1.0, 1.0, 1.0]},
    )


def test_result_metric_options_for_family_exposes_multiple_result_families() -> None:
    assert "magnitude_db" in _result_metric_options_for_family("s")
    assert "gain_db" in _result_metric_options_for_family("gain")
    assert "magnitude" in _result_metric_options_for_family("impedance")
    assert "magnitude" in _result_metric_options_for_family("admittance")
    assert "linear" in _result_metric_options_for_family("qe")
    assert "value" in _result_metric_options_for_family("cm")
    assert "trajectory" in _result_metric_options_for_family("complex")


def test_result_trace_options_for_complex_family_supports_s_z_y_traces() -> None:
    trace_options = _result_trace_options_for_family("complex")

    assert trace_options == {
        "s": "S",
        "z": "Z",
        "y": "Y",
    }


def test_result_port_options_follow_result_bundle() -> None:
    assert _result_port_options(_sample_result()) == {1: "1", 2: "2"}


def test_result_mode_options_follow_result_bundle() -> None:
    assert _result_mode_options(_sample_result()) == {
        "0": "Signal (0)",
        "1": "Sideband (1)",
    }


def test_build_simulation_result_figure_builds_impedance_view() -> None:
    figure = _build_simulation_result_figure(
        result=_sample_result(),
        view_family="impedance",
        metric="real",
        trace="z",
        output_mode=(0,),
        output_port=2,
        input_mode=(0,),
        input_port=2,
        reference_impedance_ohm=50.0,
        dark_mode=True,
    )

    assert figure.layout.title.text == "Z22 Real Part"
    assert figure.layout.yaxis.title.text == "Real (Ohm)"
    assert len(figure.data) == 1


def test_build_simulation_result_figure_builds_complex_plane_view() -> None:
    figure = _build_simulation_result_figure(
        result=_sample_result(),
        view_family="complex",
        metric="trajectory",
        trace="y",
        output_mode=(0,),
        output_port=2,
        input_mode=(0,),
        input_port=2,
        reference_impedance_ohm=50.0,
        dark_mode=True,
    )

    assert figure.layout.title.text == "Y22 Complex Plane"
    assert figure.layout.xaxis.title.text == "Real"
    assert figure.layout.yaxis.title.text == "Imaginary"
    assert len(figure.data) == 1


def test_build_simulation_result_figure_builds_selected_s_parameter_view() -> None:
    figure = _build_simulation_result_figure(
        result=_sample_result(),
        view_family="s",
        metric="magnitude_linear",
        trace="s",
        output_mode=(0,),
        output_port=2,
        input_mode=(0,),
        input_port=1,
        reference_impedance_ohm=50.0,
        dark_mode=True,
    )

    assert figure.layout.title.text == "S21 Magnitude"
    assert figure.data[0].name == "S21"


def test_build_simulation_result_figure_overlays_multiple_s_parameter_traces() -> None:
    figure = _build_simulation_result_figure(
        result=_sample_result(),
        view_family="s",
        metric="magnitude_linear",
        trace="s",
        output_mode=(0,),
        output_port=1,
        input_mode=(0,),
        input_port=1,
        reference_impedance_ohm=50.0,
        dark_mode=True,
        trace_selections=[
            {
                "trace": "s",
                "output_mode": (0,),
                "output_port": 1,
                "input_mode": (0,),
                "input_port": 1,
            },
            {
                "trace": "s",
                "output_mode": (0,),
                "output_port": 2,
                "input_mode": (0,),
                "input_port": 1,
            },
        ],
    )

    assert str(figure.layout.title.text).startswith("S-Parameter Magnitude")
    assert "S11 Magnitude" in str(figure.layout.title.text)
    assert "S21 Magnitude" in str(figure.layout.title.text)
    assert [trace.name for trace in figure.data] == ["S11", "S21"]


def test_build_simulation_result_figure_builds_sideband_qe_view() -> None:
    figure = _build_simulation_result_figure(
        result=_sample_result(),
        view_family="qe",
        metric="linear",
        trace="qe",
        output_mode=(1,),
        output_port=2,
        input_mode=(0,),
        input_port=1,
        reference_impedance_ohm=50.0,
        dark_mode=True,
    )

    assert figure.layout.title.text == "QE 21 [om=(1,), im=(0,)]"
    assert list(figure.data[0].y) == [0.8, 0.82, 0.84]


def test_build_simulation_result_figure_builds_cm_view() -> None:
    figure = _build_simulation_result_figure(
        result=_sample_result(),
        view_family="cm",
        metric="value",
        trace="cm",
        output_mode=(1,),
        output_port=2,
        input_mode=(1,),
        input_port=2,
        reference_impedance_ohm=50.0,
        dark_mode=True,
    )

    assert figure.layout.title.text == "CM2 [om=(1,)]"
    assert list(figure.data[0].y) == [1.0, 1.0, 1.0]


def test_build_s_parameter_data_records_exports_all_cached_s_traces() -> None:
    records = _build_s_parameter_data_records(dataset_id=7, result=_sample_result())

    summary = {(record.parameter, record.representation): record.values for record in records}

    assert len(records) == 6
    assert summary[("S11", "real")] == [0.2, 0.0, -0.2]
    assert summary[("S21", "imaginary")] == [0.0, 0.0, 0.0]
    assert summary[("S22", "real")] == [0.1, 0.1, 0.1]


def test_build_result_bundle_data_records_exports_mode_bundles() -> None:
    records = _build_result_bundle_data_records(dataset_id=7, result=_sample_result())

    summary = {(record.data_type, record.parameter, record.representation) for record in records}

    assert ("s_params", "S21", "real") in summary
    assert ("s_params", "S21 [om=(1,), im=(0,)]", "imaginary") in summary
    assert ("z_params", "Z22", "real") in summary
    assert ("y_params", "Y22", "imaginary") in summary
    assert ("qe", "QE21 [om=(1,), im=(0,)]", "value") in summary
    assert ("qe_ideal", "QEideal21 [om=(1,), im=(0,)]", "value") in summary
    assert ("commutation", "CM2 [om=(1,)]", "value") in summary


def test_build_post_processed_y_data_records_for_base_mode_uses_yij_names() -> None:
    sweep = PortMatrixSweep(
        mode=(0,),
        labels=("1", "2"),
        frequencies_ghz=(5.0, 5.1),
        y_matrices=(
            np.asarray(((1.0 + 0.5j, 0.1 + 0.0j), (0.2 + 0.0j, 2.0 + 0.5j))),
            np.asarray(((1.1 + 0.6j, 0.1 + 0.1j), (0.2 + 0.1j, 2.1 + 0.6j))),
        ),
        source_kind="y",
    )
    records = _build_post_processed_y_data_records(dataset_id=11, sweep=sweep)
    summary = {(record.parameter, record.representation) for record in records}
    assert ("Y11", "real") in summary
    assert ("Y12", "imaginary") in summary
    assert ("Y21", "real") in summary
    assert ("Y22", "imaginary") in summary


def test_build_post_processed_y_data_records_for_transformed_sideband_labels() -> None:
    sweep = PortMatrixSweep(
        mode=(1,),
        labels=("cm(1,2)", "dm(1,2)"),
        frequencies_ghz=(5.0,),
        y_matrices=(np.asarray(((1.0 + 0.1j, 0.0 + 0.0j), (0.0 + 0.0j, 2.0 + 0.2j))),),
        source_kind="y",
    )
    records = _build_post_processed_y_data_records(dataset_id=12, sweep=sweep)
    parameter_names = {record.parameter for record in records}
    assert "Y_cm_1_2_cm_1_2 [om=(1,), im=(1,)]" in parameter_names
    assert "Y_dm_1_2_dm_1_2 [om=(1,), im=(1,)]" in parameter_names


def test_matrix_element_name_uses_transformed_port_label_tokens() -> None:
    labels = {1: "cm(1,2)", 2: "dm(1,2)", 3: "3"}
    assert (
        _matrix_element_name(
            matrix_symbol="Z",
            output_port=2,
            input_port=2,
            port_label_by_index=labels,
        )
        == "Z_dm_dm"
    )
    assert (
        _matrix_element_name(
            matrix_symbol="Z",
            output_port=2,
            input_port=1,
            port_label_by_index=labels,
        )
        == "Z_dm_cm"
    )
    assert (
        _matrix_element_name(
            matrix_symbol="Z",
            output_port=2,
            input_port=3,
            port_label_by_index=labels,
        )
        == "Z_dm_3"
    )


def test_coordinate_weight_fields_editable_depends_on_weight_mode() -> None:
    assert _coordinate_weight_fields_editable("manual") is True
    assert _coordinate_weight_fields_editable("auto") is False
    assert _coordinate_weight_fields_editable("AUTO") is False


def test_termination_mode_and_selected_ports_are_normalized() -> None:
    assert _normalize_termination_mode("MANUAL") == "manual"
    assert _normalize_termination_mode("unexpected") == "auto"
    assert _normalize_termination_selected_ports(
        ["2", "1", "not-a-port", "2"],
        available_ports=[1, 2, 3],
    ) == [1, 2]


def test_build_termination_compensation_plan_handles_auto_and_manual() -> None:
    auto_plan = _build_termination_compensation_plan(
        enabled=True,
        mode="auto",
        selected_ports=[1, 2],
        manual_resistance_ohm_by_port={1: 33.0, 2: 44.0},
        inferred_resistance_ohm_by_port={1: 50.0, 2: 100.0},
        inferred_source_by_port={1: "schema_infer", 2: "fallback_default_50"},
        inferred_warning_by_port={2: "Port 2 fallback warning"},
    )
    assert auto_plan["enabled"] is True
    assert auto_plan["mode"] == "auto"
    assert auto_plan["resistance_ohm_by_port"] == {1: 50.0, 2: 100.0}
    assert auto_plan["source_by_port"] == {1: "schema_infer", 2: "fallback_default_50"}
    assert auto_plan["warnings"] == ["Port 2 fallback warning"]

    manual_plan = _build_termination_compensation_plan(
        enabled=True,
        mode="manual",
        selected_ports=[2],
        manual_resistance_ohm_by_port={1: 55.0, 2: 75.0},
        inferred_resistance_ohm_by_port={1: 50.0, 2: 100.0},
        inferred_source_by_port={1: "schema_infer", 2: "schema_infer"},
        inferred_warning_by_port={},
    )
    assert manual_plan["enabled"] is True
    assert manual_plan["mode"] == "manual"
    assert manual_plan["resistance_ohm_by_port"] == {2: 75.0}
    assert manual_plan["source_by_port"] == {2: "manual"}
    assert manual_plan["warnings"] == []


def test_can_save_post_processed_results_requires_valid_output_state() -> None:
    sweep = PortMatrixSweep(
        mode=(0,),
        labels=("1", "2"),
        frequencies_ghz=(5.0,),
        y_matrices=(np.asarray(((1.0 + 0.0j, 0.0), (0.0, 2.0 + 0.0j))),),
        source_kind="y",
    )
    assert _can_save_post_processed_results(sweep, {"steps": []}) is True
    assert _can_save_post_processed_results(None, {"steps": []}) is False
    assert _can_save_post_processed_results(sweep, None) is False


def test_z0_control_tokens_are_shared_across_views() -> None:
    assert _Z0_CONTROL_PROPS == "dense outlined"
    assert _Z0_CONTROL_CLASSES == "w-32"


def test_post_processing_input_panel_does_not_define_save_button() -> None:
    source = inspect.getsource(simulation_page._render_post_processing_panel)
    assert "Save Post-Processed Results" not in source


def test_post_processing_panel_exposes_setup_save_load_controls() -> None:
    source = inspect.getsource(simulation_page._render_post_processing_panel)
    assert "Post-Processing Setup" in source
    assert "Save Post-Processing Setup" in source


def test_kron_keep_basis_uses_non_dropdown_multi_select_interaction() -> None:
    source = inspect.getsource(simulation_page._render_post_processing_panel)
    assert 'ui.label("Keep Basis Labels")' in source
    assert "Select All" in source
    assert "Clear" in source
    assert "multiple=True" not in source


def test_build_post_processed_result_payload_supports_family_metric_trace_rendering() -> None:
    sweep = PortMatrixSweep(
        mode=(1,),
        labels=("cm(1,2)", "dm(1,2)"),
        frequencies_ghz=(5.0, 5.2),
        y_matrices=(
            np.asarray(((0.02 + 0.01j, 0.001 + 0.0j), (0.002 + 0.0j, 0.03 + 0.02j))),
            np.asarray(((0.021 + 0.011j, 0.0015 + 0.0j), (0.0025 + 0.0j, 0.031 + 0.021j))),
        ),
        source_kind="y",
    )
    converted, port_options = _build_post_processed_result_payload(
        sweep,
        reference_impedance_ohm=50.0,
    )
    assert port_options == {1: "cm(1,2)", 2: "dm(1,2)"}

    figure = _build_simulation_result_figure(
        result=converted,
        view_family="admittance",
        metric="imag",
        trace="admittance",
        output_mode=(1,),
        output_port=1,
        input_mode=(1,),
        input_port=1,
        reference_impedance_ohm=50.0,
        dark_mode=True,
        trace_selections=[
            {
                "trace": "admittance",
                "output_mode": (1,),
                "output_port": 1,
                "input_mode": (1,),
                "input_port": 1,
            },
            {
                "trace": "admittance",
                "output_mode": (1,),
                "output_port": 2,
                "input_mode": (1,),
                "input_port": 2,
            },
        ],
    )
    assert len(figure.data) == 2
    assert figure.layout.title.text is not None


def test_hash_stable_json_is_order_independent() -> None:
    assert _hash_stable_json({"b": 2, "a": 1}) == _hash_stable_json({"a": 1, "b": 2})


def test_hash_schema_source_changes_with_source_text() -> None:
    assert _hash_schema_source('{"name":"A"}') != _hash_schema_source('{"name":"B"}')


def test_simulation_setup_storage_roundtrip_preserves_termination_compensation(monkeypatch) -> None:
    storage: dict[str, object] = {}

    def fake_get(key: str, default: object = None) -> object:
        return storage.get(key, default)

    def fake_set(key: str, value: object) -> None:
        storage[key] = value

    monkeypatch.setattr(simulation_page, "_user_storage_get", fake_get)
    monkeypatch.setattr(simulation_page, "_user_storage_set", fake_set)

    schema_id = 183
    setup_payload = {
        "freq_range": {"start_ghz": 4.0, "stop_ghz": 5.0, "points": 101},
        "harmonics": {"n_modulation_harmonics": 4, "n_pump_harmonics": 8},
        "sources": [{"pump_freq_ghz": 4.75, "port": 1, "current_amp": 0.0, "mode": [1]}],
        "advanced": {
            "include_dc": False,
            "enable_three_wave_mixing": False,
            "enable_four_wave_mixing": True,
            "max_intermod_order": -1,
            "max_iterations": 1000,
            "f_tol": 1e-8,
            "line_search_switch_tol": 1e-5,
            "alpha_min": 1e-4,
        },
        "termination_compensation": {
            "enabled": True,
            "mode": "manual",
            "selected_ports": [1, 2],
            "manual_resistance_ohm_by_port": {"1": 50.0, "2": 75.0},
        },
    }
    _save_saved_setups_for_schema(
        schema_id,
        [{"id": "sim-a", "name": "Simulation Setup A", "payload": setup_payload}],
    )

    loaded = _load_saved_setups_for_schema(schema_id)
    assert [entry["id"] for entry in loaded] == ["sim-a"]
    assert (
        loaded[0]["payload"]["termination_compensation"]
        == setup_payload["termination_compensation"]
    )


def test_post_process_setup_storage_roundtrip_per_schema(monkeypatch) -> None:
    storage: dict[str, object] = {}

    def fake_get(key: str, default: object = None) -> object:
        return storage.get(key, default)

    def fake_set(key: str, value: object) -> None:
        storage[key] = value

    monkeypatch.setattr(simulation_page, "_user_storage_get", fake_get)
    monkeypatch.setattr(simulation_page, "_user_storage_set", fake_set)

    schema_a = 183
    schema_b = 999
    setup_payload = {
        "mode_filter": "base",
        "mode_token": "0",
        "reference_impedance_ohm": 50.0,
        "steps": [{"type": "kron_reduction", "enabled": True, "keep_labels": ["1", "2"]}],
    }
    _save_saved_post_process_setups_for_schema(
        schema_a,
        [{"id": "post-a", "name": "Post-Processing Setup A", "payload": setup_payload}],
    )
    _save_saved_post_process_setups_for_schema(
        schema_b,
        [{"id": "post-b", "name": "Post-Processing Setup B", "payload": {"steps": []}}],
    )

    loaded_a = _load_saved_post_process_setups_for_schema(schema_a)
    loaded_b = _load_saved_post_process_setups_for_schema(schema_b)
    assert [entry["id"] for entry in loaded_a] == ["post-a"]
    assert [entry["id"] for entry in loaded_b] == ["post-b"]
    assert loaded_a[0]["payload"]["steps"][0]["type"] == "kron_reduction"


def test_post_process_selected_setup_id_roundtrip(monkeypatch) -> None:
    storage: dict[str, object] = {}

    def fake_get(key: str, default: object = None) -> object:
        return storage.get(key, default)

    def fake_set(key: str, value: object) -> None:
        storage[key] = value

    monkeypatch.setattr(simulation_page, "_user_storage_get", fake_get)
    monkeypatch.setattr(simulation_page, "_user_storage_set", fake_set)

    assert _load_selected_post_process_setup_id(183) == ""
    _save_selected_post_process_setup_id(183, "post-a")
    _save_selected_post_process_setup_id(999, "post-b")
    assert _load_selected_post_process_setup_id(183) == "post-a"
    assert _load_selected_post_process_setup_id(999) == "post-b"


def test_normalized_simulation_setup_snapshot_captures_sources_and_advanced_options() -> None:
    snapshot = _normalized_simulation_setup_snapshot(
        FrequencyRange(start_ghz=4.0, stop_ghz=5.0, points=201),
        SimulationConfig(
            sources=[
                DriveSourceConfig(
                    pump_freq_ghz=4.65,
                    port=1,
                    current_amp=2e-6,
                    mode_components=(1, 0),
                ),
                DriveSourceConfig(
                    pump_freq_ghz=4.85,
                    port=2,
                    current_amp=3e-6,
                    mode_components=(0, 1),
                ),
            ],
            n_modulation_harmonics=4,
            n_pump_harmonics=6,
            include_dc=True,
            enable_three_wave_mixing=False,
            enable_four_wave_mixing=True,
            max_intermod_order=None,
            max_iterations=321,
            f_tol=1e-7,
            line_search_switch_tol=1e-6,
            alpha_min=1e-5,
        ),
    )

    assert snapshot["freq_range"] == {"start_ghz": 4.0, "stop_ghz": 5.0, "points": 201}
    assert snapshot["sources"] == [
        {"pump_freq_ghz": 4.65, "port": 1, "current_amp": 2e-06, "mode": [1, 0]},
        {"pump_freq_ghz": 4.85, "port": 2, "current_amp": 3e-06, "mode": [0, 1]},
    ]
    assert snapshot["advanced"]["include_dc"] is True
    assert snapshot["advanced"]["max_intermod_order"] == -1
