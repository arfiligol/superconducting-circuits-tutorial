"""Tests for canonical design-scoped persistence naming."""

from core.shared.persistence.models import (
    DerivedParameter,
    DeviceType,
    ParameterDesignation,
    TraceBatchRecord,
    TraceRecord,
)


def test_design_scoped_records_expose_canonical_design_id_alias() -> None:
    trace = TraceRecord(
        dataset_id=11,
        data_type="y_parameters",
        parameter="Y11",
        representation="imaginary",
        axes=[],
        values=[],
        store_ref={},
    )
    batch = TraceBatchRecord(
        dataset_id=12,
        bundle_type="circuit_simulation",
        role="cache",
        status="completed",
        source_meta={},
        config_snapshot={},
        result_payload={},
    )
    derived = DerivedParameter(
        dataset_id=13,
        device_type=DeviceType.RESONATOR,
        name="mode_1_ghz",
        value=5.0,
        unit="GHz",
        method="fit",
        extra={},
    )
    designation = ParameterDesignation(
        dataset_id=14,
        designated_name="f_q",
        source_analysis_type="fit",
        source_parameter_name="mode_1_ghz",
    )

    assert trace.design_id == 11
    assert batch.design_id == 12
    assert derived.design_id == 13
    assert designation.design_id == 14

    trace.design_id = 21
    batch.design_id = 22
    derived.design_id = 23
    designation.design_id = 24

    assert trace.dataset_id == 21
    assert batch.dataset_id == 22
    assert derived.dataset_id == 23
    assert designation.dataset_id == 24
