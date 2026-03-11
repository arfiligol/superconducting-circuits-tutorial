from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from src.app.api.schemas.circuit_definitions import (
    CircuitDefinitionCreateRequest,
    CircuitDefinitionDetailResponse,
    CircuitDefinitionSummaryResponse,
    CircuitDefinitionUpdateRequest,
    ValidationNoticeResponse,
)
from src.app.domain.circuit_definitions import CircuitDefinitionDraft, CircuitDefinitionUpdate
from src.app.infrastructure.runtime import get_circuit_definition_service
from src.app.services.circuit_definition_service import CircuitDefinitionService

router = APIRouter(prefix="/circuit-definitions", tags=["circuit-definitions"])


@router.get("", response_model=list[CircuitDefinitionSummaryResponse])
def list_circuit_definitions(
    definition_service: Annotated[
        CircuitDefinitionService,
        Depends(get_circuit_definition_service),
    ],
) -> list[CircuitDefinitionSummaryResponse]:
    return [
        CircuitDefinitionSummaryResponse.model_validate(summary.__dict__)
        for summary in definition_service.list_circuit_definitions()
    ]


@router.get("/{definition_id}", response_model=CircuitDefinitionDetailResponse)
def get_circuit_definition(
    definition_id: int,
    definition_service: Annotated[
        CircuitDefinitionService,
        Depends(get_circuit_definition_service),
    ],
) -> CircuitDefinitionDetailResponse:
    detail = definition_service.get_circuit_definition(definition_id)
    return CircuitDefinitionDetailResponse(
        definition_id=detail.definition_id,
        name=detail.name,
        created_at=detail.created_at,
        element_count=detail.element_count,
        source_text=detail.source_text,
        normalized_output=detail.normalized_output,
        validation_notices=[
            ValidationNoticeResponse(level=notice.level, message=notice.message)
            for notice in detail.validation_notices
        ],
        preview_artifacts=list(detail.preview_artifacts),
    )


@router.post(
    "",
    response_model=CircuitDefinitionDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_circuit_definition(
    payload: CircuitDefinitionCreateRequest,
    definition_service: Annotated[
        CircuitDefinitionService,
        Depends(get_circuit_definition_service),
    ],
) -> CircuitDefinitionDetailResponse:
    detail = definition_service.create_circuit_definition(
        CircuitDefinitionDraft(name=payload.name, source_text=payload.source_text),
    )
    return get_circuit_definition(detail.definition_id, definition_service)


@router.put("/{definition_id}", response_model=CircuitDefinitionDetailResponse)
def update_circuit_definition(
    definition_id: int,
    payload: CircuitDefinitionUpdateRequest,
    definition_service: Annotated[
        CircuitDefinitionService,
        Depends(get_circuit_definition_service),
    ],
) -> CircuitDefinitionDetailResponse:
    detail = definition_service.update_circuit_definition(
        definition_id,
        CircuitDefinitionUpdate(name=payload.name, source_text=payload.source_text),
    )
    return get_circuit_definition(detail.definition_id, definition_service)


@router.delete("/{definition_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_circuit_definition(
    definition_id: int,
    definition_service: Annotated[
        CircuitDefinitionService,
        Depends(get_circuit_definition_service),
    ],
) -> Response:
    definition_service.delete_circuit_definition(definition_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
