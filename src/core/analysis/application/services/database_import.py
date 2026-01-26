"""Service for importing HFSS data directly to SQLite database."""

from pathlib import Path

from core.analysis.application.preprocessing.admittance import process_hfss_admittance_file
from core.analysis.application.preprocessing.naming import strip_component_suffix
from core.analysis.application.preprocessing.phase import process_hfss_phase_file
from core.analysis.application.services.database_service import save_component_record_to_db
from core.analysis.infrastructure.paths import (
    RAW_LAYOUT_ADMITTANCE_DIR,
    RAW_LAYOUT_PHASE_DIR,
)
from core.shared.logging import get_logger

logger = get_logger(__name__)


def resolve_input_path(raw_path: Path, search_dir: Path) -> Path | None:
    """Resolve input path, checking search_dir if raw_path doesn't exist."""
    if raw_path.exists():
        return raw_path
    candidate = search_dir / raw_path
    if candidate.exists():
        return candidate
    return None


def import_hfss_to_database(
    file_path: Path,
    file_type: str,
    dataset_name: str | None = None,
    tags: list[str] | None = None,
) -> None:
    """
    Import an HFSS file directly to SQLite database.

    Args:
        file_path: Path to the HFSS CSV file
        file_type: Either 'admittance' or 'phase'
        dataset_name: Optional dataset name override (defaults to filename)
        tags: Optional list of tags to attach to the dataset
    """
    # Determine paths and processor
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
        logger.warning("File not found: %s", file_path)
        return

    # Determine dataset name
    name = dataset_name or strip_component_suffix(resolved_path.stem)

    try:
        # Process the file to ComponentRecord
        record = processor(resolved_path, name)

        # Save to database
        save_component_record_to_db(
            record=record,
            dataset_name=name,
            tags=tags,
        )

    except Exception as e:
        logger.error("Failed to import %s: %s", resolved_path, e)
        logger.debug("Traceback:", exc_info=True)
