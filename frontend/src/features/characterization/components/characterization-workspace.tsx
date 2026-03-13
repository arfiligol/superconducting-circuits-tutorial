"use client";

import { useState, useTransition } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Play,
  RefreshCcw,
  Search,
} from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { useCharacterizationWorkflowData } from "@/features/characterization/hooks/use-characterization-workflow-data";
import { parseCharacterizationTaskIdParam } from "@/features/characterization/lib/task-id";
import {
  buildCharacterizationRequestSummary,
  filterCharacterizationTasks,
  summarizeCharacterizationTasks,
  type CharacterizationTaskScope,
  type CharacterizationTaskStatusFilter,
} from "@/features/characterization/lib/workflow";
import {
  SurfacePanel,
  SurfaceStat,
  SurfaceTag,
  cx,
} from "@/features/shared/components/surface-kit";
import { TaskEventHistoryPanel } from "@/features/shared/components/task-event-history-panel";
import {
  TaskAttachmentPanel,
  TaskLifecyclePanel,
  TaskResultPanel,
} from "@/features/shared/components/task-workflow-panels";
import { ApiError } from "@/lib/api/client";
import {
  resolveTaskConnectionState,
  resolveTaskRecoveryNotice,
  summarizeTaskLifecycle,
  summarizeTaskResultSurface,
} from "@/lib/task-surface";

const characterizationRequestSchema = z.object({
  summaryNote: z.string().trim().max(180, "Keep the request note within 180 characters."),
});

type CharacterizationRequestValues = z.infer<typeof characterizationRequestSchema>;

const defaultRequestValues: CharacterizationRequestValues = {
  summaryNote: "",
};

function buildCharacterizationSearchHref(
  pathname: string,
  searchParamsValue: string,
  updates: Readonly<Record<string, string | null>>,
) {
  const params = new URLSearchParams(searchParamsValue);

  for (const [key, value] of Object.entries(updates)) {
    if (value === null) {
      params.delete(key);
    } else {
      params.set(key, value);
    }
  }

  const nextSearch = params.toString();
  return nextSearch ? `${pathname}?${nextSearch}` : pathname;
}

function describeApiError(error: Error | undefined) {
  if (!error) {
    return null;
  }

  if (error instanceof ApiError) {
    const retryHint = error.retryable === true ? " Retry is available." : "";
    const debugHint = error.debugRef ? ` Ref: ${error.debugRef}.` : "";
    return `${error.message}${retryHint}${debugHint}`;
  }

  return error.message;
}

function taskStatusTone(status: "queued" | "running" | "completed" | "failed") {
  if (status === "completed") {
    return "success" as const;
  }

  if (status === "running") {
    return "primary" as const;
  }

  if (status === "failed") {
    return "warning" as const;
  }

  return "default" as const;
}

type TaskCardProps = Readonly<{
  isFollowingLatest?: boolean;
  isLatest?: boolean;
  isSelected: boolean;
  onSelect: (taskId: number) => void;
  task: ReturnType<typeof filterCharacterizationTasks>[number];
}>;

function TaskCard({
  isFollowingLatest = false,
  isLatest = false,
  isSelected,
  onSelect,
  task,
}: TaskCardProps) {
  return (
    <button
      type="button"
      onClick={() => {
        onSelect(task.taskId);
      }}
      className={cx(
        "w-full cursor-pointer rounded-[1rem] border px-4 py-4 text-left shadow-[0_10px_30px_rgba(0,0,0,0.08)] transition",
        isSelected
          ? "border-primary/40 bg-card"
          : "border-border bg-card hover:border-primary/25 hover:bg-primary/5",
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="truncate text-sm font-semibold text-foreground">
            {task.summary || "Characterization task"}
          </h3>
          <p className="mt-1 text-xs uppercase tracking-[0.14em] text-muted-foreground">
            Task #{task.taskId}
          </p>
        </div>
        <SurfaceTag tone={taskStatusTone(task.status)}>{task.status}</SurfaceTag>
      </div>

      <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
        {isLatest ? <SurfaceTag tone="primary">Latest</SurfaceTag> : null}
        {isFollowingLatest ? <SurfaceTag tone="success">Following</SurfaceTag> : null}
        <SurfaceTag tone="default">{task.executionMode}</SurfaceTag>
        {task.datasetId ? <SurfaceTag tone="default">{task.datasetId}</SurfaceTag> : null}
        <SurfaceTag tone="default">{task.visibilityScope}</SurfaceTag>
      </div>

      <div className="mt-4 grid gap-2 text-xs text-muted-foreground sm:grid-cols-2">
        <span>Submitted: {task.submittedAt}</span>
        <span className="sm:text-right">{task.ownerDisplayName}</span>
      </div>
    </button>
  );
}

export function CharacterizationWorkspace() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [, startTransition] = useTransition();
  const [taskQuery, setTaskQuery] = useState("");
  const [taskScope, setTaskScope] = useState<CharacterizationTaskScope>("dataset");
  const [taskStatusFilter, setTaskStatusFilter] =
    useState<CharacterizationTaskStatusFilter>("all");
  const [isRefreshingWorkflow, setIsRefreshingWorkflow] = useState(false);

  const form = useForm<CharacterizationRequestValues>({
    resolver: zodResolver(characterizationRequestSchema),
    defaultValues: defaultRequestValues,
  });

  const requestedTaskId = parseCharacterizationTaskIdParam(searchParams.get("taskId"));
  const {
    session,
    activeDatasetState,
    characterizationTasks,
    latestCharacterizationTask,
    resolvedTaskId,
    activeTask,
    activeTaskError,
    isTaskTransitioning,
    taskMutationStatus,
    submitCharacterizationTask,
    clearTaskMutationStatus,
    refreshCharacterizationWorkflow,
  } = useCharacterizationWorkflowData(requestedTaskId);

  const taskSummary = summarizeCharacterizationTasks(characterizationTasks);
  const filteredTasks = filterCharacterizationTasks(characterizationTasks, {
    searchQuery: taskQuery,
    scope: taskScope,
    statusFilter: taskStatusFilter,
    activeDatasetId: activeDatasetState.activeDataset?.datasetId ?? null,
  });
  const latestTaskId = latestCharacterizationTask?.taskId ?? null;
  const taskConnectionState = resolveTaskConnectionState({
    requestedTaskId,
    resolvedTaskId,
    latestTaskId,
    activeTask,
  });
  const taskRecovery = resolveTaskRecoveryNotice(
    requestedTaskId,
    latestTaskId,
    activeTaskError,
  );
  const taskLifecycleSummary = summarizeTaskLifecycle(activeTask);
  const taskResultSummary = summarizeTaskResultSurface(activeTask);
  const requestSummaryPreview = buildCharacterizationRequestSummary({
    datasetId: activeDatasetState.activeDataset?.datasetId ?? null,
    datasetName: activeDatasetState.activeDataset?.name ?? null,
    note: form.watch("summaryNote"),
  });
  const activeDatasetErrorMessage = describeApiError(activeDatasetState.activeDatasetError);
  const activeTaskErrorMessage = describeApiError(activeTaskError);
  const eventHistoryNarrative = !activeTask
    ? "Attach or submit a characterization task to inspect its persisted event trail."
    : taskConnectionState.isStaleSnapshot && resolvedTaskId !== null
      ? `Showing persisted events from task #${activeTask.taskId} while task #${resolvedTaskId} reattaches so dispatch and analysis history stay visible.`
      : taskConnectionState.hasNewerLatestTask && latestTaskId !== null
        ? `Task #${resolvedTaskId} remains attached for comparison while newer characterization activity exists on task #${latestTaskId}.`
        : taskConnectionState.isFollowingLatest && latestTaskId !== null
          ? `Following the latest characterization task #${latestTaskId}. Persisted events here should advance as backend analysis progresses.`
          : `Task #${activeTask.taskId} keeps a persisted event trail that ties dispatch state to analysis progress and published outputs.`;

  function replaceSearchState(updates: Readonly<Record<string, string | null>>) {
    startTransition(() => {
      router.replace(
        buildCharacterizationSearchHref(pathname, searchParams.toString(), updates),
        { scroll: false },
      );
    });
  }

  async function handleRefreshWorkflow() {
    setIsRefreshingWorkflow(true);
    try {
      await refreshCharacterizationWorkflow();
    } finally {
      setIsRefreshingWorkflow(false);
    }
  }

  async function handleSubmit() {
    const values = await form.trigger();
    if (!values) {
      return;
    }

    const task = await submitCharacterizationTask({
      note: form.getValues("summaryNote"),
    });

    replaceSearchState({ taskId: String(task.taskId) });
  }

  return (
    <div className="space-y-8">
      <section className="space-y-6">
        <div>
          <h1 className="text-[2.05rem] font-semibold tracking-tight text-foreground">
            Characterization
          </h1>
          <p className="mt-2 max-w-4xl text-sm leading-6 text-muted-foreground">
            Submit dataset-backed characterization work, reattach to persisted task state, and
            inspect result handles without falling back to placeholder analytics cards.
          </p>
        </div>

        <div className="grid gap-4 xl:grid-cols-[minmax(0,1.1fr)_minmax(180px,0.3fr)_minmax(180px,0.3fr)_minmax(180px,0.3fr)]">
          <div className="rounded-[1rem] border border-border bg-card px-4 py-4 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
            <div className="flex flex-wrap items-center gap-2 text-[11px]">
              <SurfaceTag
                tone={activeDatasetState.activeDataset ? "success" : "default"}
              >
                {activeDatasetState.activeDataset?.name ?? "Dataset not attached"}
              </SurfaceTag>
              {resolvedTaskId !== null ? (
                <SurfaceTag tone={taskConnectionState.isAttached ? "success" : "warning"}>
                  Task #{resolvedTaskId}
                </SurfaceTag>
              ) : null}
              <SurfaceTag tone={taskLifecycleSummary.tone}>
                {taskLifecycleSummary.statusLabel}
              </SurfaceTag>
              {taskConnectionState.isFollowingLatest ? (
                <SurfaceTag tone="success">Following latest queue task</SurfaceTag>
              ) : null}
            </div>
            <p className="mt-3 text-sm text-muted-foreground">
              Workspace submit authority:{" "}
              {session?.canSubmitTasks ? "available" : "disabled for this session"}.
            </p>
          </div>
          <SurfaceStat label="Characterization Tasks" value={String(taskSummary.total)} />
          <SurfaceStat label="Active" value={String(taskSummary.activeCount)} tone="primary" />
          <SurfaceStat label="Result-backed" value={String(taskSummary.resultBackedCount)} />
        </div>
      </section>

      {taskMutationStatus.message ? (
        <div
          className={cx(
            "rounded-[1rem] border px-4 py-3 text-sm",
            taskMutationStatus.state === "error"
              ? "border-rose-500/30 bg-rose-500/8 text-rose-100"
              : "border-primary/30 bg-primary/8 text-foreground",
          )}
        >
          {taskMutationStatus.message}
        </div>
      ) : null}

      <section className="grid gap-5 xl:grid-cols-[minmax(320px,0.84fr)_minmax(0,1.16fr)]">
        <div className="space-y-4">
          <SurfacePanel
            title="Design Scope"
            description="Characterization authority stays dataset-centric in this slice: the active dataset anchors submission, task recovery, and persisted results."
          >
            {activeDatasetErrorMessage ? (
              <div className="rounded-[0.9rem] border border-rose-500/30 bg-rose-500/8 px-4 py-3 text-sm text-rose-100">
                Unable to resolve the active dataset. {activeDatasetErrorMessage}
              </div>
            ) : null}

            <div className="grid gap-3 md:grid-cols-2">
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Active Dataset
                </p>
                <p className="mt-2 text-sm font-semibold text-foreground">
                  {activeDatasetState.activeDataset?.name ?? "Attach a dataset in the shell first"}
                </p>
                <p className="mt-2 text-xs text-muted-foreground">
                  {activeDatasetState.activeDataset?.datasetId ?? "No dataset in session"}
                </p>
              </div>
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Dataset Source
                </p>
                <p className="mt-2 text-sm font-semibold text-foreground">
                  {activeDatasetState.activeDataset?.source ?? "none"}
                </p>
                <p className="mt-2 text-xs text-muted-foreground">
                  {activeDatasetState.activeDataset?.status ?? "Not attached"}
                </p>
              </div>
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Dataset Owner
                </p>
                <p className="mt-2 text-sm font-semibold text-foreground">
                  {activeDatasetState.activeDataset?.owner ?? "--"}
                </p>
              </div>
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Dataset Family
                </p>
                <p className="mt-2 text-sm font-semibold text-foreground">
                  {activeDatasetState.activeDataset?.family ?? "--"}
                </p>
              </div>
            </div>

            <div className="mt-4 rounded-[0.9rem] border border-border bg-surface px-4 py-4 text-sm text-muted-foreground">
              Trace selection and analysis config remain backend-owned in this slice. The frontend
              centers on persisted dataset, task, and result relationships so refresh and reattach
              keep the workflow readable.
            </div>
          </SurfacePanel>

          <SurfacePanel
            title="Run Characterization"
            description="Submit a characterization task for the active dataset and keep the persisted request summary visible before and after dispatch."
          >
            <form
              className="space-y-4"
              onSubmit={(event) => {
                event.preventDefault();
              }}
            >
              <label className="block rounded-[0.9rem] border border-border bg-surface px-4 py-3">
                <span className="mb-2 block text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Request Note
                </span>
                <textarea
                  {...form.register("summaryNote")}
                  rows={4}
                  placeholder="Optional context for this characterization run, for example baseline review or fit refresh."
                  className="w-full resize-none bg-transparent text-sm leading-6 text-foreground outline-none placeholder:text-muted-foreground"
                />
              </label>
              {form.formState.errors.summaryNote ? (
                <p className="text-sm text-rose-300">
                  {form.formState.errors.summaryNote.message}
                </p>
              ) : null}

              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4 text-sm text-muted-foreground">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Submission Preview
                </p>
                <p className="mt-2 text-foreground">{requestSummaryPreview}</p>
              </div>

              <button
                type="button"
                onClick={() => {
                  void handleSubmit();
                }}
                disabled={
                  taskMutationStatus.state === "submitting" ||
                  !session?.canSubmitTasks ||
                  !activeDatasetState.activeDataset
                }
                className="inline-flex cursor-pointer items-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <Play className="h-4 w-4" />
                Run Characterization
              </button>
            </form>
          </SurfacePanel>

          <SurfacePanel
            title="Characterization Task Queue"
            description="Inspect characterization-lane tasks for the current dataset or the wider workspace, then attach a task into the persisted result surface."
          >
            <div className="grid gap-3 md:grid-cols-[minmax(0,1fr)_180px_180px]">
              <label className="rounded-[0.9rem] border border-border bg-surface px-4 py-3">
                <span className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  <Search className="h-3.5 w-3.5" />
                  Search
                </span>
                <input
                  value={taskQuery}
                  onChange={(event) => {
                    setTaskQuery(event.target.value);
                  }}
                  placeholder="Find by task id, summary, or dataset"
                  className="w-full bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground"
                />
              </label>

              <label className="rounded-[0.9rem] border border-border bg-surface px-4 py-3">
                <span className="mb-2 block text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Scope
                </span>
                <select
                  value={taskScope}
                  onChange={(event) => {
                    setTaskScope(event.target.value as CharacterizationTaskScope);
                  }}
                  className="w-full bg-transparent text-sm text-foreground outline-none"
                >
                  <option value="dataset">Active dataset</option>
                  <option value="all">All characterization tasks</option>
                </select>
              </label>

              <label className="rounded-[0.9rem] border border-border bg-surface px-4 py-3">
                <span className="mb-2 block text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Status
                </span>
                <select
                  value={taskStatusFilter}
                  onChange={(event) => {
                    setTaskStatusFilter(event.target.value as CharacterizationTaskStatusFilter);
                  }}
                  className="w-full bg-transparent text-sm text-foreground outline-none"
                >
                  <option value="all">All statuses</option>
                  <option value="active">Queued or running</option>
                  <option value="completed">Completed</option>
                  <option value="failed">Failed</option>
                </select>
              </label>
            </div>

            <div className="mt-4 flex items-center justify-between gap-3 rounded-[0.9rem] border border-border bg-surface px-4 py-3 text-xs text-muted-foreground">
              <div className="flex flex-wrap items-center gap-2">
                <span>
                  Showing {filteredTasks.length} of {characterizationTasks.length} characterization
                  tasks
                </span>
                {taskConnectionState.mode === "explicit" && resolvedTaskId !== null ? (
                  <SurfaceTag tone="warning">Locked to task #{resolvedTaskId}</SurfaceTag>
                ) : null}
                {taskConnectionState.isFollowingLatest && latestTaskId !== null ? (
                  <SurfaceTag tone="success">Following latest #{latestTaskId}</SurfaceTag>
                ) : null}
              </div>
              <button
                type="button"
                onClick={() => {
                  void handleRefreshWorkflow();
                }}
                disabled={isRefreshingWorkflow}
                className="inline-flex cursor-pointer items-center gap-2 rounded-full border border-border px-3 py-1.5 text-foreground transition hover:border-primary/40 hover:bg-primary/10 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <RefreshCcw className={cx("h-3.5 w-3.5", isRefreshingWorkflow && "animate-spin")} />
                Refresh
              </button>
            </div>

            <div className="mt-4 space-y-3">
              {filteredTasks.map((task) => (
                <TaskCard
                  key={task.taskId}
                  isSelected={task.taskId === resolvedTaskId}
                  isFollowingLatest={
                    task.taskId === resolvedTaskId && taskConnectionState.isFollowingLatest
                  }
                  isLatest={task.taskId === latestTaskId}
                  onSelect={(taskId) => {
                    clearTaskMutationStatus();
                    replaceSearchState({ taskId: String(taskId) });
                  }}
                  task={task}
                />
              ))}
            </div>

            {filteredTasks.length === 0 ? (
              <div className="mt-4 rounded-[0.9rem] border border-dashed border-border bg-surface px-4 py-5 text-sm text-muted-foreground">
                No characterization tasks match the current filters.
              </div>
            ) : null}
          </SurfacePanel>
        </div>

        <div className="space-y-4">
          <TaskAttachmentPanel
            task={activeTask}
            connectionState={taskConnectionState}
            recoveryNotice={taskRecovery}
            taskErrorMessage={activeTaskErrorMessage}
            isRefreshing={isRefreshingWorkflow}
            isTransitioning={isTaskTransitioning}
            onRefresh={() => {
              void handleRefreshWorkflow();
            }}
            onAttachLatest={
              latestCharacterizationTask
                ? () => {
                    replaceSearchState({ taskId: String(latestCharacterizationTask.taskId) });
                  }
                : null
            }
            onFollowLatest={() => {
              replaceSearchState({ taskId: null });
            }}
          />

          <TaskLifecyclePanel task={activeTask} summary={taskLifecycleSummary} />

          <TaskEventHistoryPanel
            title="Task Event History"
            description="Inspect persisted event records so dispatch changes, progress movement, and task outcomes remain readable after refresh or recovery."
            task={activeTask}
            narrative={eventHistoryNarrative}
            emptyMessage="No persisted characterization task events are attached yet. Submit or attach a task to inspect its backend event history."
          />

          <TaskResultPanel task={activeTask} summary={taskResultSummary} />
        </div>
      </section>
    </div>
  );
}
