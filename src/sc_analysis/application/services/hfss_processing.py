#!/usr/bin/env python3
"""Service for processing HFSS data files (admittance and phase)."""

from pathlib import Path

from sc_analysis.application.preprocessing.admittance import process_hfss_admittance_file
from sc_analysis.application.preprocessing.naming import strip_component_suffix
from sc_analysis.application.preprocessing.phase import process_hfss_phase_file
from sc_analysis.domain.schemas.components import ComponentRecord
from sc_analysis.infrastructure.paths import (
    PREPROCESSED_DATA_DIR,
    RAW_LAYOUT_ADMITTANCE_DIR,
    RAW_LAYOUT_PHASE_DIR,
)
from sc_analysis.infrastructure.repositories.component_repository import (
    upsert_component_record,
    write_component_record,
)


def determine_component_id(path: Path, explicit: str | None = None) -> str:
    """Determine component ID from file path or explicit override."""
    if explicit:
        return explicit
    return strip_component_suffix(path.stem)


def resolve_input_path(raw_path: Path, search_dir: Path) -> Path | None:
    """Resolve input path, checking search_dir if raw_path doesn't exist."""
    if raw_path.exists():
        return raw_path
    candidate = search_dir / raw_path
    if candidate.exists():
        return candidate
    return None


def process_and_write_hfss_file(
    file_path: Path,
    file_type: str,
    component_id: str | None = None,
    output_path: Path | None = None,
) -> None:
    """Process an HFSS file and write the result to JSON.

    Args:
        file_path: Path to the HFSS CSV file
        file_type: Either 'admittance' or 'phase'
        component_id: Optional component ID override
        output_path: Optional output path override
    """
    # Determine paths
    if file_type == "admittance":
        search_dir = RAW_LAYOUT_ADMITTANCE_DIR
        processor = process_hfss_admittance_file
    elif file_type == "phase":
        search_dir = RAW_LAYOUT_PHASE_DIR
        processor = process_hfss_phase_file
    else:
        raise ValueError(f"Unknown file_type: {file_type}")

    # Resolve file path
    resolved_path = resolve_input_path(file_path, search_dir)
    if not resolved_path:
        print(f"[Warning] File not found: {file_path}")
        return

    # Determine component ID
    comp_id = determine_component_id(resolved_path, component_id)

    try:
        # Process the file
        record: ComponentRecord = processor(resolved_path, comp_id)

        # Determine output path
        final_output = output_path or (PREPROCESSED_DATA_DIR / f"{comp_id}.json")

        # Merge with existing if present
        merged = upsert_component_record(
            output_path=final_output,
            component_id=comp_id,
            source_type=record.source_type,
            dataset=record.datasets[0],
            raw_path=resolved_path,
        )

        # Write to disk
        write_component_record(merged, final_output)
        print(f"[OK] Wrote preprocessed record -> {final_output}")

    except Exception as e:
        print(f"[Error] Failed to process {resolved_path}: {e}")
        import traceback

        traceback.print_exc()
