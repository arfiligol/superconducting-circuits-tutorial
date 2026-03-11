from collections.abc import Sequence
from typing import Protocol

from src.app.domain.circuit_definitions import (
    CircuitDefinitionDetail,
    CircuitDefinitionDraft,
    CircuitDefinitionListQuery,
    CircuitDefinitionSummary,
    CircuitDefinitionUpdate,
)
from src.app.services.service_errors import service_error


class CircuitDefinitionRepository(Protocol):
    def list_circuit_definitions(self) -> Sequence[CircuitDefinitionSummary]: ...

    def get_circuit_definition(self, definition_id: int) -> CircuitDefinitionDetail | None: ...

    def create_circuit_definition(
        self,
        draft: CircuitDefinitionDraft,
    ) -> CircuitDefinitionDetail: ...

    def update_circuit_definition(
        self,
        definition_id: int,
        update: CircuitDefinitionUpdate,
    ) -> CircuitDefinitionDetail | None: ...

    def delete_circuit_definition(self, definition_id: int) -> bool: ...


class CircuitDefinitionService:
    def __init__(self, repository: CircuitDefinitionRepository) -> None:
        self._repository = repository

    def list_circuit_definitions(
        self,
        query: CircuitDefinitionListQuery,
    ) -> list[CircuitDefinitionSummary]:
        definitions = [
            summary
            for summary in self._repository.list_circuit_definitions()
            if self._matches_query(summary, query)
        ]
        return self._sort_definitions(definitions, query)

    def get_circuit_definition(self, definition_id: int) -> CircuitDefinitionDetail:
        detail = self._repository.get_circuit_definition(definition_id)
        if detail is None:
            raise service_error(
                404,
                code="circuit_definition_not_found",
                category="not_found",
                message=f"Circuit definition {definition_id} was not found.",
            )
        return detail

    def create_circuit_definition(self, draft: CircuitDefinitionDraft) -> CircuitDefinitionDetail:
        return self._repository.create_circuit_definition(draft)

    def update_circuit_definition(
        self,
        definition_id: int,
        update: CircuitDefinitionUpdate,
    ) -> CircuitDefinitionDetail:
        detail = self._repository.update_circuit_definition(definition_id, update)
        if detail is None:
            raise service_error(
                404,
                code="circuit_definition_not_found",
                category="not_found",
                message=f"Circuit definition {definition_id} was not found.",
            )
        return detail

    def delete_circuit_definition(self, definition_id: int) -> None:
        deleted = self._repository.delete_circuit_definition(definition_id)
        if not deleted:
            raise service_error(
                404,
                code="circuit_definition_not_found",
                category="not_found",
                message=f"Circuit definition {definition_id} was not found.",
            )

    def _matches_query(
        self,
        summary: CircuitDefinitionSummary,
        query: CircuitDefinitionListQuery,
    ) -> bool:
        if query.search is None:
            return True
        return query.search.casefold() in summary.name.casefold()

    def _sort_definitions(
        self,
        definitions: list[CircuitDefinitionSummary],
        query: CircuitDefinitionListQuery,
    ) -> list[CircuitDefinitionSummary]:
        reverse = query.sort_order == "desc"
        if query.sort_by == "name":
            return sorted(
                definitions,
                key=lambda summary: summary.name.casefold(),
                reverse=reverse,
            )
        if query.sort_by == "element_count":
            return sorted(
                definitions,
                key=lambda summary: summary.element_count,
                reverse=reverse,
            )
        return sorted(definitions, key=lambda summary: summary.created_at, reverse=reverse)
