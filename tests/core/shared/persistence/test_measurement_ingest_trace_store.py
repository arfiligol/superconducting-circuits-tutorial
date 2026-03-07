from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from core.analysis.application.analysis.physics.admittance import calculate_y11_imaginary
from core.analysis.application.preprocessing.dataset_payload import (
    AxisPayload,
    DataPayload,
    DatasetPayload,
)
from core.analysis.application.services.database_service import save_dataset_payload_to_db
from core.analysis.application.services.resonance_extract_service import ResonanceExtractService
from core.analysis.application.services.trace_record_materializer import materialize_trace_record
from core.shared.persistence import database as database_module
from core.shared.persistence import get_unit_of_work
from core.shared.persistence import trace_store as trace_store_module


@pytest.fixture
def isolated_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    data_root = tmp_path / "data"
    database_path = data_root / "database.db"
    trace_root = data_root / "trace_store"

    monkeypatch.setattr(database_module, "DATABASE_PATH", database_path)
    monkeypatch.setattr(trace_store_module, "DATABASE_PATH", database_path)
    monkeypatch.setattr(trace_store_module, "TRACE_STORE_PATH", trace_root)
    database_module.get_engine.cache_clear()
    yield trace_root
    database_module.get_engine.cache_clear()


def _measurement_payload(raw_file: str) -> DatasetPayload:
    frequency_ghz = np.linspace(4.0, 8.0, 201)
    l_jun_nh = np.linspace(0.8, 2.8, 9)
    values = [
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
        for freq_value in frequency_ghz
    ]

    return DatasetPayload(
        source_meta={"origin": "measurement"},
        parameters={"device_type": "squid"},
        data_records=[
            DataPayload(
                data_type="y_parameters",
                parameter="Y11",
                representation="imaginary",
                axes=[
                    AxisPayload(
                        name="Freq",
                        unit="GHz",
                        values=tuple(float(x) for x in frequency_ghz),
                    ),
                    AxisPayload(
                        name="L_jun",
                        unit="nH",
                        values=tuple(float(x) for x in l_jun_nh),
                    ),
                ],
                values=values,
            )
        ],
        raw_files=[raw_file],
    )


def test_save_dataset_payload_to_db_writes_measurement_trace_batch_and_trace_store(
    isolated_storage: Path,
) -> None:
    dataset = save_dataset_payload_to_db(
        payload=_measurement_payload("/tmp/measurement/y11.csv"),
        dataset_name="Measurement Ingest",
    )

    assert dataset.id is not None
    with get_unit_of_work() as uow:
        traces = uow.data_records.list_by_dataset(dataset.id)
        batches = uow.result_bundles.list_by_dataset(dataset.id)

    assert len(traces) == 1
    assert len(batches) == 1
    assert traces[0].values == []
    assert traces[0].store_ref["backend"] == "local_zarr"
    assert batches[0].source_kind == "measurement"
    assert batches[0].stage_kind == "raw"
    assert batches[0].result_payload["trace_count"] == 1
    assert batches[0].source_meta["raw_files"] == ["/tmp/measurement/y11.csv"]
    assert isolated_storage.joinpath(
        "designs",
        str(dataset.id),
        "batches",
        f"{batches[0].id}.zarr",
    ).exists()


def test_measurement_trace_store_records_materialize_into_characterization_path(
    isolated_storage: Path,
) -> None:
    dataset = save_dataset_payload_to_db(
        payload=_measurement_payload("/tmp/measurement/y11.csv"),
        dataset_name="Measurement Characterization",
    )

    assert dataset.id is not None
    with get_unit_of_work() as uow:
        trace = uow.data_records.list_by_dataset(dataset.id)[0]

    materialized = materialize_trace_record(trace)
    assert np.asarray(materialized.values).shape == (201, 9)
    assert materialized.axes[0]["values"][0] == pytest.approx(4.0)
    assert materialized.axes[1]["values"][-1] == pytest.approx(2.8)

    result = ResonanceExtractService().extract_admittance(str(dataset.id))
    assert result["dataset_id"] == dataset.id

    with get_unit_of_work() as uow:
        derived = uow.derived_params.list_by_dataset(dataset.id)

    assert any(param.name.startswith("mode_1_ghz") for param in derived)
    assert any(param.name.startswith("L_jun") for param in derived)
