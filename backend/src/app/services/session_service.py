from collections.abc import Sequence
from typing import Protocol

from src.app.domain.datasets import DatasetDetail
from src.app.domain.session import (
    ActiveDatasetContext,
    AppSession,
    DatasetResolution,
    SessionCapabilities,
    SessionState,
    WorkspaceAllowedActions,
    WorkspaceContext,
    WorkspaceMembership,
    WorkspaceSwitchResult,
)
from src.app.services.service_errors import service_error


class SessionRepository(Protocol):
    def get_session_state(self) -> SessionState: ...

    def set_active_workspace_id(self, workspace_id: str) -> SessionState: ...

    def set_active_dataset_id(self, dataset_id: str | None) -> SessionState: ...

    def get_last_active_dataset_id(self, workspace_id: str) -> str | None: ...

    def get_default_dataset_id(self, workspace_id: str) -> str | None: ...


class SessionDatasetRepository(Protocol):
    def get_dataset(self, dataset_id: str) -> DatasetDetail | None: ...

    def list_dataset_details(self) -> Sequence[DatasetDetail]: ...


class SessionService:
    def __init__(
        self,
        repository: SessionRepository,
        dataset_repository: SessionDatasetRepository,
    ) -> None:
        self._repository = repository
        self._dataset_repository = dataset_repository

    def get_session(self) -> AppSession:
        state = self._require_authenticated_session()
        return self._build_session(state)

    def switch_active_workspace(self, workspace_id: str) -> WorkspaceSwitchResult:
        current_state = self._require_authenticated_session()
        target_membership = _membership_for_workspace(current_state, workspace_id)
        if target_membership is None:
            raise service_error(
                403,
                code="workspace_membership_required",
                category="permission_denied",
                message="The requested workspace is not available to the current session.",
            )

        previous_dataset_id = current_state.active_dataset_id
        switched_state = self._repository.set_active_workspace_id(workspace_id)
        resolved_dataset_id, resolution = self._resolve_workspace_dataset(
            state=switched_state,
            previous_dataset_id=previous_dataset_id,
        )
        final_state = self._repository.set_active_dataset_id(resolved_dataset_id)
        return WorkspaceSwitchResult(
            session=self._build_session(final_state),
            active_dataset_resolution=resolution,
            detached_task_ids=(),
        )

    def set_active_dataset(self, dataset_id: str | None) -> AppSession:
        state = self._require_authenticated_session()
        if dataset_id is None:
            return self._build_session(self._repository.set_active_dataset_id(None))

        dataset = self._dataset_repository.get_dataset(dataset_id)
        if dataset is None:
            raise service_error(
                404,
                code="dataset_not_found",
                category="not_found",
                message=f"Dataset {dataset_id} was not found.",
            )
        if dataset.lifecycle_state == "archived":
            raise service_error(
                409,
                code="dataset_archived",
                category="conflict",
                message=f"Dataset {dataset_id} is archived and cannot be activated.",
            )
        if not _dataset_is_visible_to_state(dataset, state, workspace_id=state.workspace_id):
            raise service_error(
                403,
                code="dataset_not_visible_in_workspace",
                category="permission_denied",
                message="The selected dataset is not visible in the active workspace.",
            )

        return self._build_session(self._repository.set_active_dataset_id(dataset_id))

    def _resolve_workspace_dataset(
        self,
        *,
        state: SessionState,
        previous_dataset_id: str | None,
    ) -> tuple[str | None, DatasetResolution]:
        if previous_dataset_id is not None:
            previous_dataset = self._dataset_repository.get_dataset(previous_dataset_id)
            if previous_dataset is not None and _dataset_is_visible_to_state(
                previous_dataset,
                state,
                workspace_id=state.workspace_id,
            ):
                return previous_dataset_id, "preserved"

        last_active_dataset_id = self._repository.get_last_active_dataset_id(state.workspace_id)
        if last_active_dataset_id is not None:
            rebound_dataset = self._dataset_repository.get_dataset(last_active_dataset_id)
            if rebound_dataset is not None and _dataset_is_visible_to_state(
                rebound_dataset,
                state,
                workspace_id=state.workspace_id,
            ):
                return last_active_dataset_id, "rebound"

        default_dataset_id = self._repository.get_default_dataset_id(state.workspace_id)
        if default_dataset_id is not None:
            default_dataset = self._dataset_repository.get_dataset(default_dataset_id)
            if default_dataset is not None and _dataset_is_visible_to_state(
                default_dataset,
                state,
                workspace_id=state.workspace_id,
            ):
                return default_dataset_id, "rebound"

        visible_datasets = sorted(
            (
                dataset
                for dataset in self._dataset_repository.list_dataset_details()
                if _dataset_is_visible_to_state(dataset, state, workspace_id=state.workspace_id)
            ),
            key=lambda dataset: dataset.updated_at,
            reverse=True,
        )
        if len(visible_datasets) == 0:
            return None, "cleared"
        return visible_datasets[0].dataset_id, "rebound"

    def _build_session(self, state: SessionState) -> AppSession:
        if state.auth_state != "authenticated" or state.user is None:
            raise service_error(
                401,
                code="auth_required",
                category="auth_required",
                message="The current request requires an authenticated session.",
            )

        membership = _membership_for_workspace(state, state.workspace_id)
        if membership is None:
            raise service_error(
                403,
                code="workspace_membership_required",
                category="permission_denied",
                message="The active workspace is not available to the current session.",
            )

        active_dataset = None
        if state.active_dataset_id is not None:
            dataset = self._dataset_repository.get_dataset(state.active_dataset_id)
            if dataset is None or not _dataset_is_visible_to_state(
                dataset,
                state,
                workspace_id=state.workspace_id,
            ):
                raise service_error(
                    409,
                    code="context_rebind_required",
                    category="conflict",
                    message="Session context must be rebound before continuing.",
                )
            active_dataset = ActiveDatasetContext(
                dataset_id=dataset.dataset_id,
                name=dataset.name,
                family=dataset.family,
                status=dataset.status,
                owner_user_id=dataset.owner_user_id,
                owner_display_name=dataset.owner,
                workspace_id=dataset.workspace_id,
                visibility_scope=dataset.visibility_scope,
                lifecycle_state=dataset.lifecycle_state,
            )

        capabilities = _materialize_capabilities(state, membership)
        return AppSession(
            session_id=state.session_id,
            auth_state=state.auth_state,
            auth_mode=state.auth_mode,
            user=state.user,
            memberships=tuple(
                _with_active_membership_flag(
                    membership_item,
                    state=state,
                )
                for membership_item in state.memberships
            ),
            workspace=WorkspaceContext(
                workspace_id=membership.workspace_id,
                slug=membership.slug,
                display_name=membership.display_name,
                role=membership.role,
                default_task_scope=membership.default_task_scope,
                allowed_actions=membership.allowed_actions,
            ),
            active_dataset=active_dataset,
            capabilities=capabilities,
        )

    def _require_authenticated_session(self) -> SessionState:
        state = self._repository.get_session_state()
        if state.auth_state != "authenticated" or state.user is None:
            raise service_error(
                401,
                code="auth_required",
                category="auth_required",
                message="The current request requires an authenticated session.",
            )
        return state


def _with_active_membership_flag(
    membership: WorkspaceMembership,
    *,
    state: SessionState,
) -> WorkspaceMembership:
    return WorkspaceMembership(
        workspace_id=membership.workspace_id,
        slug=membership.slug,
        display_name=membership.display_name,
        role=membership.role,
        default_task_scope=membership.default_task_scope,
        is_active=membership.workspace_id == state.workspace_id,
        allowed_actions=membership.allowed_actions,
    )


def _membership_for_workspace(
    state: SessionState,
    workspace_id: str,
) -> WorkspaceMembership | None:
    for membership in state.memberships:
        if membership.workspace_id == workspace_id:
            return membership
    return None


def _dataset_is_visible_to_state(
    dataset: DatasetDetail,
    state: SessionState,
    *,
    workspace_id: str,
) -> bool:
    if dataset.workspace_id != workspace_id or dataset.lifecycle_state != "active":
        return False
    if dataset.visibility_scope == "workspace":
        return True
    if state.user is None:
        return False
    if state.user.platform_role == "admin":
        return True
    membership = _membership_for_workspace(state, workspace_id)
    if membership is not None and membership.role == "owner":
        return True
    return dataset.owner_user_id == state.user.user_id


def _materialize_capabilities(
    state: SessionState,
    membership: WorkspaceMembership,
) -> SessionCapabilities:
    is_admin = state.user is not None and state.user.platform_role == "admin"
    is_owner = membership.role == "owner"
    is_member = membership.role == "member"
    return SessionCapabilities(
        can_switch_workspace=len(state.memberships) > 1,
        can_switch_dataset=state.auth_state == "authenticated",
        can_invite_members=is_owner or is_admin,
        can_remove_members=is_owner or is_admin,
        can_transfer_workspace_owner=is_owner or is_admin,
        can_submit_tasks=is_owner or is_member or is_admin,
        can_manage_workspace_tasks=is_owner or is_admin,
        can_manage_definitions=is_owner or is_member or is_admin,
        can_manage_datasets=is_owner or is_member or is_admin,
        can_view_audit_logs=is_owner or is_admin,
    )
