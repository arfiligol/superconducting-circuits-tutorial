from typing import Protocol

from src.app.domain.datasets import DatasetDetail
from src.app.domain.session import (
    ActiveDatasetContext,
    AppSession,
    SessionState,
    WorkspaceContext,
)
from src.app.services.service_errors import service_error


class SessionRepository(Protocol):
    def get_session_state(self) -> SessionState: ...

    def set_active_dataset_id(self, dataset_id: str | None) -> SessionState: ...


class SessionDatasetRepository(Protocol):
    def get_dataset(self, dataset_id: str) -> DatasetDetail | None: ...


class SessionService:
    def __init__(
        self,
        repository: SessionRepository,
        dataset_repository: SessionDatasetRepository,
    ) -> None:
        self._repository = repository
        self._dataset_repository = dataset_repository

    def get_session(self) -> AppSession:
        return self._build_session(self._repository.get_session_state())

    def set_active_dataset(self, dataset_id: str | None) -> AppSession:
        if dataset_id is not None and self._dataset_repository.get_dataset(dataset_id) is None:
            raise service_error(
                404,
                code="dataset_not_found",
                category="not_found",
                message=f"Dataset {dataset_id} was not found.",
            )
        state = self._repository.set_active_dataset_id(dataset_id)
        return self._build_session(state)

    def _build_session(self, state: SessionState) -> AppSession:
        active_dataset = None
        if state.active_dataset_id is not None:
            dataset = self._dataset_repository.get_dataset(state.active_dataset_id)
            if dataset is not None:
                active_dataset = ActiveDatasetContext(
                    dataset_id=dataset.dataset_id,
                    name=dataset.name,
                    family=dataset.family,
                    status=dataset.status,
                    owner=dataset.owner,
                    access_scope="workspace",
                )
        return AppSession(
            session_id=state.session_id,
            auth_state=state.auth_state,
            auth_mode=state.auth_mode,
            scopes=state.scopes,
            can_submit_tasks="tasks:submit" in state.scopes,
            can_manage_datasets="datasets:write" in state.scopes,
            identity=state.user,
            workspace=WorkspaceContext(
                workspace_id=state.workspace_id,
                slug=state.workspace_slug,
                display_name=state.workspace_display_name,
                role=state.workspace_role,
                default_task_scope=state.default_task_scope,
                active_dataset=active_dataset,
            ),
        )
