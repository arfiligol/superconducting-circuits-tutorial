"""Logical AnalysisRun repository backed by characterization TraceBatch rows."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from sqlmodel import Session, select

from core.shared.persistence.models import AnalysisRunRecord, TraceBatchRecord
from core.shared.persistence.repositories.contracts import AnalysisRunSummary

_ANALYSIS_BUNDLE_TYPE = "characterization"
_ANALYSIS_ROLE = "analysis_run"
_EXECUTION_CONFIG_KEYS = {
    "input_trace_ids",
    "selected_trace_ids",
    "selected_trace_count",
    "trace_mode_group",
    "selected_trace_mode_group",
}


def _coerce_int_list(raw_value: object) -> list[int]:
    """Normalize one persisted id-list payload into ints only."""
    if not isinstance(raw_value, list):
        return []

    normalized: list[int] = []
    for item in raw_value:
        if isinstance(item, bool):
            normalized.append(int(item))
            continue
        if isinstance(item, int):
            normalized.append(item)
            continue
        if isinstance(item, float):
            normalized.append(int(item))
            continue
        if isinstance(item, str):
            try:
                normalized.append(int(item))
            except ValueError:
                continue
    return normalized


def _analysis_run_batch_query(*, design_id: int | None = None):
    """Build the canonical characterization-analysis-run batch query."""
    statement = (
        select(TraceBatchRecord)
        .where(TraceBatchRecord.bundle_type == _ANALYSIS_BUNDLE_TYPE)
        .where(TraceBatchRecord.role == _ANALYSIS_ROLE)
    )
    if design_id is not None:
        statement = statement.where(TraceBatchRecord.dataset_id == design_id)
    return statement.order_by(TraceBatchRecord.id)  # type: ignore[arg-type]


def is_analysis_run_batch(batch: TraceBatchRecord | None) -> bool:
    """Return whether one TraceBatch row is the physical analysis-run carrier."""
    if batch is None:
        return False
    return batch.bundle_type == _ANALYSIS_BUNDLE_TYPE and batch.role == _ANALYSIS_ROLE


def analysis_run_record_from_batch(batch: TraceBatchRecord) -> AnalysisRunRecord:
    """Project one characterization TraceBatch row into the logical run contract."""
    source_meta = dict(batch.source_meta) if isinstance(batch.source_meta, dict) else {}
    config_snapshot = dict(batch.config_snapshot) if isinstance(batch.config_snapshot, dict) else {}
    result_payload = dict(batch.result_payload) if isinstance(batch.result_payload, dict) else {}

    input_batch_ids = _coerce_int_list(source_meta.get("input_batch_ids"))
    if not input_batch_ids:
        legacy_batch_id = source_meta.get("input_bundle_id")
        if isinstance(legacy_batch_id, (int, float)) and not isinstance(legacy_batch_id, bool):
            input_batch_ids = [int(legacy_batch_id)]

    input_trace_ids = _coerce_int_list(source_meta.get("input_trace_ids"))
    if not input_trace_ids:
        input_trace_ids = _coerce_int_list(config_snapshot.get("input_trace_ids"))
    if not input_trace_ids:
        input_trace_ids = _coerce_int_list(config_snapshot.get("selected_trace_ids"))

    trace_mode_group = source_meta.get("trace_mode_group")
    if not isinstance(trace_mode_group, str) or not trace_mode_group.strip():
        fallback_mode = config_snapshot.get("trace_mode_group")
        if not isinstance(fallback_mode, str) or not fallback_mode.strip():
            fallback_mode = config_snapshot.get("selected_trace_mode_group")
        trace_mode_group = str(fallback_mode).strip() if fallback_mode is not None else ""

    normalized_config_payload = deepcopy(config_snapshot)
    for key in _EXECUTION_CONFIG_KEYS:
        normalized_config_payload.pop(key, None)

    normalized_summary_payload = deepcopy(result_payload)
    selected_trace_count = config_snapshot.get("selected_trace_count")
    if (
        "selected_trace_count" not in normalized_summary_payload
        and isinstance(selected_trace_count, (int, float))
        and not isinstance(selected_trace_count, bool)
    ):
        normalized_summary_payload["selected_trace_count"] = int(selected_trace_count)

    analysis_id = str(source_meta.get("analysis_id", "")).strip()
    analysis_label = str(source_meta.get("analysis_label", analysis_id)).strip()
    run_id = str(source_meta.get("run_id", "")).strip()
    input_scope = str(source_meta.get("input_scope", "")).strip()

    return AnalysisRunRecord(
        id=int(batch.id) if batch.id is not None else None,
        design_id=int(batch.dataset_id),
        analysis_id=analysis_id,
        analysis_label=analysis_label,
        run_id=run_id,
        status=str(batch.status),
        input_trace_ids=input_trace_ids,
        input_batch_ids=input_batch_ids,
        input_scope=input_scope,
        trace_mode_group=str(trace_mode_group).strip(),
        config_payload=normalized_config_payload,
        summary_payload=normalized_summary_payload,
        created_at=batch.created_at,
        completed_at=batch.completed_at,
    )


def analysis_run_batch_from_record(record: AnalysisRunRecord) -> TraceBatchRecord:
    """Materialize one logical analysis run into the existing batch-backed storage row."""
    source_meta: dict[str, Any] = {
        "origin": "characterization",
        "source_kind": "analysis",
        "stage_kind": "analysis_run",
        "analysis_id": record.analysis_id,
        "analysis_label": record.analysis_label or record.analysis_id,
        "run_id": record.run_id,
        "input_scope": record.input_scope,
        "input_batch_ids": [int(batch_id) for batch_id in record.input_batch_ids],
        "input_trace_ids": [int(trace_id) for trace_id in record.input_trace_ids],
        "trace_mode_group": record.trace_mode_group,
    }
    if record.input_batch_ids:
        source_meta["input_bundle_id"] = int(record.input_batch_ids[0])

    return TraceBatchRecord(
        id=record.id,
        dataset_id=record.design_id,
        bundle_type=_ANALYSIS_BUNDLE_TYPE,
        role=_ANALYSIS_ROLE,
        status=record.status,
        source_meta=source_meta,
        config_snapshot=deepcopy(record.config_payload),
        result_payload=deepcopy(record.summary_payload),
        created_at=record.created_at,
        completed_at=record.completed_at,
    )


class AnalysisRunRepository:
    """Repository for logical analysis runs persisted via TraceBatchRecord rows."""

    def __init__(self, session: Session):
        self._session = session

    def add(self, analysis_run: AnalysisRunRecord) -> AnalysisRunRecord:
        """Persist one logical analysis run using the batch-backed storage row."""
        batch = analysis_run_batch_from_record(analysis_run)
        self._session.add(batch)
        self._session.flush()
        return analysis_run_record_from_batch(batch)

    def get(self, id: int) -> AnalysisRunRecord | None:
        """Load one logical analysis run by ID."""
        batch = self._session.get(TraceBatchRecord, id)
        if not is_analysis_run_batch(batch):
            return None
        return analysis_run_record_from_batch(batch)

    def list_by_design(self, design_id: int) -> list[AnalysisRunRecord]:
        """List all logical analysis runs under one design."""
        batches = self._session.exec(_analysis_run_batch_query(design_id=design_id)).all()
        return [analysis_run_record_from_batch(batch) for batch in batches]

    def list_summaries_by_design(self, design_id: int) -> list[AnalysisRunSummary]:
        """List primitive analysis-run summaries for design-scoped UI history."""
        runs = self.list_by_design(design_id)
        summaries: list[AnalysisRunSummary] = []
        for run in runs:
            if run.id is None or not run.analysis_id:
                continue
            summaries.append(
                {
                    "analysis_run_id": int(run.id),
                    "design_id": int(run.design_id),
                    "analysis_id": str(run.analysis_id),
                    "analysis_label": str(run.analysis_label or run.analysis_id),
                    "status": str(run.status),
                }
            )
        return summaries
