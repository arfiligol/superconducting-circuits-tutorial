import { apiRequest } from "@/lib/api/client";

type SessionResponseShape = Readonly<{
  session_id: string;
  auth: Readonly<{
    state: "authenticated" | "anonymous";
    mode: "local_stub";
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
    allowed_actions: Readonly<{
      switch_to: boolean;
      activate_dataset: boolean;
      invite_members: boolean;
      remove_members: boolean;
      transfer_owner: boolean;
    }>;
  }>;
  memberships: ReadonlyArray<
    Readonly<{
      id: string;
      slug: string;
      name: string;
      role: "owner" | "member" | "viewer";
      default_task_scope: "workspace" | "owned";
      is_active: boolean;
      allowed_actions: Readonly<{
        switch_to: boolean;
        activate_dataset: boolean;
        invite_members: boolean;
        remove_members: boolean;
        transfer_owner: boolean;
      }>;
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

export type SessionSnapshot = Readonly<{
  sessionId: string;
  authState: "authenticated" | "anonymous";
  authMode: "local_stub";
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
  }>;
  memberships: ReadonlyArray<
    Readonly<{
      workspaceId: string;
      slug: string;
      displayName: string;
      role: "owner" | "member" | "viewer";
      defaultTaskScope: "workspace" | "owned";
      isActive: boolean;
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

export const appSessionKey = "/api/backend/session";

export function mapSessionResponse(payload: SessionResponseShape): SessionSnapshot {
  return {
    sessionId: payload.session_id,
    authState: payload.auth.state,
    authMode: payload.auth.mode,
    canSubmitTasks: payload.capabilities.can_submit_tasks,
    canManageDatasets: payload.capabilities.can_manage_datasets,
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
    },
    memberships: payload.memberships.map((membership) => ({
      workspaceId: membership.id,
      slug: membership.slug,
      displayName: membership.name,
      role: membership.role,
      defaultTaskScope: membership.default_task_scope,
      isActive: membership.is_active,
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

export async function getSession() {
  const response = await apiRequest<SessionResponseShape>(appSessionKey);
  return mapSessionResponse(response);
}

export async function patchActiveDataset(datasetId: string | null) {
  const response = await apiRequest<SessionResponseShape>(`${appSessionKey}/active-dataset`, {
    method: "PATCH",
    body: { dataset_id: datasetId },
  });

  return mapSessionResponse(response);
}
