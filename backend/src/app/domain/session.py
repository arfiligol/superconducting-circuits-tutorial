from dataclasses import dataclass
from typing import Literal

from src.app.domain.datasets import DatasetStatus

AuthState = Literal["authenticated", "anonymous"]
AuthMode = Literal["development_stub"]
WorkspaceRole = Literal["owner", "member", "viewer"]
TaskScope = Literal["workspace", "owned"]
DatasetAccessScope = Literal["workspace", "shared"]


@dataclass(frozen=True)
class SessionUser:
    user_id: str
    display_name: str
    email: str | None


@dataclass(frozen=True)
class SessionState:
    session_id: str
    auth_state: AuthState
    auth_mode: AuthMode
    scopes: tuple[str, ...]
    user: SessionUser | None
    workspace_id: str
    workspace_slug: str
    workspace_display_name: str
    workspace_role: WorkspaceRole
    default_task_scope: TaskScope
    active_dataset_id: str | None


@dataclass(frozen=True)
class ActiveDatasetContext:
    dataset_id: str
    name: str
    family: str
    status: DatasetStatus
    owner: str
    access_scope: DatasetAccessScope


@dataclass(frozen=True)
class WorkspaceContext:
    workspace_id: str
    slug: str
    display_name: str
    role: WorkspaceRole
    default_task_scope: TaskScope
    active_dataset: ActiveDatasetContext | None


@dataclass(frozen=True)
class AppSession:
    session_id: str
    auth_state: AuthState
    auth_mode: AuthMode
    scopes: tuple[str, ...]
    can_submit_tasks: bool
    can_manage_datasets: bool
    identity: SessionUser | None
    workspace: WorkspaceContext
