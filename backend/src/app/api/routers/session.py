from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse

from src.app.domain.session import (
    ActiveDatasetContext,
    AppSession,
    SessionLoginResult,
    WorkspaceMembership,
    WorkspaceSwitchResult,
)
from src.app.infrastructure.runtime import get_session_service
from src.app.infrastructure.session_jwt_transport import (
    DEFAULT_SESSION_TOKEN_LIFETIME_SECONDS,
    SESSION_COOKIE_NAME,
)
from src.app.services.service_errors import ServiceError, service_error
from src.app.services.session_service import SessionService
from src.app.settings import get_settings

router = APIRouter(prefix="/session", tags=["session"])


@router.get("")
def get_session(
    request: Request,
    session_service: Annotated[SessionService, Depends(get_session_service)],
) -> JSONResponse:
    try:
        session = session_service.get_session(_session_token_from_request(request))
    except ServiceError as exc:
        return _service_error_response(exc)
    return _success_response(
        data=_serialize_session(session),
        meta={"generated_at": _generated_at(), "memberships_count": len(session.memberships)},
    )


@router.post("/login")
def login(
    payload: Annotated[object, Body(...)],
    session_service: Annotated[SessionService, Depends(get_session_service)],
) -> JSONResponse:
    try:
        email, password = _parse_login_payload(payload)
        result = session_service.login(email=email, password=password)
    except ServiceError as exc:
        return _service_error_response(exc)

    response = _success_response(
        data=_serialize_session(result.session),
        meta={
            "generated_at": _generated_at(),
            "memberships_count": len(result.session.memberships),
        },
    )
    _set_session_cookie(response, result)
    return response


@router.post("/logout")
def logout(
    request: Request,
    session_service: Annotated[SessionService, Depends(get_session_service)],
) -> JSONResponse:
    session = session_service.logout(_session_token_from_request(request))
    response = _success_response(
        data=_serialize_session(session),
        meta={"generated_at": _generated_at(), "memberships_count": len(session.memberships)},
    )
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return response


@router.patch("/active-workspace")
def switch_active_workspace(
    request: Request,
    payload: Annotated[object, Body(...)],
    session_service: Annotated[SessionService, Depends(get_session_service)],
) -> JSONResponse:
    try:
        workspace_id = _parse_workspace_switch_payload(payload)
        result = session_service.switch_active_workspace(
            _session_token_from_request(request),
            workspace_id,
        )
    except ServiceError as exc:
        return _service_error_response(exc)
    return _success_response(
        data=_serialize_workspace_switch_result(result),
        meta={
            "generated_at": _generated_at(),
            "memberships_count": len(result.session.memberships),
        },
    )


@router.patch("/active-dataset")
def update_active_dataset(
    request: Request,
    payload: Annotated[object, Body(...)],
    session_service: Annotated[SessionService, Depends(get_session_service)],
) -> JSONResponse:
    try:
        dataset_id = _parse_dataset_activation_payload(payload)
        session = session_service.set_active_dataset(
            _session_token_from_request(request),
            dataset_id,
        )
    except ServiceError as exc:
        return _service_error_response(exc)
    return _success_response(
        data=_serialize_session(session),
        meta={"generated_at": _generated_at(), "memberships_count": len(session.memberships)},
    )


def _parse_login_payload(payload: object) -> tuple[str, str]:
    body = _as_mapping(payload)
    email = body.get("email")
    password = body.get("password")
    if not isinstance(email, str) or len(email.strip()) == 0:
        raise service_error(
            400,
            code="request_validation_failed",
            category="validation_error",
            message="email must be a non-empty string.",
        )
    if not isinstance(password, str) or len(password) == 0:
        raise service_error(
            400,
            code="request_validation_failed",
            category="validation_error",
            message="password must be a non-empty string.",
        )
    return email.strip(), password


def _parse_workspace_switch_payload(payload: object) -> str:
    body = _as_mapping(payload)
    workspace_id = body.get("workspace_id")
    if not isinstance(workspace_id, str) or len(workspace_id.strip()) == 0:
        raise service_error(
            400,
            code="request_validation_failed",
            category="validation_error",
            message="workspace_id must be a non-empty string.",
        )
    return workspace_id.strip()


def _parse_dataset_activation_payload(payload: object) -> str | None:
    body = _as_mapping(payload)
    if "dataset_id" not in body:
        raise service_error(
            400,
            code="request_validation_failed",
            category="validation_error",
            message="dataset_id must be provided.",
        )
    dataset_id = body.get("dataset_id")
    if dataset_id is None:
        return None
    if not isinstance(dataset_id, str) or len(dataset_id.strip()) == 0:
        raise service_error(
            400,
            code="request_validation_failed",
            category="validation_error",
            message="dataset_id must be a non-empty string or null.",
        )
    return dataset_id.strip()


def _serialize_workspace_switch_result(result: WorkspaceSwitchResult) -> dict[str, object]:
    payload = _serialize_session(result.session)
    payload["active_dataset_resolution"] = result.active_dataset_resolution
    payload["detached_task_ids"] = list(result.detached_task_ids)
    return payload


def _serialize_session(session: AppSession) -> dict[str, object]:
    return {
        "session_id": session.session_id,
        "auth": {
            "state": session.auth.state,
            "mode": session.auth.mode,
            "reason": session.auth.reason,
        },
        "user": (
            {
                "id": session.user.user_id,
                "display_name": session.user.display_name,
                "email": session.user.email,
                "platform_role": session.user.platform_role,
            }
            if session.user is not None
            else None
        ),
        "workspace": {
            "id": session.workspace.workspace_id,
            "slug": session.workspace.slug,
            "name": session.workspace.display_name,
            "role": session.workspace.role,
            "default_task_scope": session.workspace.default_task_scope,
            "allowed_actions": {
                "switch_to": session.workspace.allowed_actions.switch_to,
                "activate_dataset": session.workspace.allowed_actions.activate_dataset,
                "invite_members": session.workspace.allowed_actions.invite_members,
                "remove_members": session.workspace.allowed_actions.remove_members,
                "transfer_owner": session.workspace.allowed_actions.transfer_owner,
            },
            "memberships": [_serialize_membership(item) for item in session.memberships],
        },
        "active_dataset": _serialize_active_dataset(session.active_dataset),
        "capabilities": {
            "can_switch_workspace": session.capabilities.can_switch_workspace,
            "can_switch_dataset": session.capabilities.can_switch_dataset,
            "can_invite_members": session.capabilities.can_invite_members,
            "can_remove_members": session.capabilities.can_remove_members,
            "can_transfer_workspace_owner": session.capabilities.can_transfer_workspace_owner,
            "can_submit_tasks": session.capabilities.can_submit_tasks,
            "can_manage_workspace_tasks": session.capabilities.can_manage_workspace_tasks,
            "can_manage_definitions": session.capabilities.can_manage_definitions,
            "can_manage_datasets": session.capabilities.can_manage_datasets,
            "can_view_audit_logs": session.capabilities.can_view_audit_logs,
        },
    }


def _serialize_membership(membership: WorkspaceMembership) -> dict[str, object]:
    return {
        "id": membership.workspace_id,
        "slug": membership.slug,
        "name": membership.display_name,
        "role": membership.role,
        "default_task_scope": membership.default_task_scope,
        "is_active": membership.is_active,
        "allowed_actions": {
            "switch_to": membership.allowed_actions.switch_to,
            "activate_dataset": membership.allowed_actions.activate_dataset,
            "invite_members": membership.allowed_actions.invite_members,
            "remove_members": membership.allowed_actions.remove_members,
            "transfer_owner": membership.allowed_actions.transfer_owner,
        },
    }


def _serialize_active_dataset(active_dataset: ActiveDatasetContext | None) -> dict[str, object] | None:
    if active_dataset is None:
        return None
    return {
        "id": active_dataset.dataset_id,
        "name": active_dataset.name,
        "family": active_dataset.family,
        "status": active_dataset.status,
        "owner_user_id": active_dataset.owner_user_id,
        "owner_display_name": active_dataset.owner_display_name,
        "workspace_id": active_dataset.workspace_id,
        "visibility_scope": active_dataset.visibility_scope,
        "lifecycle_state": active_dataset.lifecycle_state,
    }


def _success_response(
    *,
    data: dict[str, object],
    status_code: int = 200,
    meta: dict[str, object] | None = None,
) -> JSONResponse:
    content: dict[str, object] = {"ok": True, "data": data}
    if meta is not None:
        content["meta"] = meta
    return JSONResponse(status_code=status_code, content=content)


def _service_error_response(exc: ServiceError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "ok": False,
            "error": {
                "code": exc.code,
                "category": exc.category,
                "message": exc.message,
                "retryable": exc.category == "internal_error",
            },
        },
    )


def _generated_at() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_mapping(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise service_error(
            400,
            code="request_validation_failed",
            category="validation_error",
            message="Request body must be an object.",
        )
    return payload


def _session_token_from_request(request: Request) -> str | None:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token is None or len(token.strip()) == 0:
        return None
    return token


def _set_session_cookie(response: JSONResponse, result: SessionLoginResult) -> None:
    settings = get_settings()
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=result.access_token,
        httponly=True,
        samesite="lax",
        secure=settings.environment not in {"development", "test"},
        max_age=DEFAULT_SESSION_TOKEN_LIFETIME_SECONDS,
        path="/",
    )
