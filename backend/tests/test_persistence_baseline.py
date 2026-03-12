from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session
from src.app.infrastructure.persistence.database import build_sqlite_database_url
from src.app.infrastructure.persistence.models import (
    RewriteResultHandleRecord,
    RewriteStorageRecord,
    RewriteTracePayloadRecord,
)
from src.app.infrastructure.storage_reference_factory import (
    REWRITE_TRACE_SCHEMA_VERSION,
    build_metadata_record_ref,
    build_result_handle_ref,
    build_result_provenance_ref,
    build_trace_payload_ref,
)


def test_alembic_upgrade_creates_rewrite_storage_tables_and_supports_round_trip(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "rewrite-metadata.db"
    config = _build_alembic_config(database_path)

    command.upgrade(config, "head")

    engine = _create_engine(database_path)
    inspector = inspect(engine)
    assert sorted(inspector.get_table_names()) == [
        "alembic_version",
        "rewrite_result_handles",
        "rewrite_storage_records",
        "rewrite_trace_payloads",
    ]

    dataset_record = build_metadata_record_ref(
        "dataset",
        "dataset:fluxonium-2025-031",
        version=3,
    )
    trace_payload = build_trace_payload_ref(
        payload_role="dataset_primary",
        store_key="datasets/fluxonium-2025-031/trace-batches/88.zarr",
        store_uri="trace_store/datasets/fluxonium-2025-031/trace-batches/88.zarr",
        group_path="trace_batches/88",
        array_path="signals/iq_real",
        dtype="float64",
        shape=(184, 1024),
        chunk_shape=(16, 1024),
    )
    result_record = build_metadata_record_ref(
        "result_handle",
        "result_handle:501",
        version=2,
    )
    result_handle = build_result_handle_ref(
        handle_id="result:fluxonium-2025-031:fit-summary",
        kind="fit_summary",
        status="materialized",
        label="Fluxonium fit summary",
        metadata_record=result_record,
        payload_backend="json_artifact",
        payload_format="json",
        payload_role="report_artifact",
        payload_locator="artifacts/fit-summary.json",
        provenance_task_id=303,
        provenance=build_result_provenance_ref(
            source_dataset_id="fluxonium-2025-031",
            source_task_id=303,
            trace_batch_record=build_metadata_record_ref(
                "trace_batch",
                "trace_batch:88",
                version=1,
            ),
        ),
    )

    with Session(engine) as session:
        dataset_row = RewriteStorageRecord(
            record_type=dataset_record.record_type,
            record_id=dataset_record.record_id,
            schema_version=dataset_record.schema_version,
            version=dataset_record.version,
        )
        trace_batch_row = RewriteStorageRecord(
            record_type="trace_batch",
            record_id="trace_batch:88",
            schema_version="sqlite_metadata.v1",
            version=1,
        )
        result_metadata_row = RewriteStorageRecord(
            record_type=result_record.record_type,
            record_id=result_record.record_id,
            schema_version=result_record.schema_version,
            version=result_record.version,
        )
        session.add_all([dataset_row, trace_batch_row, result_metadata_row])
        session.flush()

        session.add(
            RewriteTracePayloadRecord(
                owner_record_id=dataset_row.id,
                contract_version=trace_payload.contract_version,
                backend=trace_payload.backend,
                payload_role=trace_payload.payload_role,
                store_key=trace_payload.store_key,
                store_uri=trace_payload.store_uri,
                group_path=trace_payload.group_path,
                array_path=trace_payload.array_path,
                dtype=trace_payload.dtype,
                shape=list(trace_payload.shape),
                chunk_shape=list(trace_payload.chunk_shape),
                schema_version=trace_payload.schema_version,
                writer_version="rewrite-backend.v0",
            )
        )
        session.add(
            RewriteResultHandleRecord(
                metadata_record_id=result_metadata_row.id,
                handle_id=result_handle.handle_id,
                contract_version=result_handle.contract_version,
                kind=result_handle.kind,
                status=result_handle.status,
                label=result_handle.label,
                payload_backend=result_handle.payload_backend,
                payload_format=result_handle.payload_format,
                payload_role=result_handle.payload_role,
                payload_locator=result_handle.payload_locator,
                provenance_task_id=result_handle.provenance_task_id,
                source_dataset_id=result_handle.provenance.source_dataset_id,
                source_task_id=result_handle.provenance.source_task_id,
                trace_batch_record_id=trace_batch_row.id,
                analysis_run_record_id=None,
            )
        )
        session.commit()

        persisted_trace = session.scalar(
            select(RewriteTracePayloadRecord).where(
                RewriteTracePayloadRecord.store_key == trace_payload.store_key
            )
        )
        persisted_result = session.scalar(
            select(RewriteResultHandleRecord).where(
                RewriteResultHandleRecord.handle_id == result_handle.handle_id
            )
        )

    assert persisted_trace is not None
    assert persisted_trace.schema_version == REWRITE_TRACE_SCHEMA_VERSION
    assert persisted_trace.shape == [184, 1024]
    assert persisted_result is not None
    assert persisted_result.source_dataset_id == "fluxonium-2025-031"
    assert persisted_result.provenance_task_id == 303


def _build_alembic_config(database_path: Path) -> Config:
    backend_root = Path(__file__).resolve().parents[1]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "alembic"))
    config.set_main_option("sqlalchemy.url", build_sqlite_database_url(database_path))
    return config


def _create_engine(database_path: Path):
    from sqlalchemy import create_engine

    return create_engine(build_sqlite_database_url(database_path))
