from __future__ import annotations

import json
from pathlib import Path

from core.analysis.domain.schemas.components import (
    ComponentRecord,
    ParameterDataset,
    RawFileMeta,
    SourceType,
)


def load_component_record(path: Path) -> ComponentRecord:
    """
    Load and validate a component record from a JSON file.
    """
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return ComponentRecord.model_validate(data)


def load_existing_record(output_path: Path, component_id: str) -> ComponentRecord | None:
    if not output_path.exists():
        return None
    try:
        record = load_component_record(output_path)
    except Exception:
        # If file is corrupted or invalid, treat as missing?
        # Or raise error? Original code raised implicitly.
        # But here let's assume if it exists we want to read it.
        # If validation fails, it raises.
        # But if component_id mismatches, we raise.
        raise

    if record.component_id != component_id:
        raise ValueError(
            f"Existing record {output_path} belongs to component '{record.component_id}', "
            + f"which does not match requested '{component_id}'."
        )
    return record


def upsert_component_record(
    *,
    output_path: Path,
    component_id: str,
    source_type: SourceType,
    dataset: ParameterDataset,
    raw_path: Path,
) -> ComponentRecord:
    record = load_existing_record(output_path, component_id)
    if record is None:
        normalized_path = _normalize_raw_path(raw_path)
        return ComponentRecord(
            component_id=component_id,
            source_type=source_type,
            datasets=[dataset],
            raw_files=[RawFileMeta(path=normalized_path)],
        )

    _ensure_unique_dataset(record, dataset)
    record.datasets.append(dataset)
    if not _has_raw_file(record, raw_path):
        record.raw_files.append(RawFileMeta(path=_normalize_raw_path(raw_path)))
    return record


def write_component_record(record: ComponentRecord, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        # model_dump_json() returns string, we want formatted JSON
        json.dump(json.loads(record.model_dump_json()), f, indent=2)


def _ensure_unique_dataset(record: ComponentRecord, dataset: ParameterDataset) -> None:
    signature = _dataset_signature(dataset)
    for existing in record.datasets:
        if existing.dataset_id == dataset.dataset_id or _dataset_signature(existing) == signature:
            raise ValueError(
                f"Dataset '{dataset.dataset_id}' already exists in component "
                f"'{record.component_id}'. Skipping duplicate import."
            )


def _dataset_signature(dataset: ParameterDataset) -> tuple[str, str, str]:
    return (
        dataset.family.value,
        dataset.parameter.upper(),
        dataset.representation.value,
    )


def _has_raw_file(record: ComponentRecord, raw_path: Path) -> bool:
    candidate = _normalize_raw_path(raw_path)
    for meta in record.raw_files:
        existing = _normalize_existing_raw_path(meta.path)
        if existing == candidate:
            return True
    return False


def _normalize_raw_path(raw_path: Path) -> str:
    try:
        return str(raw_path.resolve(strict=False))
    except OSError:
        return str(raw_path)


def _normalize_existing_raw_path(path_str: str) -> str:
    try:
        return str(Path(path_str).resolve(strict=False))
    except OSError:
        return path_str
