import { apiRequest } from "@/lib/api/client";

import { components } from "./generated/schema";

type SessionResponseShape = components["schemas"]["SessionResponse"];


export type SessionSnapshot = Readonly<{
  sessionId: string;
  authState: "authenticated" | "anonymous";
  authMode: "development_stub";
  scopes: readonly string[];
  canSubmitTasks: boolean;
  canManageDatasets: boolean;
  user:
    | Readonly<{
        userId: string;
        displayName: string;
        email: string | null;
      }>
    | null;
  workspace: Readonly<{
    workspaceId: string;
    slug: string;
    displayName: string;
    role: "owner" | "member" | "viewer";
    defaultTaskScope: "workspace" | "owned";
  }>;
  activeDataset:
    | Readonly<{
        datasetId: string;
        name: string;
        family: string;
        status: "Ready" | "Queued" | "Review";
        owner: string;
        accessScope: "workspace" | "shared";
      }>
    | null;
}>;

export const appSessionKey = "/api/backend/session";

export function mapSessionResponse(payload: SessionResponseShape): SessionSnapshot {
  return {
    sessionId: payload.session_id,
    authState: payload.auth.state,
    authMode: payload.auth.mode,
    scopes: [...payload.auth.scopes],
    canSubmitTasks: payload.auth.can_submit_tasks,
    canManageDatasets: payload.auth.can_manage_datasets,
    user: payload.identity
      ? {
          userId: payload.identity.user_id,
          displayName: payload.identity.display_name,
          email: payload.identity.email,
        }
      : null,
    workspace: {
      workspaceId: payload.workspace.workspace_id,
      slug: payload.workspace.slug,
      displayName: payload.workspace.display_name,
      role: payload.workspace.role,
      defaultTaskScope: payload.workspace.default_task_scope,
    },
    activeDataset: payload.workspace.active_dataset
      ? {
          datasetId: payload.workspace.active_dataset.dataset_id,
          name: payload.workspace.active_dataset.name,
          family: payload.workspace.active_dataset.family,
          status: payload.workspace.active_dataset.status,
          owner: payload.workspace.active_dataset.owner,
          accessScope: payload.workspace.active_dataset.access_scope,
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
