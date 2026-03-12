import type { TaskDetail, TaskResultHandleRef, TaskSummary } from "@/lib/api/tasks";

export type CharacterizationTaskScope = "dataset" | "all";
export type CharacterizationTaskStatusFilter = "all" | "active" | "completed" | "failed";

export type CharacterizationSelectionRecovery = Readonly<{
  tone: "default" | "warning";
  title: string;
  message: string;
}> | null;

export type CharacterizationTaskSummary = Readonly<{
  total: number;
  activeCount: number;
  completedCount: number;
  failedCount: number;
  resultBackedCount: number;
}>;

export type CharacterizationTaskAttachmentState = Readonly<{
  isAttached: boolean;
  isStaleSnapshot: boolean;
}>;

export type CharacterizationTaskConnectionState = Readonly<{
  mode: "none" | "latest" | "explicit";
  latestTaskId: number | null;
  selectedTaskId: number | null;
  attachedTaskId: number | null;
  hasNewerLatestTask: boolean;
  isFollowingLatest: boolean;
}>;

export type CharacterizationDispatchSummary = Readonly<{
  stage: "idle" | "accepted" | "running" | "completed" | "failed";
  statusLabel: string;
  tone: "default" | "primary" | "success" | "warning";
  summary: string;
  submissionSourceLabel: string | null;
  acceptedAt: string | null;
  lastUpdatedAt: string | null;
}>;

export type CharacterizationTaskResultSummary = Readonly<{
  metadataRecordCount: number;
  resultHandleCount: number;
  materializedHandleCount: number;
  pendingHandleCount: number;
  reportHandleCount: number;
  fitSummaryCount: number;
  plotBundleCount: number;
  hasTracePayload: boolean;
  traceBatchId: number | null;
  analysisRunId: number | null;
}>;

export type CharacterizationResultHandleGroups = Readonly<{
  materialized: readonly TaskResultHandleRef[];
  pending: readonly TaskResultHandleRef[];
}>;

type FilterCharacterizationTasksOptions = Readonly<{
  searchQuery: string;
  scope: CharacterizationTaskScope;
  statusFilter: CharacterizationTaskStatusFilter;
  activeDatasetId: string | null;
}>;

function isCharacterizationTask(task: TaskSummary) {
  return task.kind === "characterization" || task.lane === "characterization";
}

function isActiveTask(task: TaskSummary) {
  return task.status === "queued" || task.status === "running";
}

function matchesTaskStatus(
  task: TaskSummary,
  statusFilter: CharacterizationTaskStatusFilter,
) {
  switch (statusFilter) {
    case "active":
      return isActiveTask(task);
    case "completed":
      return task.status === "completed";
    case "failed":
      return task.status === "failed";
    case "all":
    default:
      return true;
  }
}

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

export function buildCharacterizationRequestSummary(input: Readonly<{
  datasetId: string | null;
  datasetName: string | null;
  note: string;
}>) {
  const segments = [
    input.datasetName
      ? `Characterization request for ${input.datasetName}`
      : `Characterization request for dataset ${input.datasetId ?? "unbound"}`,
  ];

  if (input.note.trim().length > 0) {
    segments.push(input.note.trim());
  }

  return segments.join(" · ");
}

export function resolveLatestCharacterizationTask(
  tasks: readonly TaskSummary[],
): TaskSummary | undefined {
  const characterizationTasks = tasks.filter(isCharacterizationTask);
  return characterizationTasks.find(isActiveTask) ?? characterizationTasks[0];
}

export function filterCharacterizationTasks(
  tasks: readonly TaskSummary[],
  options: FilterCharacterizationTasksOptions,
) {
  const normalizedQuery = options.searchQuery.trim().toLowerCase();

  return tasks.filter((task) => {
    if (!isCharacterizationTask(task)) {
      return false;
    }

    if (
      options.scope === "dataset" &&
      options.activeDatasetId !== null &&
      task.datasetId !== options.activeDatasetId
    ) {
      return false;
    }

    if (!matchesTaskStatus(task, options.statusFilter)) {
      return false;
    }

    if (!normalizedQuery) {
      return true;
    }

    return (
      task.summary.toLowerCase().includes(normalizedQuery) ||
      String(task.taskId).includes(normalizedQuery) ||
      (task.datasetId?.toLowerCase().includes(normalizedQuery) ?? false)
    );
  });
}

export function summarizeCharacterizationTasks(
  tasks: readonly TaskSummary[],
): CharacterizationTaskSummary {
  return tasks.reduce<CharacterizationTaskSummary>(
    (summary, task) => ({
      total: summary.total + 1,
      activeCount: summary.activeCount + (isActiveTask(task) ? 1 : 0),
      completedCount: summary.completedCount + (task.status === "completed" ? 1 : 0),
      failedCount: summary.failedCount + (task.status === "failed" ? 1 : 0),
      resultBackedCount:
        summary.resultBackedCount + (task.status === "completed" ? 1 : 0),
    }),
    {
      total: 0,
      activeCount: 0,
      completedCount: 0,
      failedCount: 0,
      resultBackedCount: 0,
    },
  );
}

export function resolveCharacterizationTaskAttachmentState(
  activeTask: TaskDetail | undefined,
  resolvedTaskId: number | null,
): CharacterizationTaskAttachmentState {
  if (resolvedTaskId === null) {
    return {
      isAttached: false,
      isStaleSnapshot: false,
    };
  }

  return {
    isAttached: activeTask?.taskId === resolvedTaskId,
    isStaleSnapshot:
      typeof activeTask?.taskId === "number" && activeTask.taskId !== resolvedTaskId,
  };
}

export function resolveCharacterizationTaskConnectionState(input: Readonly<{
  requestedTaskId: number | null;
  resolvedTaskId: number | null;
  latestTaskId: number | null;
  activeTask: TaskDetail | undefined;
}>): CharacterizationTaskConnectionState {
  if (input.resolvedTaskId === null && input.latestTaskId === null) {
    return {
      mode: "none",
      latestTaskId: null,
      selectedTaskId: null,
      attachedTaskId: input.activeTask?.taskId ?? null,
      hasNewerLatestTask: false,
      isFollowingLatest: false,
    };
  }

  return {
    mode: input.requestedTaskId === null ? "latest" : "explicit",
    latestTaskId: input.latestTaskId,
    selectedTaskId: input.resolvedTaskId,
    attachedTaskId: input.activeTask?.taskId ?? null,
    hasNewerLatestTask:
      input.latestTaskId !== null &&
      input.resolvedTaskId !== null &&
      input.latestTaskId !== input.resolvedTaskId,
    isFollowingLatest:
      input.requestedTaskId === null &&
      input.latestTaskId !== null &&
      input.resolvedTaskId === input.latestTaskId,
  };
}

export function resolveCharacterizationTaskRecovery(
  requestedTaskId: number | null,
  latestTaskId: number | null,
  activeTaskError: Error | undefined,
): CharacterizationSelectionRecovery {
  if (requestedTaskId === null || !activeTaskError) {
    return null;
  }

  if (latestTaskId !== null && latestTaskId !== requestedTaskId) {
    return {
      tone: "warning",
      title: "Task reattach available",
      message: `Task #${requestedTaskId} could not be attached. A newer characterization task #${latestTaskId} is available instead.`,
    };
  }

  return {
    tone: "warning",
    title: "Task unavailable",
    message: `Task #${requestedTaskId} could not be attached. Refresh the queue or submit a new characterization request.`,
  };
}

export function summarizeCharacterizationDispatch(
  task: TaskDetail | undefined,
): CharacterizationDispatchSummary {
  if (!task) {
    return {
      stage: "idle",
      statusLabel: "Idle",
      tone: "default",
      summary: "Attach a characterization task to inspect persisted dispatch state.",
      submissionSourceLabel: null,
      acceptedAt: null,
      lastUpdatedAt: null,
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
        "The backend accepted the characterization request but execution failed. Persisted dispatch and result refs still anchor recovery.",
      submissionSourceLabel: formatSubmissionSourceLabel(task.dispatch.submissionSource),
      acceptedAt: task.dispatch.acceptedAt,
      lastUpdatedAt: task.dispatch.lastUpdatedAt,
    };
  }

  if (stage === "completed") {
    return {
      stage,
      statusLabel: "Dispatch completed",
      tone: "success",
      summary:
        "The characterization task completed. Persisted result handles and analysis records can be reattached after refresh.",
      submissionSourceLabel: formatSubmissionSourceLabel(task.dispatch.submissionSource),
      acceptedAt: task.dispatch.acceptedAt,
      lastUpdatedAt: task.dispatch.lastUpdatedAt,
    };
  }

  if (stage === "running") {
    return {
      stage,
      statusLabel: "Dispatch running",
      tone: "primary",
      summary:
        "The worker is still producing characterization outputs. Progress and result refs remain recoverable from the persisted task contract.",
      submissionSourceLabel: formatSubmissionSourceLabel(task.dispatch.submissionSource),
      acceptedAt: task.dispatch.acceptedAt,
      lastUpdatedAt: task.dispatch.lastUpdatedAt,
    };
  }

  return {
    stage,
    statusLabel: "Dispatch accepted",
    tone: "primary",
    summary:
      "The characterization request is queued and ready to be reattached once worker execution advances.",
    submissionSourceLabel: formatSubmissionSourceLabel(task.dispatch.submissionSource),
    acceptedAt: task.dispatch.acceptedAt,
    lastUpdatedAt: task.dispatch.lastUpdatedAt,
  };
}

export function summarizeCharacterizationTaskResults(
  task: TaskDetail | undefined,
): CharacterizationTaskResultSummary {
  return {
    metadataRecordCount: task?.resultRefs.metadataRecords.length ?? 0,
    resultHandleCount: task?.resultRefs.resultHandles.length ?? 0,
    materializedHandleCount:
      task?.resultRefs.resultHandles.filter((handle) => handle.status === "materialized").length ??
      0,
    pendingHandleCount:
      task?.resultRefs.resultHandles.filter((handle) => handle.status !== "materialized").length ??
      0,
    reportHandleCount:
      task?.resultRefs.resultHandles.filter((handle) => handle.kind === "characterization_report")
        .length ?? 0,
    fitSummaryCount:
      task?.resultRefs.resultHandles.filter((handle) => handle.kind === "fit_summary").length ?? 0,
    plotBundleCount:
      task?.resultRefs.resultHandles.filter((handle) => handle.kind === "plot_bundle").length ?? 0,
    hasTracePayload: task?.resultRefs.tracePayload !== null,
    traceBatchId: task?.resultRefs.traceBatchId ?? null,
    analysisRunId: task?.resultRefs.analysisRunId ?? null,
  };
}

export function groupCharacterizationResultHandles(
  task: TaskDetail | undefined,
): CharacterizationResultHandleGroups {
  const handles = task?.resultRefs.resultHandles ?? [];

  return {
    materialized: handles.filter((handle) => handle.status === "materialized"),
    pending: handles.filter((handle) => handle.status !== "materialized"),
  };
}
