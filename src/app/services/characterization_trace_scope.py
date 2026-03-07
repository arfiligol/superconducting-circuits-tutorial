"""Design-scope trace query service for the Characterization page."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from core.analysis.domain import ModeGroup, ParameterKey, TraceKind
from core.shared.persistence.repositories import (
    DataRecordCharacterizationContract,
    ResultBundleCharacterizationContract,
    TraceIndexPageQuery,
)


@runtime_checkable
class CharacterizationTraceScopeUnitOfWork(Protocol):
    """Typed UoW interface consumed by design-facing trace scope queries."""

    data_records: DataRecordCharacterizationContract
    result_bundles: ResultBundleCharacterizationContract


def _normalize_analysis_data_type(data_type: str) -> str:
    """Normalize analysis data_type keys to canonical repository tokens."""
    kind = TraceKind.from_token(data_type)
    return data_type.strip().lower() if kind is TraceKind.UNKNOWN else kind.value


def _normalize_analysis_parameter_name(parameter: str) -> str:
    """Normalize analysis parameter names by stripping sideband suffix tokens."""
    return ParameterKey.from_raw(parameter).canonical


def _normalize_analysis_representation(representation: str) -> str:
    """Normalize analysis representation token to lowercase form."""
    return representation.strip().lower()


def _normalize_analysis_requirement_value(key: str, value: object) -> object:
    """Normalize one `requires` value to align with record metadata normalization."""
    if key == "data_type":
        return _normalize_analysis_data_type(str(value))
    if key == "parameter":
        if isinstance(value, list):
            return [_normalize_analysis_parameter_name(str(item)) for item in value]
        return _normalize_analysis_parameter_name(str(value))
    if key == "representation":
        return _normalize_analysis_representation(str(value))
    return value


def _normalize_analysis_requirements(requirements: dict[str, object]) -> dict[str, object]:
    """Normalize `requires` block so all matching uses one canonical rule set."""
    return {
        key: _normalize_analysis_requirement_value(key, value)
        for key, value in requirements.items()
    }


def _analysis_data_type_candidates(data_type: str) -> list[str]:
    """Resolve canonical + alias data_type keys accepted by persistence rows."""
    kind = TraceKind.from_token(data_type)
    if kind is TraceKind.UNKNOWN:
        normalized = _normalize_analysis_data_type(data_type)
        return [normalized] if normalized else []
    return list(kind.accepted_tokens)


def _analysis_query_filters(analysis_requires: dict[str, object]) -> dict[str, object]:
    """Convert analysis `requires` into DB-friendly metadata filter clauses."""
    normalized_requires = _normalize_analysis_requirements(analysis_requires)
    data_type_value = normalized_requires.get("data_type", "")
    data_types: list[str] = []
    if isinstance(data_type_value, str) and data_type_value:
        data_types = _analysis_data_type_candidates(data_type_value)

    parameter_value = normalized_requires.get("parameter")
    parameters: list[str] = []
    if isinstance(parameter_value, list):
        parameters = [str(item) for item in parameter_value if str(item)]
    elif isinstance(parameter_value, str) and parameter_value:
        parameters = [parameter_value]

    representation = str(normalized_requires.get("representation", "") or "")
    return {
        "data_types": data_types,
        "parameters": parameters,
        "representation": representation,
    }


def count_scope_trace_records(
    *,
    uow: CharacterizationTraceScopeUnitOfWork,
    dataset_id: int,
    selected_bundle_id: int | None,
) -> int:
    """Count traces visible in the current design scope."""
    if selected_bundle_id is not None:
        return uow.result_bundles.count_data_records(selected_bundle_id)
    return uow.data_records.count_by_dataset(dataset_id)


def list_scope_compatible_trace_index_page(
    *,
    uow: CharacterizationTraceScopeUnitOfWork,
    dataset_id: int,
    selected_bundle_id: int | None,
    analysis_requires: dict[str, object],
    search: str = "",
    sort_by: str = "id",
    descending: bool = False,
    mode_filter: str = "all",
    ids: Sequence[int] | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[dict[str, str | int]], int]:
    """List one page of compatible trace metadata under the current design scope."""
    filters = _analysis_query_filters(analysis_requires)
    raw_data_types = filters.get("data_types")
    raw_parameters = filters.get("parameters")
    data_types = raw_data_types if isinstance(raw_data_types, list) else []
    parameters = raw_parameters if isinstance(raw_parameters, list) else []
    normalized_mode = ModeGroup.normalize(
        mode_filter,
        allow_all=True,
        default=ModeGroup.ALL,
    )
    query = TraceIndexPageQuery(
        search=search,
        sort_by=sort_by,
        descending=descending,
        data_types=tuple(str(item) for item in data_types),
        parameters=tuple(str(item) for item in parameters),
        representation=str(filters["representation"]),
        mode_filter=normalized_mode.value,
        ids=tuple(int(record_id) for record_id in ids) if ids is not None else None,
        limit=limit,
        offset=offset,
    )
    if selected_bundle_id is not None:
        return uow.result_bundles.list_data_record_index_page(
            selected_bundle_id,
            query=query,
        )
    return uow.data_records.list_index_page_by_dataset(
        dataset_id,
        query=query,
    )


__all__ = [
    "CharacterizationTraceScopeUnitOfWork",
    "count_scope_trace_records",
    "list_scope_compatible_trace_index_page",
]
