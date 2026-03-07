from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from core.analysis.application.preprocessing.dataset_payload import (
    AxisPayload,
    DataPayload,
    DatasetPayload,
)
from core.analysis.application.services.data_record_management import DataRecordManagementService
from core.analysis.application.services.database_service import save_dataset_payload_to_db
from core.analysis.application.services.resonance_extract_service import ResonanceExtractService
from core.shared.persistence import LocalZarrTraceStore, get_unit_of_work
from core.shared.persistence import database as persistence_database


@pytest.fixture
def isolated_persistence(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
):
    db_path = tmp_path / "database.db"
    monkeypatch.setattr(persistence_database, "DATABASE_PATH", db_path)
    monkeypatch.setenv("SC_TRACE_STORE_ROOT", str(tmp_path / "trace_store"))
    persistence_database.get_engine.cache_clear()
    yield
    persistence_database.get_engine.cache_clear()


def _layout_payload(*, parameter: str = "Y11") -> DatasetPayload:
    return DatasetPayload(
        source_meta={"origin": "layout_simulation"},
        parameters={"design_family": "layout"},
        data_records=[
            DataPayload(
                data_type="y_parameters",
                parameter=parameter,
                representation="imaginary",
                axes=[
                    AxisPayload(name="Freq", unit="GHz", values=[4.8, 4.9, 5.0]),
                    AxisPayload(name="L_jun", unit="nH", values=[8.0, 9.0]),
                ],
                values=[
                    [-2.0, -1.0],
                    [0.2, 0.5],
                    [1.2, 1.6],
                ],
            )
        ],
        raw_files=["/tmp/layout/Y11.csv"],
    )


def test_save_dataset_payload_to_db_materializes_layout_traces_to_trace_store(
    isolated_persistence,
) -> None:
    design = save_dataset_payload_to_db(
        _layout_payload(),
        dataset_name="Layout Design",
        tags=["hfss"],
    )

    with get_unit_of_work() as uow:
        saved_design = uow.datasets.get(int(design.id or 0))
        traces = uow.data_records.list_by_dataset(int(design.id or 0))
        batches = uow.result_bundles.list_by_dataset(int(design.id or 0))

        assert saved_design is not None
        assert saved_design.source_meta["origin"] == "layout_simulation"
        assert saved_design.source_meta["raw_files"] == ["/tmp/layout/Y11.csv"]
        assert [tag.name for tag in saved_design.tags] == ["hfss"]

        assert len(traces) == 1
        trace = traces[0]
        assert trace.values == []
        assert trace.axes == [
            {"name": "Freq", "unit": "GHz", "length": 3},
            {"name": "L_jun", "unit": "nH", "length": 2},
        ]
        assert trace.store_ref["backend"] == "local_zarr"

        assert len(batches) == 1
        batch = batches[0]
        assert batch.source_kind == "layout_simulation"
        assert batch.stage_kind == "raw"
        assert batch.result_payload["trace_count"] == 1
        assert uow.result_bundles.list_traces(int(batch.id or 0))[0].id == trace.id

    store = LocalZarrTraceStore()
    np.testing.assert_allclose(
        store.read_trace_slice(trace.store_ref, selection=()),
        np.array([[-2.0, -1.0], [0.2, 0.5], [1.2, 1.6]]),
    )
    np.testing.assert_allclose(
        store.read_axis_slice(trace.store_ref, axis_name="Freq"),
        np.array([4.8, 4.9, 5.0]),
    )

    detail = DataRecordManagementService().get_record(int(trace.id or 0))
    assert detail is not None
    assert detail.axes[0]["values"] == [4.8, 4.9, 5.0]
    assert detail.axes[1]["values"] == [8.0, 9.0]
    assert detail.values == [[-2.0, -1.0], [0.2, 0.5], [1.2, 1.6]]


def test_resonance_extract_service_reads_store_backed_layout_trace(
    isolated_persistence,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    design = save_dataset_payload_to_db(_layout_payload(), dataset_name="Characterization Layout")
    captured: dict[str, object] = {}

    def fake_extract_modes(df: pd.DataFrame) -> pd.DataFrame:
        captured["row_count"] = len(df)
        captured["columns"] = list(df.columns)
        return pd.DataFrame(
            [
                {
                    "L_jun": 8.0,
                    "Mode 1": 4.91,
                }
            ]
        )

    monkeypatch.setattr(
        "core.analysis.application.services.resonance_extract_service.extract_modes_from_dataframe",
        fake_extract_modes,
    )

    result = ResonanceExtractService().extract_admittance(str(int(design.id or 0)))

    assert result["dataset_id"] == int(design.id or 0)
    assert captured["row_count"] == 6
    assert captured["columns"] == ["Freq [GHz]", "im(Y) []", "L_jun [nH]"]

    with get_unit_of_work() as uow:
        params = uow.derived_params.list_by_dataset(int(design.id or 0))

    assert {param.name for param in params} >= {"L_jun", "mode_1_ghz"}
