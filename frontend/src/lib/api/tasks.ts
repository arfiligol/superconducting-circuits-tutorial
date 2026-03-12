import { apiRequest } from "@/lib/api/client";

import { components } from "./generated/schema";

type TaskSummaryResponseShape = components["schemas"]["TaskSummaryResponse"];
type TaskDetailResponseShape = components["schemas"]["TaskDetailResponse"];

export type TaskMetadataRecordRef = Readonly<{
  backend: "sqlite_metadata";
  recordType: "dataset" | "trace_batch" | "analysis_run" | "result_handle";
  recordId: string;
  version: number;
  schemaVersion: string;
}>;

export type TaskTracePayloadRef = Readonly<{
  contractVersion: string;
  backend: "local_zarr" | "s3_zarr";
  payloadRole: "dataset_primary" | "task_output" | "analysis_projection";
  storeKey: string;
  storeUri: string;
  groupPath: string;
  arrayPath: string;
  dtype: string;
  shape: readonly number[];
  chunkShape: readonly number[];
  schemaVersion: string;
}>;

export type TaskResultHandleRef = Readonly<{
  contractVersion: string;
  handleId: string;
  kind: "simulation_trace" | "fit_summary" | "characterization_report" | "plot_bundle";
  status: "pending" | "materialized";
  label: string;
  metadataRecord: TaskMetadataRecordRef;
  payloadBackend:
    | "local_zarr"
    | "json_artifact"
    | "markdown_artifact"
    | "bundle_archive"
    | null;
  payloadFormat: "zarr" | "json" | "markdown" | "zip" | null;
  payloadRole: "trace_payload" | "report_artifact" | "bundle_artifact" | null;
  payloadLocator: string | null;
  provenanceTaskId: number | null;
  provenance: Readonly<{
    sourceDatasetId: string | null;
    sourceTaskId: number | null;
    traceBatchRecord: TaskMetadataRecordRef | null;
    analysisRunRecord: TaskMetadataRecordRef | null;
  }>;
}>;

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

export type TaskDetail = TaskSummary &
  Readonly<{
    queueBackend: "in_memory_scaffold";
    workerTaskName:
      | "simulation_run_task"
      | "simulation_smoke_task"
      | "simulation_failure_task"
      | "simulation_crash_task"
      | "post_processing_run_task"
      | "post_processing_smoke_task"
      | "characterization_run_task"
      | "characterization_smoke_task"
      | "characterization_failure_task"
      | "characterization_crash_task";
    requestReady: boolean;
    submittedFromActiveDataset: boolean;
    progress: Readonly<{
      phase: "queued" | "running" | "completed" | "failed";
      percentComplete: number;
      summary: string;
      updatedAt: string;
    }>;
    resultRefs: Readonly<{
      traceBatchId: number | null;
      analysisRunId: number | null;
      metadataRecords: readonly TaskMetadataRecordRef[];
      tracePayload: TaskTracePayloadRef | null;
      resultHandles: readonly TaskResultHandleRef[];
    }>;
  }>;

export type TaskSubmissionDraft = components["schemas"]["TaskSubmissionRequest"];
export type TaskMutationResponse = components["schemas"]["TaskMutationResponse"];

export const tasksListKey = "/api/backend/tasks";

export function taskDetailKey(taskId: number) {
  return `/api/backend/tasks/${encodeURIComponent(taskId)}`;
}

function mapMetadataRecordRef(
  payload: components["schemas"]["MetadataRecordRefResponse"],
): TaskMetadataRecordRef {
  return {
    backend: payload.backend,
    recordType: payload.record_type,
    recordId: payload.record_id,
    version: payload.version,
    schemaVersion: payload.schema_version,
  };
}

function mapTracePayloadRef(
  payload: components["schemas"]["TracePayloadRefResponse"],
): TaskTracePayloadRef {
  return {
    contractVersion: payload.contract_version,
    backend: payload.backend,
    payloadRole: payload.payload_role,
    storeKey: payload.store_key,
    storeUri: payload.store_uri,
    groupPath: payload.group_path,
    arrayPath: payload.array_path,
    dtype: payload.dtype,
    shape: [...payload.shape],
    chunkShape: [...payload.chunk_shape],
    schemaVersion: payload.schema_version,
  };
}

function mapResultHandleRef(
  payload: components["schemas"]["ResultHandleRefResponse"],
): TaskResultHandleRef {
  return {
    contractVersion: payload.contract_version,
    handleId: payload.handle_id,
    kind: payload.kind,
    status: payload.status,
    label: payload.label,
    metadataRecord: mapMetadataRecordRef(payload.metadata_record),
    payloadBackend: payload.payload_backend,
    payloadFormat: payload.payload_format,
    payloadRole: payload.payload_role,
    payloadLocator: payload.payload_locator,
    provenanceTaskId: payload.provenance_task_id,
    provenance: {
      sourceDatasetId: payload.provenance.source_dataset_id,
      sourceTaskId: payload.provenance.source_task_id,
      traceBatchRecord: payload.provenance.trace_batch_record
        ? mapMetadataRecordRef(payload.provenance.trace_batch_record)
        : null,
      analysisRunRecord: payload.provenance.analysis_run_record
        ? mapMetadataRecordRef(payload.provenance.analysis_run_record)
        : null,
    },
  };
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

export function mapTaskDetailResponse(payload: TaskDetailResponseShape): TaskDetail {
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
    resultRefs: {
      traceBatchId: payload.result_refs.trace_batch_id,
      analysisRunId: payload.result_refs.analysis_run_id,
      metadataRecords: payload.result_refs.metadata_records.map(mapMetadataRecordRef),
      tracePayload: payload.result_refs.trace_payload
        ? mapTracePayloadRef(payload.result_refs.trace_payload)
        : null,
      resultHandles: payload.result_refs.result_handles.map(mapResultHandleRef),
    },
  };
}

export async function getTask(taskId: number) {
  const response = await apiRequest<TaskDetailResponseShape>(taskDetailKey(taskId));
  return mapTaskDetailResponse(response);
}

export function unwrapTaskMutation(response: TaskMutationResponse): TaskDetail {
  return mapTaskDetailResponse(response.task);
}

export async function submitTask(payload: TaskSubmissionDraft) {
  const response = await apiRequest<TaskMutationResponse>(tasksListKey, {
    method: "POST",
    body: payload,
  });

  return unwrapTaskMutation(response);
}
