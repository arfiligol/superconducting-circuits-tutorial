import { apiRequest } from "@/lib/api/client";

type SessionResponseShape = Readonly<{
  session_id: string;
  auth: Readonly<{
    state: "authenticated" | "anonymous";
    mode: "development_stub";
    scopes: readonly string[];
    can_submit_tasks: boolean;
    can_manage_datasets: boolean;
    user: Readonly<{
      user_id: string;
      display_name: string;
      email: string | null;
    }> | null;
  }>;
  active_dataset: Readonly<{
    dataset_id: string;
    name: string;
    family: string;
    status: "Ready" | "Queued" | "Review";
  }> | null;
}>;

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
  activeDataset:
    | Readonly<{
        datasetId: string;
        name: string;
        family: string;
        status: "Ready" | "Queued" | "Review";
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
    user: payload.auth.user
      ? {
          userId: payload.auth.user.user_id,
          displayName: payload.auth.user.display_name,
          email: payload.auth.user.email,
        }
      : null,
    activeDataset: payload.active_dataset
      ? {
          datasetId: payload.active_dataset.dataset_id,
          name: payload.active_dataset.name,
          family: payload.active_dataset.family,
          status: payload.active_dataset.status,
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
