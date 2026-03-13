"use client";

import { useState, useTransition } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Play,
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
  ResearchTaskQueuePanel,
  ResearchWorkflowHero,
  ResearchWorkflowOverviewPanel,
} from "@/features/shared/components/research-workflow-panels";
import {
  SurfacePanel,
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
import { summarizeTaskEventHistory } from "@/lib/task-event-history";
import { summarizeResearchWorkflowSurface } from "@/lib/research-workflow-surface";
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

const characterizationTaskScopeOptions = [
  { label: "Active dataset", value: "dataset" },
  { label: "All characterization tasks", value: "all" },
] as const satisfies readonly Readonly<{
  label: string;
  value: CharacterizationTaskScope;
}>[];

const characterizationTaskStatusOptions = [
  { label: "All statuses", value: "all" },
  { label: "Queued or running", value: "active" },
  { label: "Completed", value: "completed" },
  { label: "Failed", value: "failed" },
] as const satisfies readonly Readonly<{
  label: string;
  value: CharacterizationTaskStatusFilter;
}>[];

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
  const eventHistorySummary = summarizeTaskEventHistory(activeTask);
  const workflowSurfaceSummary = summarizeResearchWorkflowSurface({
    connectionState: taskConnectionState,
    lifecycleSummary: taskLifecycleSummary,
    eventHistorySummary,
    resultSummary: taskResultSummary,
  });
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
      <ResearchWorkflowHero
        eyebrow="Research Workflow"
        title="Characterization"
        description="Submit dataset-backed characterization work, reattach to persisted task state, and inspect event and result history with the same shared workflow language as simulation."
        contextTags={[
          {
            label: activeDatasetState.activeDataset?.name ?? "Dataset not attached",
            tone: activeDatasetState.activeDataset
              ? "success"
              : activeDatasetState.status === "error"
                ? "warning"
                : "default",
          },
          ...(resolvedTaskId !== null
            ? [
                {
                  label: `Task #${resolvedTaskId}`,
                  tone: taskConnectionState.isAttached ? "success" : "warning",
                } as const,
              ]
            : []),
          {
            label: taskLifecycleSummary.statusLabel,
            tone: taskLifecycleSummary.tone,
          },
          ...(taskConnectionState.isFollowingLatest
            ? [{ label: "Following latest queue task", tone: "success" as const }]
            : []),
        ]}
        submitAuthorityLabel={`Workspace submit authority: ${
          session?.canSubmitTasks ? "available" : "disabled for this session"
        }.`}
        stats={[
          { label: "Characterization Tasks", value: String(taskSummary.total) },
          { label: "Active", value: String(taskSummary.activeCount), tone: "primary" },
          { label: "Result-backed", value: String(taskSummary.resultBackedCount) },
        ]}
      />

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

          <ResearchTaskQueuePanel
            title="Characterization Task Queue"
            description="Inspect characterization-lane tasks for the current dataset or the wider workspace, then attach a task into the shared research workflow surface."
            searchValue={taskQuery}
            onSearchChange={setTaskQuery}
            searchPlaceholder="Find by task id, summary, or dataset"
            scopeValue={taskScope}
            onScopeChange={(value) => {
              setTaskScope(value as CharacterizationTaskScope);
            }}
            scopeOptions={characterizationTaskScopeOptions}
            statusValue={taskStatusFilter}
            onStatusChange={(value) => {
              setTaskStatusFilter(value as CharacterizationTaskStatusFilter);
            }}
            statusOptions={characterizationTaskStatusOptions}
            summaryLabel={`Showing ${filteredTasks.length} of ${characterizationTasks.length} characterization tasks`}
            summaryTags={[
              ...(taskConnectionState.mode === "explicit" && resolvedTaskId !== null
                ? [{ label: `Locked to task #${resolvedTaskId}`, tone: "warning" as const }]
                : []),
              ...(taskConnectionState.isFollowingLatest && latestTaskId !== null
                ? [
                    {
                      label: `Following latest #${latestTaskId}`,
                      tone: "success" as const,
                    },
                  ]
                : []),
            ]}
            isRefreshing={isRefreshingWorkflow}
            onRefresh={() => {
              void handleRefreshWorkflow();
            }}
            isEmpty={filteredTasks.length === 0}
            emptyMessage="No characterization tasks match the current filters."
          >
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
          </ResearchTaskQueuePanel>
        </div>

        <div className="space-y-4">
          <ResearchWorkflowOverviewPanel
            summary={workflowSurfaceSummary}
            narrative={eventHistoryNarrative}
          />

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
