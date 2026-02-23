"""Service for saving dataset payloads to SQLite database."""

from core.analysis.application.preprocessing.dataset_payload import DataPayload, DatasetPayload
from core.shared.logging import get_logger
from core.shared.persistence import DataRecord, DatasetRecord, get_unit_of_work

logger = get_logger(__name__)


def dataset_to_data_records(payload: DataPayload) -> list[DataRecord]:
    """Convert a DataPayload to DataRecord list."""
    axes_list = [
        {"name": axis.name, "unit": axis.unit, "values": list(axis.values)} for axis in payload.axes
    ]

    return [
        DataRecord(
            dataset_id=0,  # Will be set later
            data_type=payload.data_type,
            parameter=payload.parameter,
            representation=payload.representation,
            axes=axes_list,
            values=list(payload.values),
        )
    ]


def save_dataset_payload_to_db(
    payload: DatasetPayload,
    dataset_name: str,
    tags: list[str] | None = None,
) -> DatasetRecord:
    """
    Save a dataset payload to SQLite database.

    Args:
        payload: DatasetPayload from preprocessing
        dataset_name: Unique name for the dataset (e.g., "PF6FQ_Q0_XY_Y11")
        tags: Optional list of tags to attach

    Returns:
        The created DatasetRecord
    """
    with get_unit_of_work() as uow:
        existing = uow.datasets.get_by_name(dataset_name)

        source_meta: dict = dict(payload.source_meta)
        if payload.raw_files:
            source_meta["raw_files"] = list(payload.raw_files)

        if existing:
            logger.info("Dataset '%s' already exists, appending data...", dataset_name)
            dataset_record = existing

            # Optionally update source meta and parameters if needed
            # dataset_record.source_meta.update(source_meta)

            # Add new tags if any
            if tags:
                for tag_name in tags:
                    tag = uow.tags.get_or_create(tag_name)
                    if tag not in dataset_record.tags:
                        dataset_record.tags.append(tag)
        else:
            # Create DatasetRecord
            dataset_record = DatasetRecord(
                name=dataset_name,
                source_meta=source_meta,
                parameters=dict(payload.parameters),
            )
            if tags:
                for tag_name in tags:
                    tag = uow.tags.get_or_create(tag_name)
                    dataset_record.tags.append(tag)
            uow.datasets.add(dataset_record)
            uow.commit()

        # Add data records
        for payload_ds in payload.data_records:
            # If dataset existed, remove older versions of this exact record to prevent duplicates
            if existing:
                for dr in list(dataset_record.data_records):
                    if (
                        dr.data_type == payload_ds.data_type
                        and dr.parameter == payload_ds.parameter
                        and dr.representation == payload_ds.representation
                    ):
                        uow.data_records.delete(dr)

            # Insert the new data records
            for data_rec in dataset_to_data_records(payload_ds):
                data_rec.dataset_id = dataset_record.id  # type: ignore[assignment]
                uow.data_records.add(data_rec)

        uow.commit()
        logger.info("Saved to database: %s", dataset_name)
        return dataset_record
