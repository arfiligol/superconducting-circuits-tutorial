from dataclasses import dataclass
from typing import Literal

from src.app.domain.datasets import DatasetStatus

AuthState = Literal["authenticated", "anonymous"]
AuthMode = Literal["development_stub"]


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
    active_dataset_id: str | None


@dataclass(frozen=True)
class ActiveDatasetContext:
    dataset_id: str
    name: str
    family: str
    status: DatasetStatus


@dataclass(frozen=True)
class AppSession:
    session_id: str
    auth_state: AuthState
    auth_mode: AuthMode
    scopes: tuple[str, ...]
    can_submit_tasks: bool
    can_manage_datasets: bool
    user: SessionUser | None
    active_dataset: ActiveDatasetContext | None
