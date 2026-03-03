"""Tests for Characterization page helpers."""

from app.pages.characterization import (
    _analysis_record_index,
    _build_analysis_run_bundle_record,
    _build_analysis_run_ui_state,
    _build_mode_vs_ljun_dataframe,
    _build_result_artifacts_for_analysis,
    _bundle_option_label,
    _evaluate_analysis_scope_compatibility,
    _filter_method_groups_by_trace_mode,
    _result_view_controls_row_classes,
    _trace_mode_filter_options,
    _trace_mode_group_for_selected_rows,
)
from core.shared.persistence.models import (
    DataRecord,
    DerivedParameter,
    DeviceType,
    ResultBundleRecord,
)


def test_analysis_record_index_normalizes_simulation_record_aliases() -> None:
    records = [
        DataRecord(
            dataset_id=7,
            data_type="s_params",
            parameter="S21 [om=(1,), im=(0,)]",
            representation="real",
            axes=[],
            values=[],
        ),
        DataRecord(
            dataset_id=7,
            data_type="y_params",
            parameter="Y11",
            representation="imaginary",
            axes=[],
            values=[],
        ),
    ]

    assert _analysis_record_index(records) == [
        {
            "data_type": "s_parameters",
            "parameter": "S21",
            "representation": "real",
        },
        {
            "data_type": "y_parameters",
            "parameter": "Y11",
            "representation": "imaginary",
        },
    ]


def test_bundle_option_label_includes_identity_and_status() -> None:
    bundle = ResultBundleRecord(
        id=12,
        dataset_id=3,
        bundle_type="circuit_simulation",
        role="manual_export",
        status="completed",
        source_meta={},
        config_snapshot={},
        result_payload={},
    )

    assert _bundle_option_label(bundle) == "#12 circuit_simulation (manual_export, completed)"


def test_build_analysis_run_bundle_record_captures_selected_input_bundle() -> None:
    bundle = _build_analysis_run_bundle_record(
        dataset_id=9,
        analysis_id="s21_resonance_fit",
        analysis_label="S21 Resonance Fit",
        selected_bundle_id=5,
        config_snapshot={"model": "notch", "f_min": 4.5},
    )

    assert bundle.dataset_id == 9
    assert bundle.bundle_type == "characterization"
    assert bundle.role == "analysis_run"
    assert bundle.status == "completed"
    assert bundle.source_meta["analysis_id"] == "s21_resonance_fit"
    assert bundle.source_meta["input_bundle_id"] == 5
    assert bundle.config_snapshot == {"model": "notch", "f_min": 4.5}


def test_compatibility_zero_marks_unavailable_and_disables_run() -> None:
    compatibility = _evaluate_analysis_scope_compatibility(
        scoped_record_index=[
            {
                "id": 11,
                "data_type": "s_parameters",
                "parameter": "S21",
                "representation": "real",
            }
        ],
        analysis_requires={"data_type": "y_parameters", "representation": "imaginary"},
    )
    ui_state = _build_analysis_run_ui_state(
        has_compatible_traces=compatibility.has_compatible_traces,
        selected_trace_count=0,
    )

    assert compatibility.has_compatible_traces is False
    assert compatibility.compatible_trace_rows == []
    assert compatibility.message == "Unavailable for current scope"
    assert ui_state.run_disabled is True
    assert ui_state.availability_text == "Unavailable for current scope"


def test_compatible_scope_with_zero_selection_disables_run() -> None:
    compatibility = _evaluate_analysis_scope_compatibility(
        scoped_record_index=[
            {
                "id": 21,
                "data_type": "y_parameters",
                "parameter": "Y11",
                "representation": "imaginary",
            }
        ],
        analysis_requires={"data_type": "y_parameters", "representation": "imaginary"},
    )
    ui_state = _build_analysis_run_ui_state(
        has_compatible_traces=compatibility.has_compatible_traces,
        selected_trace_count=0,
    )

    assert compatibility.has_compatible_traces is True
    assert len(compatibility.compatible_trace_rows) == 1
    assert ui_state.run_disabled is True
    assert ui_state.run_hint == "Select at least one trace to run."


def test_compatible_scope_with_selected_trace_enables_run() -> None:
    compatibility = _evaluate_analysis_scope_compatibility(
        scoped_record_index=[
            {
                "id": 31,
                "data_type": "y_parameters",
                "parameter": "Y11",
                "representation": "imaginary",
            }
        ],
        analysis_requires={"data_type": "y_parameters", "representation": "imaginary"},
    )
    ui_state = _build_analysis_run_ui_state(
        has_compatible_traces=compatibility.has_compatible_traces,
        selected_trace_count=1,
    )

    assert compatibility.has_compatible_traces is True
    assert ui_state.run_disabled is False
    assert ui_state.availability_text == "Available for current scope"


def test_compatibility_normalizes_y_params_aliases_for_scope_matching() -> None:
    compatibility = _evaluate_analysis_scope_compatibility(
        scoped_record_index=[
            {
                "id": 41,
                "data_type": "y_params",
                "parameter": "Y11 [om=(1,), im=(0,)]",
                "representation": "Imaginary",
            },
            {
                "id": 42,
                "data_type": "y_parameters",
                "parameter": "Y11",
                "representation": "imaginary",
            },
        ],
        analysis_requires={"data_type": "y_parameters", "parameter": ["Y11"]},
    )

    assert compatibility.has_compatible_traces is True
    assert {int(row["id"]) for row in compatibility.compatible_trace_rows} == {41, 42}


def test_build_mode_vs_ljun_dataframe_supports_single_column_non_sweep() -> None:
    params = [
        DerivedParameter(
            dataset_id=8,
            device_type=DeviceType.RESONATOR,
            name="mode_1_ghz",
            value=4.95,
            unit="GHz",
            method="admittance_zero_crossing",
            extra={},
        ),
        DerivedParameter(
            dataset_id=8,
            device_type=DeviceType.RESONATOR,
            name="mode_2_ghz",
            value=5.12,
            unit="GHz",
            method="admittance_zero_crossing",
            extra={},
        ),
        DerivedParameter(
            dataset_id=8,
            device_type=DeviceType.RESONATOR,
            name="L_jun",
            value=3.2,
            unit="nH",
            method="admittance_zero_crossing",
            extra={},
        ),
    ]

    dataframe = _build_mode_vs_ljun_dataframe(params)

    assert dataframe is not None
    assert dataframe.shape == (2, 1)
    assert list(dataframe.index) == ["Mode 1 (GHz)", "Mode 2 (GHz)"]
    assert "(nH)" in str(dataframe.columns[0])


def test_build_result_artifacts_for_analysis_emits_mode_vs_ljun_manifest() -> None:
    params = [
        DerivedParameter(
            dataset_id=9,
            device_type=DeviceType.RESONATOR,
            name="mode_1_ghz",
            value=5.01,
            unit="GHz",
            method="admittance_zero_crossing",
            extra={},
        ),
        DerivedParameter(
            dataset_id=9,
            device_type=DeviceType.RESONATOR,
            name="L_jun",
            value=0.0,
            unit="nH",
            method="admittance_zero_crossing",
            extra={},
        ),
    ]

    artifacts = _build_result_artifacts_for_analysis(
        analysis_id="admittance_extraction",
        method_groups={"admittance_zero_crossing": params},
    )

    mode_artifacts = [
        artifact for artifact in artifacts if artifact.view_kind == "matrix_table_plot"
    ]
    assert len(mode_artifacts) == 1
    assert mode_artifacts[0].category == "resonance"
    assert mode_artifacts[0].artifact_id.endswith(".mode_vs_ljun")


def test_trace_mode_group_for_selected_rows_maps_mixed_selection_to_sideband() -> None:
    assert _trace_mode_group_for_selected_rows([{"mode": "Base"}]) == "base"
    assert _trace_mode_group_for_selected_rows([{"mode": "Sideband"}]) == "sideband"
    assert (
        _trace_mode_group_for_selected_rows(
            [
                {"mode": "Base"},
                {"mode": "Sideband"},
            ]
        )
        == "sideband"
    )


def test_trace_mode_filter_options_and_group_filtering() -> None:
    base_param = DerivedParameter(
        dataset_id=10,
        device_type=DeviceType.RESONATOR,
        name="mode_1_ghz",
        value=5.0,
        unit="GHz",
        method="admittance_zero_crossing",
        extra={"trace_mode_group": "base"},
    )
    sideband_param = DerivedParameter(
        dataset_id=10,
        device_type=DeviceType.RESONATOR,
        name="mode_2_ghz",
        value=5.1,
        unit="GHz",
        method="admittance_zero_crossing",
        extra={"trace_mode_group": "sideband"},
    )
    method_groups = {"admittance_zero_crossing": [base_param, sideband_param]}

    options = _trace_mode_filter_options(method_groups)
    assert options["all"] == "All"
    assert options["base"] == "Base"
    assert options["sideband"] == "Sideband"
    assert "unknown" not in options

    base_only = _filter_method_groups_by_trace_mode(
        method_groups,
        trace_mode_filter="base",
    )
    assert list(base_only) == ["admittance_zero_crossing"]
    assert [param.name for param in base_only["admittance_zero_crossing"]] == ["mode_1_ghz"]


def test_result_view_controls_row_uses_single_row_desktop_contract() -> None:
    classes = _result_view_controls_row_classes()
    assert "flex-wrap" in classes
    assert "lg:flex-nowrap" in classes
