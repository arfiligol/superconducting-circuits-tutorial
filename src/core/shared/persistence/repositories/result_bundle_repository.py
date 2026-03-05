"""Repository for ResultBundleRecord operations."""

from collections.abc import Sequence
from typing import Any, cast

from sqlalchemy import String, asc, case, desc, func, not_, or_
from sqlalchemy import cast as sa_cast
from sqlalchemy import select as sa_select
from sqlmodel import Session, select

from core.shared.persistence.models import (
    DataRecord,
    ResultBundleDataLink,
    ResultBundleRecord,
)
from core.shared.persistence.repositories.query_objects import TraceIndexPageQuery


class ResultBundleRepository:
    """Repository for ResultBundleRecord operations."""

    def __init__(self, session: Session):
        self._session = session

    def get(self, id: int) -> ResultBundleRecord | None:
        """Get a result bundle by ID."""
        return self._session.get(ResultBundleRecord, id)

    def add(self, bundle: ResultBundleRecord) -> ResultBundleRecord:
        """Add a new result bundle."""
        self._session.add(bundle)
        return bundle

    def _dataset_statement(
        self,
        *,
        dataset_id: int,
        bundle_type: str | None = None,
        role: str | None = None,
        include_cache: bool = True,
    ):
        statement = select(ResultBundleRecord).where(ResultBundleRecord.dataset_id == dataset_id)
        if bundle_type:
            statement = statement.where(ResultBundleRecord.bundle_type == bundle_type)
        if role:
            statement = statement.where(ResultBundleRecord.role == role)
        elif not include_cache:
            statement = statement.where(ResultBundleRecord.role != "cache")
        return statement

    def list_by_dataset(self, dataset_id: int) -> list[ResultBundleRecord]:
        """List all result bundles under one dataset."""
        statement = self._dataset_statement(dataset_id=dataset_id).order_by(ResultBundleRecord.id)  # type: ignore[arg-type]
        return list(self._session.exec(statement).all())

    def list_cache_by_dataset(self, dataset_id: int) -> list[ResultBundleRecord]:
        """List cache-role bundles under one dataset."""
        statement = self._dataset_statement(
            dataset_id=dataset_id,
            role="cache",
        ).order_by(ResultBundleRecord.id)  # type: ignore[arg-type]
        return list(self._session.exec(statement).all())

    def list_provenance_by_dataset(self, dataset_id: int) -> list[ResultBundleRecord]:
        """List non-cache provenance bundles under one dataset."""
        statement = self._dataset_statement(
            dataset_id=dataset_id,
            include_cache=False,
        ).order_by(ResultBundleRecord.id)  # type: ignore[arg-type]
        return list(self._session.exec(statement).all())

    def count_by_dataset(
        self,
        dataset_id: int,
        *,
        bundle_type: str | None = None,
        role: str | None = None,
        include_cache: bool = True,
    ) -> int:
        """Count bundles under one dataset with optional semantic filters."""
        statement = self._dataset_statement(
            dataset_id=dataset_id,
            bundle_type=bundle_type,
            role=role,
            include_cache=include_cache,
        )
        count_statement = sa_select(func.count()).select_from(statement.subquery())
        return int(self._session.execute(count_statement).scalar_one())

    def find_simulation_cache(
        self,
        *,
        dataset_id: int,
        schema_source_hash: str,
        simulation_setup_hash: str,
    ) -> ResultBundleRecord | None:
        """Find one completed circuit-simulation cache bundle by formal identity."""
        statement = (
            select(ResultBundleRecord)
            .where(ResultBundleRecord.dataset_id == dataset_id)
            .where(ResultBundleRecord.bundle_type == "circuit_simulation")
            .where(ResultBundleRecord.role == "cache")
            .where(ResultBundleRecord.status == "completed")
            .where(ResultBundleRecord.schema_source_hash == schema_source_hash)
            .where(ResultBundleRecord.simulation_setup_hash == simulation_setup_hash)
            .order_by(ResultBundleRecord.id.desc())  # type: ignore[union-attr]
        )
        return self._session.exec(statement).first()

    def attach_data_records(self, *, bundle_id: int, data_record_ids: list[int]) -> None:
        """Attach existing DataRecord rows to a bundle."""
        for data_record_id in data_record_ids:
            self._session.add(
                ResultBundleDataLink(
                    result_bundle_id=bundle_id,
                    data_record_id=data_record_id,
                )
            )

    def list_data_records(self, bundle_id: int) -> list[DataRecord]:
        """List all DataRecord rows attached to one bundle."""
        statement = (
            select(DataRecord)
            .join(
                ResultBundleDataLink,
                DataRecord.id == ResultBundleDataLink.data_record_id,  # type: ignore[arg-type]
            )
            .where(ResultBundleDataLink.result_bundle_id == bundle_id)
            .order_by(DataRecord.id)  # type: ignore[arg-type]
        )
        return list(self._session.exec(statement).all())

    def list_data_record_index(self, bundle_id: int) -> list[dict[str, str | int]]:
        """List lightweight metadata for bundle-linked DataRecord rows only."""
        statement = (
            select(
                DataRecord.id,
                DataRecord.data_type,
                DataRecord.parameter,
                DataRecord.representation,
            )
            .join(
                ResultBundleDataLink,
                DataRecord.id == ResultBundleDataLink.data_record_id,  # type: ignore[arg-type]
            )
            .where(ResultBundleDataLink.result_bundle_id == bundle_id)
            .order_by(DataRecord.id)  # type: ignore[arg-type]
        )
        rows = self._session.exec(statement).all()
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

    def count_data_records(self, bundle_id: int) -> int:
        """Count trace membership rows for one bundle."""
        bundle_col = cast(Any, ResultBundleDataLink.result_bundle_id)
        statement = sa_select(func.count()).where(bundle_col == bundle_id)
        return int(self._session.execute(statement).scalar_one())

    def list_data_record_index_page(
        self,
        bundle_id: int,
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
        """List one page of bundle-linked trace metadata rows."""
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
        bundle_col = cast(Any, ResultBundleDataLink.result_bundle_id)
        link_record_col = cast(Any, ResultBundleDataLink.data_record_id)

        statement = (
            sa_select(
                id_col,
                data_type_col,
                parameter_col,
                representation_col,
            )
            .join(
                ResultBundleDataLink,
                id_col == link_record_col,
            )
            .where(bundle_col == bundle_id)
        )

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
