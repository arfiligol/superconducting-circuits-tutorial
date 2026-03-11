import { apiRequest } from "@/lib/api/client";

type TaskSummaryResponseShape = Readonly<{
  task_id: number;
  kind: "simulation" | "post_processing" | "characterization";
  lane: "simulation" | "characterization";
  status: "queued" | "running" | "completed" | "failed";
  submitted_at: string;
  submitted_by: string;
  dataset_id: string | null;
  definition_id: number | null;
  summary: string;
}>;

export type TaskSummary = Readonly<{
  taskId: number;
  kind: "simulation" | "post_processing" | "characterization";
  lane: "simulation" | "characterization";
  status: "queued" | "running" | "completed" | "failed";
  submittedAt: string;
  submittedBy: string;
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
    status: payload.status,
    submittedAt: payload.submitted_at,
    submittedBy: payload.submitted_by,
    datasetId: payload.dataset_id,
    definitionId: payload.definition_id,
    summary: payload.summary,
  };
}

export async function listTasks() {
  const response = await apiRequest<TaskSummaryResponseShape[]>(tasksListKey);
  return response.map(mapTaskSummaryResponse);
}
