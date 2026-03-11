from collections.abc import Sequence
from typing import Protocol

from fastapi import HTTPException, status
from src.app.domain.circuit_definitions import (
    CircuitDefinitionDetail,
    CircuitDefinitionDraft,
    CircuitDefinitionSummary,
    CircuitDefinitionUpdate,
)


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

    def list_circuit_definitions(self) -> list[CircuitDefinitionSummary]:
        return list(self._repository.list_circuit_definitions())

    def get_circuit_definition(self, definition_id: int) -> CircuitDefinitionDetail:
        detail = self._repository.get_circuit_definition(definition_id)
        if detail is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Circuit definition {definition_id} was not found.",
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Circuit definition {definition_id} was not found.",
            )
        return detail

    def delete_circuit_definition(self, definition_id: int) -> None:
        deleted = self._repository.delete_circuit_definition(definition_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Circuit definition {definition_id} was not found.",
            )
