from typing import Annotated

from fastapi import APIRouter, Depends
from src.app.api.schemas.session import (
    ActiveDatasetResponse,
    ActiveDatasetUpdateRequest,
    SessionAuthResponse,
    SessionResponse,
    SessionUserResponse,
)
from src.app.domain.session import AppSession
from src.app.infrastructure.runtime import get_session_service
from src.app.services.session_service import SessionService

router = APIRouter(prefix="/session", tags=["session"])


@router.get("", response_model=SessionResponse)
def get_session(
    session_service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionResponse:
    return _build_session_response(session_service.get_session())


@router.patch("/active-dataset", response_model=SessionResponse)
def update_active_dataset(
    payload: ActiveDatasetUpdateRequest,
    session_service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionResponse:
    return _build_session_response(session_service.set_active_dataset(payload.dataset_id))


def _build_session_response(session: AppSession) -> SessionResponse:
    return SessionResponse(
        session_id=session.session_id,
        auth=SessionAuthResponse(
            state=session.auth_state,
            mode=session.auth_mode,
            scopes=list(session.scopes),
            can_submit_tasks=session.can_submit_tasks,
            can_manage_datasets=session.can_manage_datasets,
            user=(
                SessionUserResponse(
                    user_id=session.user.user_id,
                    display_name=session.user.display_name,
                    email=session.user.email,
                )
                if session.user is not None
                else None
            ),
        ),
        active_dataset=(
            ActiveDatasetResponse(
                dataset_id=session.active_dataset.dataset_id,
                name=session.active_dataset.name,
                family=session.active_dataset.family,
                status=session.active_dataset.status,
            )
            if session.active_dataset is not None
            else None
        ),
    )
