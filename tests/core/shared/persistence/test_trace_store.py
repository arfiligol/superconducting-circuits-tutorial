"""Tests for TraceStore Zarr baseline behavior."""

from __future__ import annotations

import numpy as np

from core.shared.persistence.models import DataRecord
from core.shared.persistence.trace_store import (
    LocalZarrTraceStore,
    TraceStore,
    coerce_trace_store_ref,
)


def test_local_zarr_trace_store_satisfies_contract() -> None:
    store = LocalZarrTraceStore()

    assert isinstance(store, TraceStore)


def test_local_zarr_trace_store_writes_trace_and_reads_slices(tmp_path) -> None:
    store = LocalZarrTraceStore(root_path=tmp_path / "trace_store")
    values = np.arange(12, dtype=np.float64).reshape(4, 3)

    write_result = store.write_trace(
        design_id=42,
        batch_id=105,
        trace_id=9001,
        values=values,
        axes=[
            {"name": "frequency", "unit": "GHz", "values": [4.0, 5.0, 6.0, 7.0]},
            {"name": "L_jun", "unit": "nH", "values": [8.0, 9.0, 10.0]},
        ],
    )

    assert write_result.axes == [
        {"name": "frequency", "unit": "GHz", "length": 4},
        {"name": "L_jun", "unit": "nH", "length": 3},
    ]
    assert write_result.store_ref["backend"] == "local_zarr"
    assert write_result.store_ref["group_path"] == "/traces/9001"
    assert write_result.store_ref["array_path"] == "values"
    assert write_result.store_ref["shape"] == [4, 3]
    assert write_result.store_ref["chunk_shape"] == [4, 1]
    assert write_result.store_ref["store_uri"].endswith("designs/42/batches/105.zarr")

    read_column = store.read_trace_slice(write_result.store_ref, selection=(slice(None), 1))
    np.testing.assert_array_equal(read_column, values[:, 1])

    read_row = store.read_trace_slice(write_result.store_ref, selection=(1, slice(None)))
    np.testing.assert_array_equal(read_row, values[1, :])

    axis_values = store.read_axis_slice(
        write_result.store_ref,
        axis_name="frequency",
        selection=slice(1, 3),
    )
    np.testing.assert_array_equal(axis_values, np.array([5.0, 6.0]))


def test_trace_store_ref_accepts_s3_backend_as_extension_direction() -> None:
    ref = coerce_trace_store_ref(
        {
            "backend": "s3_zarr",
            "store_uri": "s3://trace-bucket/designs/42/batches/105.zarr",
            "group_path": "/traces/9001",
            "array_path": "values",
            "dtype": "float64",
            "shape": [4001, 11],
            "chunk_shape": [4001, 1],
            "schema_version": "1.0",
        }
    )

    assert ref["backend"] == "s3_zarr"


def test_data_record_uses_store_ref_shape_metadata_without_inline_values() -> None:
    record = DataRecord(
        dataset_id=1,
        data_type="y_params",
        parameter="Y11",
        representation="imaginary",
        axes=[
            {"name": "frequency", "unit": "GHz", "length": 4001},
            {"name": "L_jun", "unit": "nH", "length": 11},
        ],
        values=[],
        store_ref={
            "backend": "local_zarr",
            "store_uri": "data/trace_store/designs/1/batches/2.zarr",
            "group_path": "/traces/3",
            "array_path": "values",
            "dtype": "float64",
            "shape": [4001, 11],
            "chunk_shape": [4001, 1],
            "schema_version": "1.0",
        },
    )

    assert record.trace_shape() == (4001, 11)
    assert record.axis_length(0) == 4001
    assert record.axis_length(1) == 11
