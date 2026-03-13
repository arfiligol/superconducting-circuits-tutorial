import type { TaskDetail, TaskResultHandleRef } from "@/lib/api/tasks";

type SurfaceTone = "default" | "primary" | "success" | "warning";

export type TaskConnectionState = Readonly<{
  mode: "none" | "latest" | "explicit";
  latestTaskId: number | null;
  selectedTaskId: number | null;
  attachedTaskId: number | null;
  hasNewerLatestTask: boolean;
  isFollowingLatest: boolean;
  isAttached: boolean;
  isStaleSnapshot: boolean;
}>;

export type TaskRecoveryNotice = Readonly<{
  tone: "warning";
  title: string;
  message: string;
}> | null;

export type TaskLifecycleSummary = Readonly<{
  stage: "idle" | "accepted" | "running" | "completed" | "failed";
  statusLabel: string;
  tone: SurfaceTone;
  summary: string;
  progressPercent: number;
  progressSummary: string;
  backendStatusLabel: string;
  workerTaskName: string | null;
  submissionSourceLabel: string | null;
  acceptedAt: string | null;
  lastUpdatedAt: string | null;
  taskDatasetId: string | null;
  dispatchKey: string | null;
  requestReady: boolean;
  submittedFromActiveDataset: boolean;
  executionMode: TaskDetail["executionMode"] | null;
  visibilityScope: TaskDetail["visibilityScope"] | null;
}>;

export type TaskResultSurfaceSummary = Readonly<{
  metadataRecordCount: number;
  resultHandleCount: number;
  materializedHandleCount: number;
  pendingHandleCount: number;
  hasTracePayload: boolean;
  traceBatchId: number | null;
  analysisRunId: number | null;
  handleKindCounts: readonly Readonly<{
    kind: TaskResultHandleRef["kind"];
    count: number;
  }>[];
}>;

export type TaskResultHandleGroups = Readonly<{
  materialized: readonly TaskResultHandleRef[];
  pending: readonly TaskResultHandleRef[];
}>;

function formatSubmissionSourceLabel(
  source: TaskDetail["dispatch"]["submissionSource"],
): string {
  switch (source) {
    case "active_dataset":
      return "Active dataset session";
    case "explicit_dataset":
      return "Explicit dataset binding";
    case "definition_only":
      return "Definition-only dispatch";
    default:
      return source;
  }
}

export function formatTaskConnectionModeLabel(mode: TaskConnectionState["mode"]) {
  switch (mode) {
    case "explicit":
      return "Explicit attachment";
    case "latest":
      return "Follow latest";
    case "none":
    default:
      return "No task available";
  }
}

export function resolveTaskConnectionState(input: Readonly<{
  requestedTaskId: number | null;
  resolvedTaskId: number | null;
  latestTaskId: number | null;
  activeTask: TaskDetail | undefined;
}>): TaskConnectionState {
  const attachedTaskId = input.activeTask?.taskId ?? null;

  if (input.resolvedTaskId === null && input.latestTaskId === null) {
    return {
      mode: "none",
      latestTaskId: null,
      selectedTaskId: null,
      attachedTaskId,
      hasNewerLatestTask: false,
      isFollowingLatest: false,
      isAttached: false,
      isStaleSnapshot: false,
    };
  }

  const mode = input.requestedTaskId === null ? "latest" : "explicit";
  const isAttached =
    attachedTaskId !== null &&
    input.resolvedTaskId !== null &&
    attachedTaskId === input.resolvedTaskId;
  const isStaleSnapshot =
    attachedTaskId !== null &&
    input.resolvedTaskId !== null &&
    attachedTaskId !== input.resolvedTaskId;

  return {
    mode,
    latestTaskId: input.latestTaskId,
    selectedTaskId: input.resolvedTaskId,
    attachedTaskId,
    hasNewerLatestTask:
      input.latestTaskId !== null &&
      input.resolvedTaskId !== null &&
      input.latestTaskId !== input.resolvedTaskId,
    isFollowingLatest:
      input.requestedTaskId === null &&
      input.latestTaskId !== null &&
      input.resolvedTaskId === input.latestTaskId,
    isAttached,
    isStaleSnapshot,
  };
}

export function resolveTaskRecoveryNotice(
  requestedTaskId: number | null,
  latestTaskId: number | null,
  activeTaskError: Error | undefined,
): TaskRecoveryNotice {
  if (requestedTaskId === null || !activeTaskError) {
    return null;
  }

  if (latestTaskId !== null && latestTaskId !== requestedTaskId) {
    return {
      tone: "warning",
      title: "Task reattach available",
      message: `Task #${requestedTaskId} could not be attached. A newer task #${latestTaskId} is available instead.`,
    };
  }

  return {
    tone: "warning",
    title: "Task unavailable",
    message: `Task #${requestedTaskId} could not be attached. Refresh the task queue or submit a new request.`,
  };
}

export function summarizeTaskLifecycle(
  task: TaskDetail | undefined,
): TaskLifecycleSummary {
  if (!task) {
    return {
      stage: "idle",
      statusLabel: "Idle",
      tone: "default",
      summary:
        "Attach a task to inspect persisted dispatch state, progress, and backend execution metadata.",
      progressPercent: 0,
      progressSummary: "Select or submit a task to inspect its persisted execution state.",
      backendStatusLabel: "pending",
      workerTaskName: null,
      submissionSourceLabel: null,
      acceptedAt: null,
      lastUpdatedAt: null,
      taskDatasetId: null,
      dispatchKey: null,
      requestReady: false,
      submittedFromActiveDataset: false,
      executionMode: null,
      visibilityScope: null,
    };
  }

  const stage =
    task.dispatch.status === "failed" || task.status === "failed" || task.progress.phase === "failed"
      ? "failed"
      : task.dispatch.status === "completed" ||
          task.status === "completed" ||
          task.progress.phase === "completed"
        ? "completed"
        : task.dispatch.status === "running" ||
            task.status === "running" ||
            task.progress.phase === "running"
          ? "running"
          : "accepted";

  if (stage === "failed") {
    return {
      stage,
      statusLabel: "Dispatch failed",
      tone: "warning",
      summary:
        "The backend accepted the request but execution failed. Persisted dispatch, events, and result refs still anchor recovery.",
      progressPercent: task.progress.percentComplete,
      progressSummary: task.progress.summary,
      backendStatusLabel: task.status,
      workerTaskName: task.workerTaskName,
      submissionSourceLabel: formatSubmissionSourceLabel(task.dispatch.submissionSource),
      acceptedAt: task.dispatch.acceptedAt,
      lastUpdatedAt: task.dispatch.lastUpdatedAt,
      taskDatasetId: task.datasetId,
      dispatchKey: task.dispatch.dispatchKey,
      requestReady: task.requestReady,
      submittedFromActiveDataset: task.submittedFromActiveDataset,
      executionMode: task.executionMode,
      visibilityScope: task.visibilityScope,
    };
  }

  if (stage === "completed") {
    return {
      stage,
      statusLabel: "Dispatch completed",
      tone: "success",
      summary:
        "The task completed. Persisted result handles, metadata records, and event history can be reattached after refresh.",
      progressPercent: task.progress.percentComplete,
      progressSummary: task.progress.summary,
      backendStatusLabel: task.status,
      workerTaskName: task.workerTaskName,
      submissionSourceLabel: formatSubmissionSourceLabel(task.dispatch.submissionSource),
      acceptedAt: task.dispatch.acceptedAt,
      lastUpdatedAt: task.dispatch.lastUpdatedAt,
      taskDatasetId: task.datasetId,
      dispatchKey: task.dispatch.dispatchKey,
      requestReady: task.requestReady,
      submittedFromActiveDataset: task.submittedFromActiveDataset,
      executionMode: task.executionMode,
      visibilityScope: task.visibilityScope,
    };
  }

  if (stage === "running") {
    return {
      stage,
      statusLabel: "Dispatch running",
      tone: "primary",
      summary:
        "Worker execution is active. Progress, events, and result refs remain recoverable from the persisted task contract.",
      progressPercent: task.progress.percentComplete,
      progressSummary: task.progress.summary,
      backendStatusLabel: task.status,
      workerTaskName: task.workerTaskName,
      submissionSourceLabel: formatSubmissionSourceLabel(task.dispatch.submissionSource),
      acceptedAt: task.dispatch.acceptedAt,
      lastUpdatedAt: task.dispatch.lastUpdatedAt,
      taskDatasetId: task.datasetId,
      dispatchKey: task.dispatch.dispatchKey,
      requestReady: task.requestReady,
      submittedFromActiveDataset: task.submittedFromActiveDataset,
      executionMode: task.executionMode,
      visibilityScope: task.visibilityScope,
    };
  }

  return {
    stage,
    statusLabel: "Dispatch accepted",
    tone: "primary",
    summary:
      "The request is queued and ready to be reattached once worker execution advances.",
    progressPercent: task.progress.percentComplete,
    progressSummary: task.progress.summary,
    backendStatusLabel: task.status,
    workerTaskName: task.workerTaskName,
    submissionSourceLabel: formatSubmissionSourceLabel(task.dispatch.submissionSource),
    acceptedAt: task.dispatch.acceptedAt,
    lastUpdatedAt: task.dispatch.lastUpdatedAt,
    taskDatasetId: task.datasetId,
    dispatchKey: task.dispatch.dispatchKey,
    requestReady: task.requestReady,
    submittedFromActiveDataset: task.submittedFromActiveDataset,
    executionMode: task.executionMode,
    visibilityScope: task.visibilityScope,
  };
}

export function groupTaskResultHandles(
  task: TaskDetail | undefined,
): TaskResultHandleGroups {
  const handles = task?.resultRefs.resultHandles ?? [];

  return {
    materialized: handles.filter((handle) => handle.status === "materialized"),
    pending: handles.filter((handle) => handle.status !== "materialized"),
  };
}

export function summarizeTaskResultSurface(
  task: TaskDetail | undefined,
): TaskResultSurfaceSummary {
  const handles = task?.resultRefs.resultHandles ?? [];
  const countsByKind = new Map<TaskResultHandleRef["kind"], number>();

  for (const handle of handles) {
    countsByKind.set(handle.kind, (countsByKind.get(handle.kind) ?? 0) + 1);
  }

  return {
    metadataRecordCount: task?.resultRefs.metadataRecords.length ?? 0,
    resultHandleCount: handles.length,
    materializedHandleCount: handles.filter((handle) => handle.status === "materialized").length,
    pendingHandleCount: handles.filter((handle) => handle.status !== "materialized").length,
    hasTracePayload: task?.resultRefs.tracePayload != null,
    traceBatchId: task?.resultRefs.traceBatchId ?? null,
    analysisRunId: task?.resultRefs.analysisRunId ?? null,
    handleKindCounts: [...countsByKind.entries()]
      .map(([kind, count]) => ({ kind, count }))
      .sort((left, right) => right.count - left.count || left.kind.localeCompare(right.kind)),
  };
}
