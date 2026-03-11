from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from src.app.api.schemas.circuit_definitions import (
    CircuitDefinitionCreateRequest,
    CircuitDefinitionDetailResponse,
    CircuitDefinitionMutationResponse,
    CircuitDefinitionSummaryResponse,
    CircuitDefinitionUpdateRequest,
    CircuitDefinitionValidationSummaryResponse,
    ValidationNoticeResponse,
)
from src.app.domain.circuit_definitions import (
    CircuitDefinitionDetail,
    CircuitDefinitionDraft,
    CircuitDefinitionListQuery,
    CircuitDefinitionSortBy,
    CircuitDefinitionSummary,
    CircuitDefinitionUpdate,
    SortOrder,
)
from src.app.infrastructure.runtime import get_circuit_definition_service
from src.app.services.circuit_definition_service import CircuitDefinitionService

router = APIRouter(prefix="/circuit-definitions", tags=["circuit-definitions"])


@router.get("", response_model=list[CircuitDefinitionSummaryResponse])
def list_circuit_definitions(
    definition_service: Annotated[
        CircuitDefinitionService,
        Depends(get_circuit_definition_service),
    ],
    search: Annotated[str | None, Query(min_length=1)] = None,
    sort_by: Annotated[CircuitDefinitionSortBy, Query()] = "created_at",
    sort_order: Annotated[SortOrder, Query()] = "desc",
) -> list[CircuitDefinitionSummaryResponse]:
    return [
        _build_circuit_definition_summary_response(summary)
        for summary in definition_service.list_circuit_definitions(
            CircuitDefinitionListQuery(
                search=search,
                sort_by=sort_by,
                sort_order=sort_order,
            ),
        )
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
    return _build_circuit_definition_detail_response(detail)


@router.post(
    "",
    response_model=CircuitDefinitionMutationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_circuit_definition(
    payload: CircuitDefinitionCreateRequest,
    definition_service: Annotated[
        CircuitDefinitionService,
        Depends(get_circuit_definition_service),
    ],
) -> CircuitDefinitionMutationResponse:
    detail = definition_service.create_circuit_definition(
        CircuitDefinitionDraft(name=payload.name, source_text=payload.source_text),
    )
    return CircuitDefinitionMutationResponse(
        operation="created",
        definition=_build_circuit_definition_detail_response(detail),
    )


@router.put("/{definition_id}", response_model=CircuitDefinitionMutationResponse)
def update_circuit_definition(
    definition_id: int,
    payload: CircuitDefinitionUpdateRequest,
    definition_service: Annotated[
        CircuitDefinitionService,
        Depends(get_circuit_definition_service),
    ],
) -> CircuitDefinitionMutationResponse:
    detail = definition_service.update_circuit_definition(
        definition_id,
        CircuitDefinitionUpdate(name=payload.name, source_text=payload.source_text),
    )
    return CircuitDefinitionMutationResponse(
        operation="updated",
        definition=_build_circuit_definition_detail_response(detail),
    )


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


def _build_circuit_definition_summary_response(
    summary: CircuitDefinitionSummary,
) -> CircuitDefinitionSummaryResponse:
    return CircuitDefinitionSummaryResponse.model_validate(summary.__dict__)


def _build_circuit_definition_detail_response(
    detail: CircuitDefinitionDetail,
) -> CircuitDefinitionDetailResponse:
    warning_count = sum(1 for notice in detail.validation_notices if notice.level == "warning")
    return CircuitDefinitionDetailResponse(
        definition_id=detail.definition_id,
        name=detail.name,
        created_at=detail.created_at,
        element_count=detail.element_count,
        validation_status="warning" if warning_count else "ok",
        preview_artifact_count=len(detail.preview_artifacts),
        source_text=detail.source_text,
        normalized_output=detail.normalized_output,
        validation_notices=[
            ValidationNoticeResponse(level=notice.level, message=notice.message)
            for notice in detail.validation_notices
        ],
        validation_summary=CircuitDefinitionValidationSummaryResponse(
            status="warning" if warning_count else "ok",
            notice_count=len(detail.validation_notices),
            warning_count=warning_count,
        ),
        preview_artifacts=list(detail.preview_artifacts),
    )
