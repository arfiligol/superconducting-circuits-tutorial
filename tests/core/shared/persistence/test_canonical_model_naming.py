"""Tests for canonical dataset/design persistence naming."""

from core.shared.persistence.models import (
    DerivedParameter,
    DeviceType,
    ParameterDesignation,
    TraceBatchRecord,
    TraceRecord,
)


def test_design_scoped_records_keep_dataset_and_design_scope_distinct() -> None:
    trace = TraceRecord(
        dataset_id=11,
        design_id=101,
        data_type="y_parameters",
        parameter="Y11",
        representation="imaginary",
        axes=[],
        values=[],
        store_ref={},
    )
    batch = TraceBatchRecord(
        dataset_id=12,
        design_id=102,
        bundle_type="circuit_simulation",
        role="cache",
        status="completed",
        source_meta={},
        config_snapshot={},
        result_payload={},
    )
    derived = DerivedParameter(
        dataset_id=13,
        design_id=103,
        device_type=DeviceType.RESONATOR,
        name="mode_1_ghz",
        value=5.0,
        unit="GHz",
        method="fit",
        extra={},
    )
    designation = ParameterDesignation(
        dataset_id=14,
        design_id=104,
        designated_name="f_q",
        source_analysis_type="fit",
        source_parameter_name="mode_1_ghz",
    )

    assert trace.dataset_id == 11
    assert trace.design_id == 101
    assert batch.dataset_id == 12
    assert batch.design_id == 102
    assert derived.dataset_id == 13
    assert derived.design_id == 103
    assert designation.dataset_id == 14
    assert designation.design_id == 104


def test_design_scoped_records_apply_explicit_legacy_scope_shim_when_design_id_missing() -> None:
    trace = TraceRecord(
        dataset_id=21,
        data_type="y_parameters",
        parameter="Y11",
        representation="imaginary",
        axes=[],
        values=[],
        store_ref={},
    )

    trace.ensure_scope_ids()

    assert trace.dataset_id == 21
    assert trace.design_id == 21
