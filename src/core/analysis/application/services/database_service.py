"""Service for saving ComponentRecord data to SQLite database."""

from core.analysis.domain.schemas.components import ComponentRecord, ParameterDataset
from core.shared.persistence import DataRecord, DatasetRecord, get_unit_of_work


def dataset_to_data_records(
    pydantic_dataset: ParameterDataset,
) -> list[DataRecord]:
    """Convert a ParameterDataset to DataRecord list."""
    axes_list = [
        {"name": axis.name, "unit": axis.unit, "values": list(axis.values)}
        for axis in pydantic_dataset.axes
    ]

    return [
        DataRecord(
            dataset_id=0,  # Will be set later
            data_type=pydantic_dataset.family.value,
            parameter=pydantic_dataset.parameter,
            representation=pydantic_dataset.representation.value,
            axes=axes_list,
            values=list(pydantic_dataset.values),
        )
    ]


def save_component_record_to_db(
    record: ComponentRecord,
    dataset_name: str,
    tags: list[str] | None = None,
) -> DatasetRecord:
    """
    Save a ComponentRecord to SQLite database.

    Args:
        record: The ComponentRecord from preprocessing
        dataset_name: Unique name for the dataset (e.g., "PF6FQ_Q0_XY_Y11")
        tags: Optional list of tags to attach

    Returns:
        The created DatasetRecord
    """
    with get_unit_of_work() as uow:
        # Check if dataset already exists
        existing = uow.datasets.get_by_name(dataset_name)
        if existing:
            print(f"[Info] Dataset '{dataset_name}' already exists, updating...")
            uow.datasets.delete(existing)
            uow.commit()

        # Build source metadata
        source_meta: dict = {
            "origin": record.source_type.value,
        }
        if record.raw_files:
            source_meta["raw_files"] = [rf.path for rf in record.raw_files]

        # Create DatasetRecord
        dataset_record = DatasetRecord(
            name=dataset_name,
            source_meta=source_meta,
            parameters=dict(record.sweep_parameters),
        )

        # Add tags
        if tags:
            for tag_name in tags:
                tag = uow.tags.get_or_create(tag_name)
                dataset_record.tags.append(tag)

        # Add dataset first to get ID
        uow.datasets.add(dataset_record)
        uow.commit()

        # Add data records
        for pydantic_ds in record.datasets:
            for data_rec in dataset_to_data_records(pydantic_ds):
                data_rec.dataset_id = dataset_record.id  # type: ignore[assignment]
                uow.data_records.add(data_rec)

        uow.commit()

        print(f"[OK] Saved to database: {dataset_name}")
        return dataset_record
