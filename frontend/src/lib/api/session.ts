import { apiRequest } from "@/lib/api/client";

export type SessionAuthState = "authenticated" | "anonymous" | "degraded";
export type SessionAuthMode = "local_stub" | "development_stub" | "jwt_cookie";

type AllowedActionsResponseShape = Readonly<{
  switch_to: boolean;
  activate_dataset: boolean;
  invite_members: boolean;
  remove_members: boolean;
  transfer_owner: boolean;
}>;

type SessionResponseShape = Readonly<{
  session_id: string;
  auth: Readonly<{
    state: SessionAuthState;
    mode: SessionAuthMode;
  }>;
  user:
    | Readonly<{
        id: string;
        display_name: string;
        email: string | null;
        platform_role: "admin" | "user";
      }>
    | null;
  workspace: Readonly<{
    id: string;
    slug: string;
    name: string;
    role: "owner" | "member" | "viewer";
    default_task_scope: "workspace" | "owned";
    allowed_actions: AllowedActionsResponseShape;
  }>;
  memberships: ReadonlyArray<
    Readonly<{
      id: string;
      slug: string;
      name: string;
      role: "owner" | "member" | "viewer";
      default_task_scope: "workspace" | "owned";
      is_active: boolean;
      allowed_actions: AllowedActionsResponseShape;
    }>
  >;
  active_dataset:
    | Readonly<{
        id: string;
        name: string;
        family: string;
        status: "Ready" | "Queued" | "Review";
        owner_user_id: string;
        owner_display_name: string;
        workspace_id: string;
        visibility_scope: "private" | "workspace";
        lifecycle_state: "active" | "archived" | "deleted";
      }>
    | null;
  capabilities: Readonly<{
    can_switch_workspace: boolean;
    can_switch_dataset: boolean;
    can_invite_members: boolean;
    can_remove_members: boolean;
    can_transfer_workspace_owner: boolean;
    can_submit_tasks: boolean;
    can_manage_workspace_tasks: boolean;
    can_manage_definitions: boolean;
    can_manage_datasets: boolean;
    can_view_audit_logs: boolean;
  }>;
}>;

type WorkspaceSwitchResponseShape = SessionResponseShape &
  Readonly<{
    active_dataset_resolution: "preserved" | "rebound" | "cleared";
    detached_task_ids: readonly string[];
  }>;

export type SessionAllowedActions = Readonly<{
  switchTo: boolean;
  activateDataset: boolean;
  inviteMembers: boolean;
  removeMembers: boolean;
  transferOwner: boolean;
}>;

export type SessionCapabilities = Readonly<{
  canSwitchWorkspace: boolean;
  canSwitchDataset: boolean;
  canInviteMembers: boolean;
  canRemoveMembers: boolean;
  canTransferWorkspaceOwner: boolean;
  canSubmitTasks: boolean;
  canManageWorkspaceTasks: boolean;
  canManageDefinitions: boolean;
  canManageDatasets: boolean;
  canViewAuditLogs: boolean;
}>;

export type SessionSnapshot = Readonly<{
  sessionId: string;
  authState: SessionAuthState;
  authMode: SessionAuthMode;
  capabilities: SessionCapabilities;
  canSubmitTasks: boolean;
  canManageDatasets: boolean;
  user:
    | Readonly<{
        userId: string;
        displayName: string;
        email: string | null;
        platformRole: "admin" | "user";
      }>
    | null;
  workspace: Readonly<{
    workspaceId: string;
    slug: string;
    displayName: string;
    role: "owner" | "member" | "viewer";
    defaultTaskScope: "workspace" | "owned";
    allowedActions: SessionAllowedActions;
  }>;
  memberships: ReadonlyArray<
    Readonly<{
      workspaceId: string;
      slug: string;
      displayName: string;
      role: "owner" | "member" | "viewer";
      defaultTaskScope: "workspace" | "owned";
      isActive: boolean;
      allowedActions: SessionAllowedActions;
    }>
  >;
  activeDataset:
    | Readonly<{
        datasetId: string;
        name: string;
        family: string;
        status: "Ready" | "Queued" | "Review";
        ownerUserId: string;
        owner: string;
        workspaceId: string;
        visibilityScope: "private" | "workspace";
        lifecycleState: "active" | "archived" | "deleted";
      }>
    | null;
}>;

export type WorkspaceSwitchResult = Readonly<{
  session: SessionSnapshot;
  activeDatasetResolution: "preserved" | "rebound" | "cleared";
  detachedTaskIds: readonly string[];
}>;

export const appSessionKey = "/api/backend/session";

function mapAllowedActions(payload: AllowedActionsResponseShape): SessionAllowedActions {
  return {
    switchTo: payload.switch_to,
    activateDataset: payload.activate_dataset,
    inviteMembers: payload.invite_members,
    removeMembers: payload.remove_members,
    transferOwner: payload.transfer_owner,
  };
}

export function mapSessionResponse(payload: SessionResponseShape): SessionSnapshot {
  const capabilities: SessionCapabilities = {
    canSwitchWorkspace: payload.capabilities.can_switch_workspace,
    canSwitchDataset: payload.capabilities.can_switch_dataset,
    canInviteMembers: payload.capabilities.can_invite_members,
    canRemoveMembers: payload.capabilities.can_remove_members,
    canTransferWorkspaceOwner: payload.capabilities.can_transfer_workspace_owner,
    canSubmitTasks: payload.capabilities.can_submit_tasks,
    canManageWorkspaceTasks: payload.capabilities.can_manage_workspace_tasks,
    canManageDefinitions: payload.capabilities.can_manage_definitions,
    canManageDatasets: payload.capabilities.can_manage_datasets,
    canViewAuditLogs: payload.capabilities.can_view_audit_logs,
  };

  return {
    sessionId: payload.session_id,
    authState: payload.auth.state,
    authMode: payload.auth.mode,
    capabilities,
    canSubmitTasks: capabilities.canSubmitTasks,
    canManageDatasets: capabilities.canManageDatasets,
    user: payload.user
      ? {
          userId: payload.user.id,
          displayName: payload.user.display_name,
          email: payload.user.email,
          platformRole: payload.user.platform_role,
        }
      : null,
    workspace: {
      workspaceId: payload.workspace.id,
      slug: payload.workspace.slug,
      displayName: payload.workspace.name,
      role: payload.workspace.role,
      defaultTaskScope: payload.workspace.default_task_scope,
      allowedActions: mapAllowedActions(payload.workspace.allowed_actions),
    },
    memberships: payload.memberships.map((membership) => ({
      workspaceId: membership.id,
      slug: membership.slug,
      displayName: membership.name,
      role: membership.role,
      defaultTaskScope: membership.default_task_scope,
      isActive: membership.is_active,
      allowedActions: mapAllowedActions(membership.allowed_actions),
    })),
    activeDataset: payload.active_dataset
      ? {
          datasetId: payload.active_dataset.id,
          name: payload.active_dataset.name,
          family: payload.active_dataset.family,
          status: payload.active_dataset.status,
          ownerUserId: payload.active_dataset.owner_user_id,
          owner: payload.active_dataset.owner_display_name,
          workspaceId: payload.active_dataset.workspace_id,
          visibilityScope: payload.active_dataset.visibility_scope,
          lifecycleState: payload.active_dataset.lifecycle_state,
        }
      : null,
  };
}

export function mapWorkspaceSwitchResponse(
  payload: WorkspaceSwitchResponseShape,
): WorkspaceSwitchResult {
  return {
    session: mapSessionResponse(payload),
    activeDatasetResolution: payload.active_dataset_resolution,
    detachedTaskIds: [...payload.detached_task_ids],
  };
}

export async function getSession() {
  const response = await apiRequest<SessionResponseShape>(appSessionKey);
  return mapSessionResponse(response);
}

export async function patchActiveWorkspace(workspaceId: string) {
  const response = await apiRequest<WorkspaceSwitchResponseShape>(
    `${appSessionKey}/active-workspace`,
    {
      method: "PATCH",
      body: { workspace_id: workspaceId },
    },
  );

  return mapWorkspaceSwitchResponse(response);
}

export async function patchActiveDataset(datasetId: string | null) {
  const response = await apiRequest<SessionResponseShape>(`${appSessionKey}/active-dataset`, {
    method: "PATCH",
    body: { dataset_id: datasetId },
  });

  return mapSessionResponse(response);
}
