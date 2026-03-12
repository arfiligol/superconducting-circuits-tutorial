"use client";

import { useEffect, useState, useTransition } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  FileCode2,
  LoaderCircle,
  Play,
  RefreshCcw,
  Search,
  WandSparkles,
  Waypoints,
} from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";

import type { CircuitDefinitionSummary } from "@/features/circuit-definition-editor/lib/contracts";
import { buildNormalizedOutputPreview } from "@/features/circuit-definition-editor/lib/preview";
import { useSimulationWorkflowData } from "@/features/simulation/hooks/use-simulation-workflow-data";
import { parseSimulationDefinitionIdParam } from "@/features/simulation/lib/definition-id";
import {
  buildSimulationRequestSummary,
  filterSimulationDefinitions,
  filterSimulationTasks,
  resolveSimulationSelectionRecovery,
  resolveSimulationTaskAttachmentState,
  resolveSimulationTaskRecovery,
  summarizeSimulationTaskResults,
  summarizeSimulationTasks,
  type SimulationTaskScope,
  type SimulationTaskStatusFilter,
} from "@/features/simulation/lib/workflow";
import {
  SurfacePanel,
  SurfaceStat,
  SurfaceTag,
  cx,
} from "@/features/shared/components/surface-kit";
import { TaskEventHistoryPanel } from "@/features/shared/components/task-event-history-panel";
import { ApiError } from "@/lib/api/client";

const simulationRequestSchema = z.object({
  summaryNote: z.string().trim().max(180, "Keep the request note within 180 characters."),
});

type SimulationRequestValues = z.infer<typeof simulationRequestSchema>;

const defaultRequestValues: SimulationRequestValues = {
  summaryNote: "",
};

function buildSimulationSearchHref(
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

function lineCount(value: string) {
  return value.split("\n").length;
}

function parseTaskIdParam(value: string | null): number | null {
  if (!value) {
    return null;
  }

  const parsedValue = Number.parseInt(value, 10);
  return Number.isFinite(parsedValue) ? parsedValue : null;
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

function definitionStatusTone(
  status: CircuitDefinitionSummary["validation_status"],
) {
  return status === "warning" ? ("warning" as const) : ("success" as const);
}

function taskKindLabel(kind: "simulation" | "post_processing" | "characterization") {
  if (kind === "post_processing") {
    return "Post Processing";
  }

  if (kind === "characterization") {
    return "Characterization";
  }

  return "Simulation";
}

type DefinitionCardProps = Readonly<{
  definition: CircuitDefinitionSummary;
  isActive: boolean;
  onSelect: (definitionId: number) => void;
  isPinned?: boolean;
}>;

function DefinitionCard({
  definition,
  isActive,
  onSelect,
  isPinned = false,
}: DefinitionCardProps) {
  return (
    <button
      type="button"
      onClick={() => {
        onSelect(definition.definition_id);
      }}
      className={cx(
        "w-full cursor-pointer rounded-[1rem] border px-4 py-4 text-left shadow-[0_10px_30px_rgba(0,0,0,0.08)] transition",
        isActive
          ? "border-primary/40 bg-card"
          : "border-border bg-card hover:border-primary/25 hover:bg-primary/5",
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h2 className="truncate text-sm font-semibold text-foreground">{definition.name}</h2>
          <p className="mt-1 text-xs uppercase tracking-[0.14em] text-muted-foreground">
            Definition #{definition.definition_id}
          </p>
        </div>
        <SurfaceTag tone={definitionStatusTone(definition.validation_status)}>
          {definition.validation_status === "warning" ? "Warnings" : "Ready"}
        </SurfaceTag>
      </div>

      <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
        {isActive ? <SurfaceTag tone="primary">Selected</SurfaceTag> : null}
        {isPinned ? <SurfaceTag tone="warning">Pinned</SurfaceTag> : null}
        <SurfaceTag tone={definition.preview_artifact_count > 0 ? "primary" : "default"}>
          {definition.preview_artifact_count} artifacts
        </SurfaceTag>
      </div>

      <div className="mt-4 grid gap-2 text-xs text-muted-foreground sm:grid-cols-2">
        <span>Created: {definition.created_at}</span>
        <span className="sm:text-right">{definition.element_count} elements</span>
      </div>
    </button>
  );
}

type TaskCardProps = Readonly<{
  isSelected: boolean;
  onSelect: (taskId: number) => void;
  task: ReturnType<typeof filterSimulationTasks>[number];
}>;

function TaskCard({ isSelected, onSelect, task }: TaskCardProps) {
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
            {task.summary || `${taskKindLabel(task.kind)} task`}
          </h3>
          <p className="mt-1 text-xs uppercase tracking-[0.14em] text-muted-foreground">
            Task #{task.taskId}
          </p>
        </div>
        <SurfaceTag tone={taskStatusTone(task.status)}>
          {task.status}
        </SurfaceTag>
      </div>

      <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
        <SurfaceTag tone="default">{taskKindLabel(task.kind)}</SurfaceTag>
        <SurfaceTag tone="default">{task.executionMode}</SurfaceTag>
        {task.definitionId !== null ? (
          <SurfaceTag tone="default">Definition #{task.definitionId}</SurfaceTag>
        ) : null}
        {task.datasetId ? <SurfaceTag tone="default">{task.datasetId}</SurfaceTag> : null}
      </div>

      <div className="mt-4 grid gap-2 text-xs text-muted-foreground sm:grid-cols-2">
        <span>Submitted: {task.submittedAt}</span>
        <span className="sm:text-right">{task.ownerDisplayName}</span>
      </div>
    </button>
  );
}

export function SimulationWorkbenchShell() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [, startTransition] = useTransition();
  const [definitionQuery, setDefinitionQuery] = useState("");
  const [taskQuery, setTaskQuery] = useState("");
  const [taskScope, setTaskScope] = useState<SimulationTaskScope>("definition");
  const [taskStatusFilter, setTaskStatusFilter] =
    useState<SimulationTaskStatusFilter>("all");
  const [isRefreshingWorkflow, setIsRefreshingWorkflow] = useState(false);

  const form = useForm<SimulationRequestValues>({
    resolver: zodResolver(simulationRequestSchema),
    defaultValues: defaultRequestValues,
  });

  const requestedDefinitionId = searchParams.get("definitionId");
  const requestedTaskId = parseTaskIdParam(searchParams.get("taskId"));
  const rawDefinitionId = parseSimulationDefinitionIdParam(requestedDefinitionId);
  const {
    session,
    activeDatasetState,
    definitions,
    definitionsError,
    isDefinitionsLoading,
    resolvedDefinitionId,
    selectedDefinitionSummary,
    activeDefinition,
    activeDefinitionError,
    isDefinitionTransitioning,
    simulationTasks,
    latestSimulationTask,
    resolvedTaskId,
    activeTask,
    activeTaskError,
    isTaskTransitioning,
    taskMutationStatus,
    submitSimulationTask,
    clearTaskMutationStatus,
    refreshSimulationWorkflow,
  } = useSimulationWorkflowData(rawDefinitionId, requestedTaskId);

  const filteredDefinitions = filterSimulationDefinitions(definitions, definitionQuery);
  const pinnedDefinition =
    resolvedDefinitionId !== null &&
    !filteredDefinitions.some(
      (definition) => definition.definition_id === resolvedDefinitionId,
    )
      ? definitions?.find((definition) => definition.definition_id === resolvedDefinitionId)
      : undefined;
  const taskSummary = summarizeSimulationTasks(simulationTasks);
  const filteredTasks = filterSimulationTasks(simulationTasks, {
    searchQuery: taskQuery,
    scope: taskScope,
    statusFilter: taskStatusFilter,
    selectedDefinitionId: resolvedDefinitionId,
    activeDatasetId: activeDatasetState.activeDataset?.datasetId ?? null,
  });
  const taskResultSummary = summarizeSimulationTaskResults(activeTask);
  const definitionRecovery = resolveSimulationSelectionRecovery(
    requestedDefinitionId,
    resolvedDefinitionId,
    definitions,
  );
  const taskRecovery = resolveSimulationTaskRecovery(
    requestedTaskId,
    latestSimulationTask?.taskId ?? null,
    activeTaskError,
  );
  const taskAttachmentState = resolveSimulationTaskAttachmentState(activeTask, resolvedTaskId);
  const normalizedPreview = buildNormalizedOutputPreview(
    activeDefinition?.normalized_output ?? "{\n  \"circuit\": \"pending\"\n}",
  );
  const requestSummaryPreview = buildSimulationRequestSummary({
    kind: "simulation",
    definitionId: resolvedDefinitionId,
    definitionName: selectedDefinitionSummary?.name ?? null,
    datasetId: activeDatasetState.activeDataset?.datasetId ?? null,
    datasetName: activeDatasetState.activeDataset?.name ?? null,
    note: form.watch("summaryNote"),
  });
  const definitionsErrorMessage = describeApiError(definitionsError);
  const activeDefinitionErrorMessage = describeApiError(activeDefinitionError);
  const activeTaskErrorMessage = describeApiError(activeTaskError);
  const eventHistoryNarrative = !activeTask
    ? "Attach or submit a simulation task to inspect its persisted dispatch trail."
    : taskAttachmentState.isStaleSnapshot && resolvedTaskId !== null
      ? `Showing persisted events from task #${activeTask.taskId} while task #${resolvedTaskId} reattaches so the simulation surface stays readable during route switching.`
      : latestSimulationTask && resolvedTaskId === latestSimulationTask.taskId
        ? `Following the latest simulation task #${latestSimulationTask.taskId}. Persisted events should advance here as dispatch, progress, and result publication change.`
        : `Task #${activeTask.taskId} keeps a persisted event trail alongside dispatch and progress so refreshes do not erase execution context.`;

  useEffect(() => {
    if (resolvedDefinitionId === null || resolvedDefinitionId === rawDefinitionId) {
      return;
    }

    startTransition(() => {
      router.replace(
        buildSimulationSearchHref(pathname, searchParams.toString(), {
          definitionId: String(resolvedDefinitionId),
        }),
        { scroll: false },
      );
    });
  }, [pathname, rawDefinitionId, resolvedDefinitionId, router, searchParams]);

  function replaceSearchState(updates: Readonly<Record<string, string | null>>) {
    startTransition(() => {
      router.replace(buildSimulationSearchHref(pathname, searchParams.toString(), updates), {
        scroll: false,
      });
    });
  }

  async function handleRefreshWorkflow() {
    setIsRefreshingWorkflow(true);
    try {
      await refreshSimulationWorkflow();
    } finally {
      setIsRefreshingWorkflow(false);
    }
  }

  async function handleSubmit(kind: "simulation" | "post_processing") {
    const values = await form.trigger();
    if (!values) {
      return;
    }

    const task = await submitSimulationTask({
      kind,
      note: form.getValues("summaryNote"),
    });

    replaceSearchState({
      definitionId: resolvedDefinitionId !== null ? String(resolvedDefinitionId) : null,
      taskId: String(task.taskId),
    });
  }

  return (
    <div className="space-y-8">
      <section className="space-y-6">
        <div>
          <h1 className="text-[2.05rem] font-semibold tracking-tight text-foreground">
            Circuit Simulation
          </h1>
          <p className="mt-2 max-w-4xl text-sm leading-6 text-muted-foreground">
            Attach a canonical definition, submit persisted simulation work, and reattach to the
            latest task and result refs without relying on page-local placeholder state.
          </p>
        </div>

        <div className="grid gap-4 xl:grid-cols-[minmax(0,1.1fr)_minmax(180px,0.3fr)_minmax(180px,0.3fr)_minmax(180px,0.3fr)]">
          <div className="rounded-[1rem] border border-border bg-card px-4 py-4 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
            <div className="flex flex-wrap items-center gap-2 text-[11px]">
              <SurfaceTag tone="primary">
                {selectedDefinitionSummary?.name ?? "Definition pending"}
              </SurfaceTag>
              <SurfaceTag
                tone={
                  activeDatasetState.activeDataset
                    ? "success"
                    : activeDatasetState.status === "error"
                      ? "warning"
                      : "default"
                }
              >
                {activeDatasetState.activeDataset?.name ?? "Dataset not attached"}
              </SurfaceTag>
              {resolvedTaskId !== null ? (
                <SurfaceTag tone={taskAttachmentState.isAttached ? "success" : "warning"}>
                  Task #{resolvedTaskId}
                </SurfaceTag>
              ) : null}
            </div>
            <p className="mt-3 text-sm text-muted-foreground">
              Workspace submit authority:{" "}
              {session?.canSubmitTasks ? "available" : "disabled for this session"}.
            </p>
          </div>
          <SurfaceStat label="Simulation Tasks" value={String(taskSummary.total)} />
          <SurfaceStat label="Active" value={String(taskSummary.activeCount)} tone="primary" />
          <SurfaceStat label="Result-backed" value={String(taskSummary.resultBackedCount)} />
        </div>
      </section>

      {definitionsError ? (
        <div className="rounded-[1rem] border border-rose-500/30 bg-rose-500/8 px-4 py-3 text-sm text-rose-100">
          Unable to load circuit definitions. {definitionsErrorMessage}
        </div>
      ) : null}

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

      <section className="grid gap-5 xl:grid-cols-[minmax(320px,0.82fr)_minmax(0,1.18fr)]">
        <div className="space-y-4">
          <SurfacePanel
            title="Canonical Definition"
            description="Simulation authority starts from the persisted circuit definition contract, not from page-local setup state."
          >
            <label className="rounded-[0.9rem] border border-border bg-surface px-4 py-3">
              <span className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-muted-foreground">
                <Search className="h-3.5 w-3.5" />
                Search definitions
              </span>
              <input
                value={definitionQuery}
                onChange={(event) => {
                  setDefinitionQuery(event.target.value);
                }}
                placeholder="Find by name or id"
                className="w-full bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground"
              />
            </label>

            {definitionRecovery ? (
              <div
                className={cx(
                  "mt-4 rounded-[0.9rem] border px-4 py-3 text-sm",
                  definitionRecovery.tone === "warning"
                    ? "border-amber-500/30 bg-amber-500/8 text-foreground"
                    : "border-border bg-surface text-muted-foreground",
                )}
              >
                <p className="font-medium text-foreground">{definitionRecovery.title}</p>
                <p className="mt-1">{definitionRecovery.message}</p>
              </div>
            ) : null}

            {isDefinitionsLoading && !definitions ? (
              <div className="mt-4 rounded-[0.9rem] border border-border bg-surface px-4 py-5 text-sm text-muted-foreground">
                Loading canonical definitions...
              </div>
            ) : null}

            {pinnedDefinition ? (
              <div className="mt-4 space-y-2">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Selected definition
                </p>
                <DefinitionCard
                  definition={pinnedDefinition}
                  isActive
                  isPinned
                  onSelect={(definitionId) => {
                    clearTaskMutationStatus();
                    replaceSearchState({ definitionId: String(definitionId) });
                  }}
                />
              </div>
            ) : null}

            <div className="mt-4 space-y-3">
              {filteredDefinitions.map((definition) => (
                <DefinitionCard
                  key={definition.definition_id}
                  definition={definition}
                  isActive={definition.definition_id === resolvedDefinitionId}
                  onSelect={(definitionId) => {
                    clearTaskMutationStatus();
                    replaceSearchState({ definitionId: String(definitionId) });
                  }}
                />
              ))}
            </div>

            {filteredDefinitions.length === 0 && (definitions?.length ?? 0) > 0 ? (
              <div className="mt-4 rounded-[0.9rem] border border-dashed border-border bg-surface px-4 py-5 text-sm text-muted-foreground">
                No canonical definitions match the current search.
              </div>
            ) : null}
          </SurfacePanel>

          <SurfacePanel
            title="Simulation Setup"
            description="Use the active dataset plus the selected canonical definition to submit persisted simulation or post-processing work."
          >
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
                  Canonical Definition
                </p>
                <p className="mt-2 text-sm font-semibold text-foreground">
                  {selectedDefinitionSummary?.name ?? "Select a definition"}
                </p>
                <p className="mt-2 text-xs text-muted-foreground">
                  {resolvedDefinitionId !== null
                    ? `Definition #${resolvedDefinitionId}`
                    : "No definition selected"}
                </p>
              </div>
            </div>

            <form
              className="mt-4 space-y-4"
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
                  placeholder="Optional context for this run, for example basis check or cache verification."
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

              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => {
                    void handleSubmit("simulation");
                  }}
                  disabled={
                    taskMutationStatus.state === "submitting" ||
                    !session?.canSubmitTasks ||
                    !activeDatasetState.activeDataset ||
                    resolvedDefinitionId === null
                  }
                  className="inline-flex cursor-pointer items-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <Play className="h-4 w-4" />
                  Run Simulation
                </button>
                <button
                  type="button"
                  onClick={() => {
                    void handleSubmit("post_processing");
                  }}
                  disabled={
                    taskMutationStatus.state === "submitting" ||
                    !session?.canSubmitTasks ||
                    !activeDatasetState.activeDataset ||
                    resolvedDefinitionId === null
                  }
                  className="inline-flex cursor-pointer items-center gap-2 rounded-md border border-border bg-surface px-4 py-2.5 text-sm font-medium text-foreground transition hover:border-primary/40 hover:bg-primary/10 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <WandSparkles className="h-4 w-4" />
                  Run Post Processing
                </button>
              </div>
            </form>
          </SurfacePanel>

          <SurfacePanel
            title="Simulation Task Queue"
            description="Inspect recent simulation and post-processing tasks, then attach a task into the right-hand detail surface."
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
                    setTaskScope(event.target.value as SimulationTaskScope);
                  }}
                  className="w-full bg-transparent text-sm text-foreground outline-none"
                >
                  <option value="definition">Current definition</option>
                  <option value="dataset">Active dataset</option>
                  <option value="all">All simulation tasks</option>
                </select>
              </label>

              <label className="rounded-[0.9rem] border border-border bg-surface px-4 py-3">
                <span className="mb-2 block text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Status
                </span>
                <select
                  value={taskStatusFilter}
                  onChange={(event) => {
                    setTaskStatusFilter(event.target.value as SimulationTaskStatusFilter);
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
              <span>
                Showing {filteredTasks.length} of {simulationTasks.length} simulation tasks
              </span>
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
                  onSelect={(taskId) => {
                    replaceSearchState({ taskId: String(taskId) });
                  }}
                  task={task}
                />
              ))}
            </div>

            {filteredTasks.length === 0 ? (
              <div className="mt-4 rounded-[0.9rem] border border-dashed border-border bg-surface px-4 py-5 text-sm text-muted-foreground">
                No simulation tasks match the current filters.
              </div>
            ) : null}
          </SurfacePanel>
        </div>

        <div className="space-y-4">
          <SurfacePanel
            title="Task Attachment / Recovery"
            description="Inspect the attached task detail, refresh it safely, and recover from stale route state without leaving the simulation workspace."
            actions={
              <button
                type="button"
                onClick={() => {
                  void handleRefreshWorkflow();
                }}
                disabled={isRefreshingWorkflow}
                className="inline-flex cursor-pointer items-center gap-2 rounded-full border border-border bg-surface px-3 py-1.5 text-xs font-medium text-foreground transition hover:border-primary/40 hover:bg-primary/10 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <RefreshCcw className={cx("h-3.5 w-3.5", isRefreshingWorkflow && "animate-spin")} />
                Refresh surface
              </button>
            }
          >
            <div className="grid gap-3 md:grid-cols-4">
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Selected Task
                </p>
                <p className="mt-2 text-lg font-semibold text-foreground">
                  {resolvedTaskId ?? "--"}
                </p>
              </div>
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Attached Snapshot
                </p>
                <p className="mt-2 text-lg font-semibold text-foreground">
                  {activeTask?.taskId ?? "--"}
                </p>
              </div>
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Backend Status
                </p>
                <p className="mt-2 text-lg font-semibold text-foreground">
                  {activeTask?.status ?? "pending"}
                </p>
              </div>
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Worker Task
                </p>
                <p className="mt-2 text-sm font-semibold text-foreground">
                  {activeTask?.workerTaskName ?? "--"}
                </p>
              </div>
            </div>

            {taskRecovery ? (
              <div className="mt-4 rounded-[0.9rem] border border-amber-500/30 bg-amber-500/8 px-4 py-3 text-sm text-foreground">
                <p className="font-medium">{taskRecovery.title}</p>
                <p className="mt-1">{taskRecovery.message}</p>
                {latestSimulationTask ? (
                  <button
                    type="button"
                    onClick={() => {
                      replaceSearchState({ taskId: String(latestSimulationTask.taskId) });
                    }}
                    className="mt-3 inline-flex cursor-pointer items-center gap-2 rounded-full border border-amber-500/30 px-3 py-1.5 text-xs font-medium transition hover:bg-amber-500/10"
                  >
                    Attach latest task #{latestSimulationTask.taskId}
                  </button>
                ) : null}
              </div>
            ) : null}

            {activeTaskError ? (
              <div className="mt-4 rounded-[0.9rem] border border-rose-500/30 bg-rose-500/8 px-4 py-3 text-sm text-rose-100">
                Unable to load task detail. {activeTaskErrorMessage}
              </div>
            ) : null}

            {taskAttachmentState.isStaleSnapshot && activeTask ? (
              <div className="mt-4 rounded-[0.9rem] border border-amber-500/30 bg-amber-500/8 px-4 py-3 text-sm text-foreground">
                Retaining task #{activeTask.taskId} while task #{resolvedTaskId} attaches so the
                simulation surface stays readable during refresh or route switching.
              </div>
            ) : null}

            {isTaskTransitioning && resolvedTaskId !== null ? (
              <div className="mt-4 flex items-center gap-3 rounded-[0.9rem] border border-border bg-surface px-4 py-4 text-sm text-muted-foreground">
                <LoaderCircle className="h-4 w-4 animate-spin" />
                Reattaching task detail...
              </div>
            ) : null}
          </SurfacePanel>

          <SurfacePanel
            title="Execution Status"
            description="Track persisted worker progress, submission readiness, and whether the task is still anchored to the active dataset."
          >
            <div className="grid gap-3 md:grid-cols-4">
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Phase
                </p>
                <p className="mt-2 text-lg font-semibold text-foreground">
                  {activeTask?.progress.phase ?? "pending"}
                </p>
              </div>
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Progress
                </p>
                <p className="mt-2 text-lg font-semibold text-foreground">
                  {activeTask ? `${activeTask.progress.percentComplete}%` : "--"}
                </p>
              </div>
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Result Handles
                </p>
                <p className="mt-2 text-lg font-semibold text-foreground">
                  {taskResultSummary.resultHandleCount}
                </p>
              </div>
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Metadata Records
                </p>
                <p className="mt-2 text-lg font-semibold text-foreground">
                  {taskResultSummary.metadataRecordCount}
                </p>
              </div>
            </div>

            <div className="mt-4 rounded-[0.9rem] border border-border bg-surface px-4 py-4 text-sm text-muted-foreground">
              {activeTask?.progress.summary ??
                "Select or submit a task to inspect its persisted execution status."}
            </div>

            <div className="mt-4 flex flex-wrap gap-2 text-[11px]">
              {activeTask ? (
                <>
                  <SurfaceTag tone={activeTask.requestReady ? "success" : "warning"}>
                    {activeTask.requestReady ? "Request ready" : "Request not ready"}
                  </SurfaceTag>
                  <SurfaceTag
                    tone={activeTask.submittedFromActiveDataset ? "success" : "warning"}
                  >
                    {activeTask.submittedFromActiveDataset
                      ? "Submitted from active dataset"
                      : "Dataset detached from session"}
                  </SurfaceTag>
                  <SurfaceTag tone="default">{activeTask.executionMode}</SurfaceTag>
                  <SurfaceTag tone="default">{activeTask.visibilityScope}</SurfaceTag>
                  <SurfaceTag tone="default">{taskKindLabel(activeTask.kind)}</SurfaceTag>
                </>
              ) : (
                <SurfaceTag tone="default">No task attached</SurfaceTag>
              )}
            </div>
          </SurfacePanel>

          <TaskEventHistoryPanel
            title="Task Event History"
            description="Inspect the persisted task timeline directly so dispatch changes, progress movement, and task outcomes remain readable after refresh or reattachment."
            task={activeTask}
            narrative={eventHistoryNarrative}
            emptyMessage="No persisted simulation task events are attached yet. Submit or attach a task to inspect its backend event history."
          />

          <SurfacePanel
            title="Result Refs"
            description="Surface the persisted result references directly from task detail so refresh and reattach paths still have enough authority context."
          >
            <div className="grid gap-3 md:grid-cols-4">
              <SurfaceStat
                label="Trace Batch"
                value={taskResultSummary.traceBatchId !== null ? String(taskResultSummary.traceBatchId) : "--"}
              />
              <SurfaceStat
                label="Analysis Run"
                value={taskResultSummary.analysisRunId !== null ? String(taskResultSummary.analysisRunId) : "--"}
              />
              <SurfaceStat
                label="Materialized"
                value={String(taskResultSummary.materializedHandleCount)}
                tone="primary"
              />
              <SurfaceStat
                label="Trace Payload"
                value={taskResultSummary.hasTracePayload ? "present" : "none"}
              />
            </div>

            <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                    Trace Payload
                  </p>
                  <SurfaceTag tone={activeTask?.resultRefs.tracePayload ? "success" : "default"}>
                    {activeTask?.resultRefs.tracePayload ? "attached" : "pending"}
                  </SurfaceTag>
                </div>
                {activeTask?.resultRefs.tracePayload ? (
                  <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4 text-sm text-muted-foreground">
                    <p className="font-medium text-foreground">
                      {activeTask.resultRefs.tracePayload.backend} ·{" "}
                      {activeTask.resultRefs.tracePayload.payloadRole}
                    </p>
                    <p className="mt-2 break-all">
                      {activeTask.resultRefs.tracePayload.storeUri}
                    </p>
                    <p className="mt-2">
                      {activeTask.resultRefs.tracePayload.dtype} · shape{" "}
                      {activeTask.resultRefs.tracePayload.shape.join(" × ")}
                    </p>
                  </div>
                ) : (
                  <div className="rounded-[0.9rem] border border-dashed border-border bg-surface px-4 py-4 text-sm text-muted-foreground">
                    No trace payload ref is attached to the current task yet.
                  </div>
                )}

                <div className="space-y-3">
                  <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                    Metadata Records
                  </p>
                  {activeTask?.resultRefs.metadataRecords.length ? (
                    activeTask.resultRefs.metadataRecords.map((record) => (
                      <div
                        key={`${record.recordType}-${record.recordId}`}
                        className="rounded-[0.9rem] border border-border bg-surface px-4 py-3 text-sm"
                      >
                        <p className="font-medium text-foreground">
                          {record.recordType} · {record.recordId}
                        </p>
                        <p className="mt-1 text-xs text-muted-foreground">
                          v{record.version} · {record.schemaVersion}
                        </p>
                      </div>
                    ))
                  ) : (
                    <div className="rounded-[0.9rem] border border-dashed border-border bg-surface px-4 py-4 text-sm text-muted-foreground">
                      No metadata records have been surfaced for this task yet.
                    </div>
                  )}
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                    Result Handles
                  </p>
                  <SurfaceTag tone={taskResultSummary.resultHandleCount > 0 ? "primary" : "default"}>
                    {taskResultSummary.resultHandleCount}
                  </SurfaceTag>
                </div>
                {activeTask?.resultRefs.resultHandles.length ? (
                  activeTask.resultRefs.resultHandles.map((handle) => (
                    <div
                      key={handle.handleId}
                      className="rounded-[0.9rem] border border-border bg-surface px-4 py-4"
                    >
                      <div className="flex flex-wrap items-center gap-2 text-[11px]">
                        <SurfaceTag tone={taskStatusTone(handle.status === "materialized" ? "completed" : "queued")}>
                          {handle.status}
                        </SurfaceTag>
                        <SurfaceTag tone="default">{handle.kind}</SurfaceTag>
                        {handle.payloadFormat ? (
                          <SurfaceTag tone="default">{handle.payloadFormat}</SurfaceTag>
                        ) : null}
                      </div>
                      <p className="mt-3 text-sm font-semibold text-foreground">{handle.label}</p>
                      <p className="mt-1 break-all text-xs text-muted-foreground">
                        {handle.payloadLocator ?? handle.handleId}
                      </p>
                      <p className="mt-2 text-xs text-muted-foreground">
                        Source task: {handle.provenance.sourceTaskId ?? "--"} · Dataset:{" "}
                        {handle.provenance.sourceDatasetId ?? "--"}
                      </p>
                    </div>
                  ))
                ) : (
                  <div className="rounded-[0.9rem] border border-dashed border-border bg-surface px-4 py-4 text-sm text-muted-foreground">
                    No result handles have been attached to the current task yet.
                  </div>
                )}
              </div>
            </div>
          </SurfacePanel>

          <SurfacePanel
            title="Canonical Definition Snapshot"
            description="The simulation surface stays anchored to the selected backend definition detail, even while task state refreshes or reattaches."
          >
            {activeDefinitionError ? (
              <div className="rounded-[0.9rem] border border-rose-500/30 bg-rose-500/8 px-4 py-3 text-sm text-rose-100">
                Unable to load definition detail. {activeDefinitionErrorMessage}
              </div>
            ) : null}

            {isDefinitionTransitioning && resolvedDefinitionId !== null ? (
              <div className="mb-4 flex items-center gap-3 rounded-[0.9rem] border border-border bg-surface px-4 py-4 text-sm text-muted-foreground">
                <LoaderCircle className="h-4 w-4 animate-spin" />
                Refreshing canonical definition detail...
              </div>
            ) : null}

            <div className="grid gap-3 md:grid-cols-4">
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Definition
                </p>
                <p className="mt-2 text-sm font-semibold text-foreground">
                  {activeDefinition?.name ?? "None selected"}
                </p>
              </div>
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Validation
                </p>
                <p className="mt-2 text-sm font-semibold text-foreground">
                  {activeDefinition?.validation_status ?? "pending"}
                </p>
              </div>
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Preview Fields
                </p>
                <p className="mt-2 text-sm font-semibold text-foreground">
                  {normalizedPreview.fieldCount}
                </p>
              </div>
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Source Lines
                </p>
                <p className="mt-2 text-sm font-semibold text-foreground">
                  {activeDefinition ? lineCount(activeDefinition.source_text) : 0}
                </p>
              </div>
            </div>

            <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
              <div className="space-y-3">
                {normalizedPreview.fields.slice(0, 6).map((field) => (
                  <div
                    key={field.key}
                    className="rounded-[0.9rem] border border-border bg-surface px-4 py-3"
                  >
                    <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                      {field.label}
                    </p>
                    <p className="mt-2 text-sm font-semibold text-foreground">{field.value}</p>
                  </div>
                ))}
                {normalizedPreview.fields.length === 0 ? (
                  <div className="rounded-[0.9rem] border border-dashed border-border bg-surface px-4 py-4 text-sm text-muted-foreground">
                    No structured normalized output is available for the selected definition yet.
                  </div>
                ) : null}
              </div>

              <div className="rounded-[0.9rem] border border-border bg-background">
                <div className="flex items-center justify-between border-b border-border bg-surface px-4 py-3 text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <FileCode2 className="h-4 w-4" />
                    <span>source_text.yml</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Waypoints className="h-4 w-4" />
                    <span>simulation authority</span>
                  </div>
                </div>
                <pre className="max-h-[22rem] overflow-auto px-4 py-4 text-sm leading-6 text-foreground">
                  {activeDefinition?.source_text ?? "circuit:\n  name: pending_selection\n"}
                </pre>
              </div>
            </div>
          </SurfacePanel>
        </div>
      </section>
    </div>
  );
}
