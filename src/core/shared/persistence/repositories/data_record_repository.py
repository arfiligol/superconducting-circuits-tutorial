"""Repository for DataRecord operations."""

from collections.abc import Sequence
from typing import Any, cast

from sqlalchemy import String, asc, case, desc, func, not_, or_
from sqlalchemy import cast as sa_cast
from sqlalchemy import select as sa_select
from sqlmodel import Session, select

from core.shared.persistence.models import DataRecord, DatasetRecord
from core.shared.persistence.repositories.query_objects import TraceIndexPageQuery


class DataRecordRepository:
    """Repository for DataRecord operations."""

    def __init__(self, session: Session):
        self._session = session

    def get(self, id: int) -> DataRecord | None:
        """Get data record by ID."""
        return self._session.get(DataRecord, id)

    def list_by_dataset(self, dataset_id: int) -> list[DataRecord]:
        """List all data records for a dataset."""
        statement = select(DataRecord).where(DataRecord.dataset_id == dataset_id)
        return list(self._session.exec(statement).all())

    def list_index_by_dataset(self, dataset_id: int) -> list[dict[str, str | int]]:
        """List lightweight record metadata for one dataset (without axis/value payloads)."""
        statement = (
            select(
                DataRecord.id,
                DataRecord.data_type,
                DataRecord.parameter,
                DataRecord.representation,
            )
            .where(DataRecord.dataset_id == dataset_id)
            .order_by(DataRecord.id)  # type: ignore[arg-type]
        )
        rows = self._session.execute(statement).all()
        return [
            {
                "id": int(record_id),
                "data_type": str(data_type),
                "parameter": str(parameter),
                "representation": str(representation),
            }
            for record_id, data_type, parameter, representation in rows
            if record_id is not None
        ]

    def count_by_dataset(self, dataset_id: int) -> int:
        """Count all records under one dataset."""
        dataset_id_col = cast(Any, DataRecord.dataset_id)
        statement = sa_select(func.count()).where(dataset_id_col == dataset_id)
        return int(self._session.execute(statement).scalar_one())

    def list_distinct_index_for_profile(self, dataset_id: int) -> list[dict[str, str]]:
        """List distinct (data_type, parameter) pairs for profile inference."""
        dataset_id_col = cast(Any, DataRecord.dataset_id)
        data_type_col = cast(Any, DataRecord.data_type)
        parameter_col = cast(Any, DataRecord.parameter)
        statement = (
            sa_select(data_type_col, parameter_col)
            .where(dataset_id_col == dataset_id)
            .distinct()
            .order_by(data_type_col, parameter_col)
        )
        rows = self._session.execute(statement).all()
        return [
            {
                "data_type": str(data_type),
                "parameter": str(parameter),
            }
            for data_type, parameter in rows
        ]

    def list_index_page_by_dataset(
        self,
        dataset_id: int,
        *,
        query: TraceIndexPageQuery | None = None,
        search: str = "",
        sort_by: str = "id",
        descending: bool = False,
        data_type: str = "",
        data_types: Sequence[str] | None = None,
        parameters: Sequence[str] | None = None,
        representation: str = "",
        mode_filter: str = "all",
        ids: Sequence[int] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[dict[str, str | int]], int]:
        """List one page of lightweight metadata rows for a dataset."""
        if query is not None:
            search = query.search
            sort_by = query.sort_by
            descending = query.descending
            data_type = query.data_type
            data_types = query.data_types
            parameters = query.parameters
            representation = query.representation
            mode_filter = query.mode_filter
            ids = query.ids
            limit = query.limit
            offset = query.offset

        id_col = cast(Any, DataRecord.id)
        data_type_col = cast(Any, DataRecord.data_type)
        parameter_col = cast(Any, DataRecord.parameter)
        representation_col = cast(Any, DataRecord.representation)
        dataset_id_col = cast(Any, DataRecord.dataset_id)

        statement = sa_select(
            id_col,
            data_type_col,
            parameter_col,
            representation_col,
        ).where(dataset_id_col == dataset_id)

        sideband_predicate = or_(
            sa_cast(parameter_col, String).ilike("% [om=%"),
            sa_cast(parameter_col, String).ilike("% [im=%"),
        )

        if ids is not None:
            normalized_ids = [int(record_id) for record_id in ids]
            if not normalized_ids:
                return ([], 0)
            statement = statement.where(id_col.in_(normalized_ids))

        search_text = search.strip()
        if search_text:
            like_value = f"%{search_text}%"
            statement = statement.where(
                or_(
                    sa_cast(id_col, String).ilike(like_value),
                    sa_cast(data_type_col, String).ilike(like_value),
                    sa_cast(parameter_col, String).ilike(like_value),
                    sa_cast(representation_col, String).ilike(like_value),
                )
            )

        normalized_data_types = [
            str(item).strip() for item in data_types or [] if str(item).strip()
        ]
        if normalized_data_types:
            statement = statement.where(
                or_(*[data_type_col == item for item in normalized_data_types])
            )
        elif data_type:
            statement = statement.where(data_type_col == data_type)
        normalized_parameters = [
            str(item).strip() for item in parameters or [] if str(item).strip()
        ]
        if normalized_parameters:
            statement = statement.where(
                or_(
                    *[
                        or_(
                            parameter_col == parameter_name,
                            parameter_col.ilike(f"{parameter_name} [%"),
                        )
                        for parameter_name in normalized_parameters
                    ]
                )
            )
        if representation:
            statement = statement.where(representation_col == representation)
        normalized_mode_filter = str(mode_filter or "").strip().lower()
        if normalized_mode_filter == "base":
            statement = statement.where(not_(sideband_predicate))
        elif normalized_mode_filter == "sideband":
            statement = statement.where(sideband_predicate)

        count_statement = sa_select(func.count()).select_from(statement.subquery())

        sort_columns = {
            "id": id_col,
            "mode": case((sideband_predicate, 1), else_=0),
            "data_type": data_type_col,
            "parameter": parameter_col,
            "representation": representation_col,
        }
        sort_column = sort_columns.get(sort_by, id_col)
        order_expression = desc(sort_column) if descending else asc(sort_column)
        statement = statement.order_by(order_expression).offset(max(0, offset)).limit(max(1, limit))

        rows = self._session.execute(statement).all()
        total_rows = int(self._session.execute(count_statement).scalar_one())
        return (
            [
                {
                    "id": int(record_id),
                    "data_type": str(row_data_type),
                    "parameter": str(row_parameter),
                    "representation": str(row_representation),
                }
                for record_id, row_data_type, row_parameter, row_representation in rows
                if record_id is not None
            ],
            total_rows,
        )

    def list_summary_by_dataset(self, dataset_id: int) -> list[dict[str, object]]:
        """List summary rows for one dataset without loading large axes/value payloads."""
        id_col = cast(Any, DataRecord.id)
        dataset_id_col = cast(Any, DataRecord.dataset_id)
        data_type_col = cast(Any, DataRecord.data_type)
        parameter_col = cast(Any, DataRecord.parameter)
        representation_col = cast(Any, DataRecord.representation)

        statement = (
            sa_select(
                id_col,
                dataset_id_col,
                data_type_col,
                parameter_col,
                representation_col,
            )
            .where(dataset_id_col == dataset_id)
            .order_by(id_col)
        )
        rows = self._session.execute(statement).all()
        return [
            {
                "id": int(record_id),
                "dataset_id": int(row_dataset_id),
                "data_type": str(data_type),
                "parameter": str(parameter),
                "representation": str(representation),
                "created_at": None,
            }
            for (
                record_id,
                row_dataset_id,
                data_type,
                parameter,
                representation,
            ) in rows
            if record_id is not None
        ]

    def add(self, record: DataRecord) -> DataRecord:
        """Add a new data record."""
        self._session.add(record)
        return record

    def list_all(self, *, include_hidden: bool = False) -> list[DataRecord]:
        """List all data records, excluding hidden-dataset rows by default."""
        statement = select(DataRecord).order_by(DataRecord.id)  # type: ignore[arg-type]
        records = list(self._session.exec(statement).all())
        if include_hidden:
            return records
        if not records:
            return []

        dataset_ids = {record.dataset_id for record in records}
        hidden_dataset_ids = {
            dataset.id
            for dataset in self._session.exec(select(DatasetRecord)).all()
            if dataset.id is not None and dataset.source_meta.get("system_hidden")
            if dataset.id in dataset_ids
        }
        return [record for record in records if record.dataset_id not in hidden_dataset_ids]

    def delete(self, record: DataRecord) -> None:
        """Delete a data record."""
        self._session.delete(record)

    def reorder_id(self, old_id: int, new_id: int) -> DataRecord:
        """Change data record ID."""
        if self.get(new_id):
            raise ValueError(f"Target ID {new_id} already exists.")

        record = self.get(old_id)
        if not record:
            raise ValueError(f"Source ID {old_id} not found.")

        # Since it's a leaf node, we can likely just update the ID directly
        # But SQLModel objects might track PK identity.
        # Direct SQL update is safer to avoid session confusion.
        from sqlmodel import update

        from core.shared.persistence.models import DataRecord, ResultBundleDataLink

        self._session.exec(
            update(ResultBundleDataLink)
            .where(ResultBundleDataLink.data_record_id == old_id)  # type: ignore[arg-type]
            .values(data_record_id=new_id)
        )

        self._session.exec(
            update(DataRecord).where(DataRecord.id == old_id).values(id=new_id)  # type: ignore[arg-type]
        )

        # Return new object
        # We need to refresh or get new one. Old object is stale.
        # But wait, we need to return valid object.
        self._session.expire(record)  # Expire old one
        updated = self.get(new_id)
        if updated is None:
            raise ValueError(f"Failed to reload record after reordering id to {new_id}.")
        return updated
