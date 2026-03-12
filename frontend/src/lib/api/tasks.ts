import { apiRequest } from "@/lib/api/client";

import { components } from "./generated/schema";

type TaskSummaryResponseShape = components["schemas"]["TaskSummaryResponse"];


export type TaskSummary = Readonly<{
  taskId: number;
  kind: "simulation" | "post_processing" | "characterization";
  lane: "simulation" | "characterization";
  executionMode: "run" | "smoke";
  status: "queued" | "running" | "completed" | "failed";
  submittedAt: string;
  ownerUserId: string;
  ownerDisplayName: string;
  workspaceId: string;
  workspaceSlug: string;
  visibilityScope: "workspace" | "owned";
  datasetId: string | null;
  definitionId: number | null;
  summary: string;
}>;

export const tasksListKey = "/api/backend/tasks";

export function mapTaskSummaryResponse(payload: TaskSummaryResponseShape): TaskSummary {
  return {
    taskId: payload.task_id,
    kind: payload.kind,
    lane: payload.lane,
    executionMode: payload.execution_mode,
    status: payload.status,
    submittedAt: payload.submitted_at,
    ownerUserId: payload.owner_user_id,
    ownerDisplayName: payload.owner_display_name,
    workspaceId: payload.workspace_id,
    workspaceSlug: payload.workspace_slug,
    visibilityScope: payload.visibility_scope,
    datasetId: payload.dataset_id,
    definitionId: payload.definition_id,
    summary: payload.summary,
  };
}

export async function listTasks() {
  const response = await apiRequest<TaskSummaryResponseShape[]>(tasksListKey);
  return response.map(mapTaskSummaryResponse);
}
