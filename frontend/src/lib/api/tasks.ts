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

export type TaskDetail = TaskSummary & Readonly<{
  queueBackend: "in_memory_scaffold";
  workerTaskName: "simulation_run_task" | "simulation_smoke_task" | "simulation_failure_task" | "simulation_crash_task" | "post_processing_run_task" | "post_processing_smoke_task" | "characterization_run_task" | "characterization_smoke_task" | "characterization_failure_task" | "characterization_crash_task";
  requestReady: boolean;
  submittedFromActiveDataset: boolean;
  progress: Readonly<{
    phase: "queued" | "running" | "completed" | "failed";
    percentComplete: number;
    summary: string;
    updatedAt: string;
  }>;
}>;

export const tasksListKey = "/api/backend/tasks";

export function taskDetailKey(taskId: number) {
  return `/api/backend/tasks/${encodeURIComponent(taskId)}`;
}

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

export function mapTaskDetailResponse(payload: components["schemas"]["TaskDetailResponse"]): TaskDetail {
  return {
    ...mapTaskSummaryResponse(payload),
    queueBackend: payload.queue_backend,
    workerTaskName: payload.worker_task_name,
    requestReady: payload.request_ready,
    submittedFromActiveDataset: payload.submitted_from_active_dataset,
    progress: {
      phase: payload.progress.phase,
      percentComplete: payload.progress.percent_complete,
      summary: payload.progress.summary,
      updatedAt: payload.progress.updated_at,
    },
  };
}

export async function getTask(taskId: number) {
  const response = await apiRequest<components["schemas"]["TaskDetailResponse"]>(taskDetailKey(taskId));
  return mapTaskDetailResponse(response);
}
