"""Tests for Characterization page helpers."""

from app.pages.characterization import (
    _build_analysis_run_availability,
    _build_analysis_run_bundle_record,
    _build_analysis_run_ui_state,
    _build_fit_parameter_table,
    _build_mode_vs_ljun_dataframe,
    _build_post_run_result_view_selection,
    _build_resonator_table,
    _completed_result_analysis_ids,
    _filter_method_groups_by_trace_mode,
    _format_sweep_support_reason,
    _is_summary_scalar_parameter,
    _latest_completed_analysis_run_summaries,
    _result_view_controls_row_classes,
    _result_view_empty_state_message,
    _trace_mode_filter_options,
    _trace_mode_group_for_selected_rows,
)
from app.services.characterization_runner import SweepSupportDiagnostic
from app.services.result_artifact_registry import build_result_artifacts_for_analysis
from core.shared.persistence.models import (
    DerivedParameter,
    DeviceType,
)


def test_build_analysis_run_bundle_record_captures_dataset_scope_input() -> None:
    bundle = _build_analysis_run_bundle_record(
        dataset_id=9,
        analysis_id="s21_resonance_fit",
        analysis_label="S21 Resonance Fit",
        run_id="char-test-run",
        selected_bundle_id=None,
        selected_scope_token="all_dataset_records",
        config_snapshot={"model": "notch", "f_min": 4.5},
    )

    assert bundle.dataset_id == 9
    assert bundle.bundle_type == "characterization"
    assert bundle.role == "analysis_run"
    assert bundle.status == "completed"
    assert bundle.source_meta["analysis_id"] == "s21_resonance_fit"
    assert bundle.source_meta["run_id"] == "char-test-run"
    assert bundle.source_meta["input_bundle_id"] is None
    assert bundle.source_meta["input_scope"] == "all_dataset_records"
    assert bundle.config_snapshot == {"model": "notch", "f_min": 4.5}


def test_build_analysis_run_ui_state_without_compatible_traces_disables_run() -> None:
    ui_state = _build_analysis_run_ui_state(
        has_compatible_traces=False,
        selected_trace_count=0,
    )

    assert ui_state.run_disabled is True
    assert ui_state.availability_text == "Unavailable for current scope"


def test_build_analysis_run_ui_state_with_no_selection_disables_run() -> None:
    ui_state = _build_analysis_run_ui_state(
        has_compatible_traces=True,
        selected_trace_count=0,
    )

    assert ui_state.run_disabled is True
    assert ui_state.run_hint == "Select at least one trace to run."


def test_build_analysis_run_ui_state_with_selection_enables_run() -> None:
    ui_state = _build_analysis_run_ui_state(
        has_compatible_traces=True,
        selected_trace_count=1,
    )

    assert ui_state.run_disabled is False
    assert ui_state.availability_text == "Available for current scope"


def test_build_analysis_run_availability_with_profile_hints_is_available() -> None:
    availability = _build_analysis_run_availability(
        profile_recommended=False,
        profile_hints=["Profile hint: missing capability SQUID Characterization"],
        has_compatible_traces=True,
    )
    assert availability.status == "Available"
    assert availability.has_compatible_traces is True
    assert "Profile hint" in availability.reason


def test_build_analysis_run_availability_marks_recommended_when_all_checks_pass() -> None:
    availability = _build_analysis_run_availability(
        profile_recommended=True,
        profile_hints=[],
        has_compatible_traces=True,
    )
    assert availability.status == "Recommended"
    assert availability.has_compatible_traces is True


def test_format_sweep_support_reason_renders_status_and_reason() -> None:
    diagnostic = SweepSupportDiagnostic(
        status="partial",
        reason="Single-axis 2D sweeps run per slice only.",
    )

    assert (
        _format_sweep_support_reason(diagnostic)
        == "Sweep support: partial - Single-axis 2D sweeps run per slice only."
    )


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

    artifacts = build_result_artifacts_for_analysis(
        analysis_id="admittance_extraction",
        method_groups={"admittance_zero_crossing": params},
        build_mode_vs_ljun_dataframe=_build_mode_vs_ljun_dataframe,
        build_resonator_table=_build_resonator_table,
        build_fit_parameter_table=_build_fit_parameter_table,
        is_summary_scalar=_is_summary_scalar_parameter,
    )

    mode_artifacts = [
        artifact for artifact in artifacts if artifact.view_kind == "matrix_table_plot"
    ]
    assert len(mode_artifacts) == 1
    assert mode_artifacts[0].category == "resonance"
    assert mode_artifacts[0].artifact_id.endswith(".mode_vs_ljun")


def test_build_result_artifacts_for_s21_ljun_sweep_emits_mode_vs_ljun_manifest() -> None:
    params = [
        DerivedParameter(
            dataset_id=10,
            device_type=DeviceType.RESONATOR,
            name="mode_1_ghz_b0",
            value=5.01,
            unit="GHz",
            method="complex_notch_fit_S21",
            extra={"sweep_axis": "L_jun", "sweep_value": 1.1, "sweep_index": 0},
        ),
        DerivedParameter(
            dataset_id=10,
            device_type=DeviceType.RESONATOR,
            name="L_jun_b0",
            value=1.1,
            unit="nH",
            method="complex_notch_fit_S21",
            extra={"sweep_axis": "L_jun", "sweep_value": 1.1, "sweep_index": 0},
        ),
        DerivedParameter(
            dataset_id=10,
            device_type=DeviceType.RESONATOR,
            name="mode_1_ghz_b1",
            value=5.12,
            unit="GHz",
            method="complex_notch_fit_S21",
            extra={"sweep_axis": "L_jun", "sweep_value": 1.6, "sweep_index": 1},
        ),
        DerivedParameter(
            dataset_id=10,
            device_type=DeviceType.RESONATOR,
            name="L_jun_b1",
            value=1.6,
            unit="nH",
            method="complex_notch_fit_S21",
            extra={"sweep_axis": "L_jun", "sweep_value": 1.6, "sweep_index": 1},
        ),
    ]

    artifacts = build_result_artifacts_for_analysis(
        analysis_id="s21_resonance_fit",
        method_groups={"complex_notch_fit_S21": params},
        build_mode_vs_ljun_dataframe=_build_mode_vs_ljun_dataframe,
        build_resonator_table=_build_resonator_table,
        build_fit_parameter_table=_build_fit_parameter_table,
        is_summary_scalar=_is_summary_scalar_parameter,
    )

    mode_artifacts = [
        artifact for artifact in artifacts if artifact.view_kind == "matrix_table_plot"
    ]
    assert len(mode_artifacts) == 1
    assert mode_artifacts[0].artifact_id.endswith(".mode_vs_ljun")


def test_build_result_artifacts_for_squid_emits_fit_parameters_manifest() -> None:
    params = [
        DerivedParameter(
            dataset_id=11,
            device_type=DeviceType.OTHER,
            name="Ls_nH",
            value=0.05,
            unit="nH",
            method="lc_squid_fit",
            extra={"mode": "mode_1", "rmse": 0.001, "trace_mode_group": "base"},
        ),
        DerivedParameter(
            dataset_id=11,
            device_type=DeviceType.OTHER,
            name="C_eff_pF",
            value=1.02,
            unit="pF",
            method="lc_squid_fit",
            extra={"mode": "mode_1", "rmse": 0.001, "trace_mode_group": "base"},
        ),
    ]

    artifacts = build_result_artifacts_for_analysis(
        analysis_id="squid_fitting",
        method_groups={"lc_squid_fit": params},
        build_mode_vs_ljun_dataframe=_build_mode_vs_ljun_dataframe,
        build_resonator_table=_build_resonator_table,
        build_fit_parameter_table=_build_fit_parameter_table,
        is_summary_scalar=_is_summary_scalar_parameter,
    )

    fit_artifacts = [a for a in artifacts if str(a.query_spec.get("shape")) == "fit_parameters"]
    assert fit_artifacts
    assert all(artifact.category == "fit" for artifact in fit_artifacts)
    assert any(artifact.artifact_id.endswith(".fit_parameters") for artifact in fit_artifacts)


def test_build_post_run_result_view_selection_prefers_first_fit_artifact() -> None:
    params = [
        DerivedParameter(
            dataset_id=11,
            device_type=DeviceType.OTHER,
            name="Ls_nH",
            value=0.05,
            unit="nH",
            method="lc_squid_fit",
            extra={"mode": "mode_1", "rmse": 0.001, "trace_mode_group": "base"},
        ),
        DerivedParameter(
            dataset_id=11,
            device_type=DeviceType.OTHER,
            name="C_eff_pF",
            value=1.02,
            unit="pF",
            method="lc_squid_fit",
            extra={"mode": "mode_1", "rmse": 0.001, "trace_mode_group": "base"},
        ),
    ]

    selection = _build_post_run_result_view_selection(
        analysis_id="squid_fitting",
        method_groups={"lc_squid_fit": params},
    )

    assert selection.analysis_id == "squid_fitting"
    assert selection.trace_mode_filter == "all"
    assert selection.category == "fit"
    assert selection.artifact_id.endswith(".fit_parameters")


def test_build_post_run_result_view_selection_keeps_analysis_when_no_artifacts_exist() -> None:
    selection = _build_post_run_result_view_selection(
        analysis_id="squid_fitting",
        method_groups={},
    )

    assert selection.analysis_id == "squid_fitting"
    assert selection.trace_mode_filter == "all"
    assert selection.category == ""
    assert selection.artifact_id == ""


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


def test_trace_mode_filter_preserves_lc_squid_fit_base_results() -> None:
    squid_param = DerivedParameter(
        dataset_id=12,
        device_type=DeviceType.OTHER,
        name="Ls_nH",
        value=0.05,
        unit="nH",
        method="lc_squid_fit",
        extra={"trace_mode_group": "base"},
    )
    method_groups = {"lc_squid_fit": [squid_param]}

    filtered = _filter_method_groups_by_trace_mode(
        method_groups,
        trace_mode_filter="base",
    )

    assert list(filtered) == ["lc_squid_fit"]
    assert filtered["lc_squid_fit"][0].name == "Ls_nH"


def test_result_view_empty_state_message_reports_persisted_but_unmapped_methods() -> None:
    message = _result_view_empty_state_message(
        selected_mode_label="Base",
        selected_analysis_groups_raw={"lc_squid_fit": [object()]},
        selected_analysis_groups={"lc_squid_fit": [object()]},
    )
    assert "Persisted results found but no renderable artifacts" in message
    assert "lc_squid_fit" in message


def test_result_view_empty_state_message_reports_completed_run_without_artifacts() -> None:
    message = _result_view_empty_state_message(
        selected_mode_label="All",
        selected_analysis_groups_raw={},
        selected_analysis_groups={},
        latest_completed_run_bundle_id=42,
    )

    assert "did not publish any result artifacts yet" in message
    assert "#42" in message


def test_latest_completed_analysis_run_summaries_keeps_latest_completed_bundle() -> None:
    latest = _latest_completed_analysis_run_summaries(
        [
            {
                "bundle_id": 4,
                "analysis_id": "admittance_extraction",
                "analysis_label": "Admittance Extraction",
                "status": "completed",
            },
            {
                "bundle_id": 5,
                "analysis_id": "squid_fitting",
                "analysis_label": "SQUID Fitting",
                "status": "failed",
            },
            {
                "bundle_id": 6,
                "analysis_id": "squid_fitting",
                "analysis_label": "SQUID Fitting",
                "status": "completed",
            },
        ]
    )

    assert sorted(latest) == ["admittance_extraction", "squid_fitting"]
    assert int(latest["squid_fitting"]["bundle_id"]) == 6


def test_completed_result_analysis_ids_include_completed_run_without_methods() -> None:
    completed_ids = _completed_result_analysis_ids(
        analyses=[
            {"id": "admittance_extraction"},
            {"id": "squid_fitting"},
            {"id": "y11_fit"},
        ],
        analysis_method_groups={
            "admittance_extraction": {"admittance_zero_crossing": [object()]},
            "squid_fitting": {},
            "y11_fit": {},
        },
        latest_completed_runs={
            "squid_fitting": {
                "bundle_id": 7,
                "analysis_id": "squid_fitting",
                "status": "completed",
            }
        },
    )

    assert completed_ids == ["admittance_extraction", "squid_fitting"]


def test_result_view_controls_row_uses_single_row_desktop_contract() -> None:
    classes = _result_view_controls_row_classes()
    assert "flex-wrap" in classes
    assert "lg:flex-nowrap" in classes
