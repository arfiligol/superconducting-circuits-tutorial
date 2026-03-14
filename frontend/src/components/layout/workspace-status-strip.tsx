"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ChevronDown,
  Database,
  FolderKanban,
  LoaderCircle,
  RefreshCw,
  ServerCog,
  Workflow,
  X,
} from "lucide-react";

import {
  resolveShellTaskHref,
  resolveShellTaskLabel,
  resolveShellWorkerSummary,
} from "@/components/layout/workspace-shell-contract";
import { cx } from "@/features/shared/components/surface-kit";
import {
  useActiveDataset,
  useActiveTask,
  useAppSession,
  useTaskQueue,
} from "@/lib/app-state";
import { ApiError } from "@/lib/api/client";

type WorkspaceStatusStripProps = Readonly<{
  compact?: boolean;
}>;

type ShellPanel = "workspace" | "dataset" | "queue" | null;

type TriggerCardProps = Readonly<{
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
  detail: string;
  active?: boolean;
  onClick?: () => void;
  trailing?: React.ReactNode;
}>;

function getStatusErrorDetail(error: Error): string {
  if (error instanceof ApiError) {
    const errorCode = error.errorCode ? ` (${error.errorCode})` : "";
    const debugRef = error.debugRef ? ` · Ref ${error.debugRef}` : "";
    return `${error.message}${errorCode}${debugRef}`;
  }

  return error.message;
}

function isRetryableError(error: Error | undefined): boolean {
  if (!error) {
    return false;
  }

  return !(error instanceof ApiError) || error.retryable !== false;
}

function TriggerCard({
  icon: Icon,
  label,
  value,
  detail,
  active = false,
  onClick,
  trailing,
}: TriggerCardProps) {
  const content = (
    <>
      <div className="flex min-w-0 items-center gap-3">
        <span
          className={cx(
            "inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full",
            active ? "bg-primary/12 text-primary" : "bg-surface-elevated text-primary/80",
          )}
        >
          <Icon className="h-4 w-4" />
        </span>
        <div className="min-w-0">
          <p className="text-[11px] font-medium uppercase tracking-[0.16em] text-muted-foreground">
            {label}
          </p>
          <p className="truncate text-sm font-medium text-foreground">{value}</p>
          <p className="truncate text-[11px] text-muted-foreground">{detail}</p>
        </div>
      </div>
      <div className="flex shrink-0 items-center gap-2">
        {trailing}
        {onClick ? <ChevronDown className="h-4 w-4 text-muted-foreground" /> : null}
      </div>
    </>
  );

  if (!onClick) {
    return (
      <div className="flex min-h-[58px] items-center justify-between gap-3 rounded-[0.95rem] border border-border bg-surface px-3 py-3">
        {content}
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className={cx(
        "flex min-h-[58px] w-full cursor-pointer items-center justify-between gap-3 rounded-[0.95rem] border px-3 py-3 text-left transition",
        active
          ? "border-primary/35 bg-primary/10"
          : "border-border bg-surface hover:border-primary/20 hover:bg-surface-elevated",
      )}
    >
      {content}
    </button>
  );
}

function PanelActionButton({
  label,
  onClick,
  spinning = false,
  disabled = false,
}: Readonly<{
  label: string;
  onClick: () => void;
  spinning?: boolean;
  disabled?: boolean;
}>) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className="inline-flex cursor-pointer items-center gap-2 rounded-md border border-border px-3 py-2 text-xs font-medium uppercase tracking-[0.16em] text-foreground transition hover:border-primary/40 hover:bg-primary/10 disabled:cursor-not-allowed disabled:opacity-60"
    >
      <RefreshCw className={cx("h-3.5 w-3.5", spinning ? "animate-spin" : undefined)} />
      {label}
    </button>
  );
}

export function WorkspaceStatusStrip({ compact = false }: WorkspaceStatusStripProps) {
  const pathname = usePathname();
  const [openPanel, setOpenPanel] = useState<ShellPanel>(null);

  const {
    session,
    workspace,
    sessionError,
    status: sessionStatus,
    isSessionLoading,
    isSessionRefreshing,
    refreshSession,
  } = useAppSession();
  const {
    activeDataset,
    source,
    status: activeDatasetStatus,
    routeDatasetId,
    sessionDatasetId,
    isDatasetDetailLoading,
    isUpdatingActiveDataset,
    isRouteSyncPending,
    canRetryRouteSync,
    activeDatasetError,
    refreshActiveDataset,
    retryRouteSync,
    clearActiveDataset,
  } = useActiveDataset();
  const {
    tasks,
    activeTasks,
    latestTask,
    summary,
    taskQueueError,
    isTaskQueueLoading,
    isTaskQueueRefreshing,
    refreshTaskQueue,
  } = useTaskQueue();
  const {
    activeTaskDetail,
    activeTaskError,
    resolvedTaskId,
    isActiveTaskLoading,
    refreshActiveTask,
  } = useActiveTask();

  useEffect(() => {
    setOpenPanel(null);
  }, [pathname]);

  const workerSummary = resolveShellWorkerSummary(workspace);
  const queueRows = (activeTasks.length > 0 ? activeTasks : tasks).slice(0, 5);

  const workspaceValue =
    sessionStatus === "loading"
      ? "Loading workspace..."
      : workspace?.displayName ?? "Workspace unavailable";
  const workspaceDetail = sessionError
    ? getStatusErrorDetail(sessionError)
    : workspace
      ? `${workspace.role} role · ${session?.memberships.length ?? 0} memberships · session authority`
      : "Waiting for session authority";

  const datasetValue =
    activeDatasetStatus === "syncing-route" || isUpdatingActiveDataset
      ? "Syncing active dataset..."
      : activeDataset?.name ?? "No active dataset";
  const datasetDetail = activeDatasetError
    ? getStatusErrorDetail(activeDatasetError)
    : source === "url" && routeDatasetId !== sessionDatasetId
      ? "URL-selected dataset is waiting to attach to the session"
      : source === "url"
        ? "Route selection is attached to the session"
        : source === "session"
          ? "Session-backed dataset context"
          : "Select a dataset from Raw Data";

  const queueValue =
    isTaskQueueLoading && summary.total === 0
      ? "Loading queue..."
      : activeTasks.length > 0
        ? `${activeTasks.length} active task${activeTasks.length === 1 ? "" : "s"}`
        : summary.total > 0
          ? `${summary.completedCount} completed · ${summary.failedCount} failed`
          : "Queue idle";
  const queueDetail = taskQueueError
    ? getStatusErrorDetail(taskQueueError)
    : activeTaskError
      ? getStatusErrorDetail(activeTaskError)
      : activeTaskDetail
        ? `Attached #${activeTaskDetail.taskId} · ${activeTaskDetail.progress.phase}`
        : latestTask
          ? `Latest #${latestTask.taskId} · ${latestTask.status}`
          : "Open queue to inspect workspace-visible tasks";

  return (
    <div className="space-y-3">
      <div
        className={cx(
          "grid gap-3",
          compact
            ? "xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(0,1fr)_minmax(0,0.9fr)]"
            : "md:grid-cols-2 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(0,1fr)_minmax(0,0.9fr)]",
        )}
      >
        <TriggerCard
          icon={FolderKanban}
          label="Active Workspace"
          value={workspaceValue}
          detail={workspaceDetail}
          active={openPanel === "workspace"}
          onClick={() => {
            setOpenPanel((current) => (current === "workspace" ? null : "workspace"));
          }}
          trailing={
            isSessionRefreshing ? <LoaderCircle className="h-4 w-4 animate-spin text-primary" /> : null
          }
        />

        <TriggerCard
          icon={Database}
          label="Active Dataset"
          value={datasetValue}
          detail={datasetDetail}
          active={openPanel === "dataset"}
          onClick={() => {
            setOpenPanel((current) => (current === "dataset" ? null : "dataset"));
          }}
          trailing={
            isDatasetDetailLoading || isRouteSyncPending ? (
              <LoaderCircle className="h-4 w-4 animate-spin text-primary" />
            ) : null
          }
        />

        <TriggerCard
          icon={Workflow}
          label="Tasks Queue"
          value={queueValue}
          detail={queueDetail}
          active={openPanel === "queue"}
          onClick={() => {
            setOpenPanel((current) => (current === "queue" ? null : "queue"));
          }}
          trailing={
            isTaskQueueRefreshing || isActiveTaskLoading ? (
              <LoaderCircle className="h-4 w-4 animate-spin text-primary" />
            ) : null
          }
        />

        <TriggerCard
          icon={ServerCog}
          label={workerSummary.label}
          value={workerSummary.value}
          detail={workerSummary.detail}
          trailing={
            <span
              className={cx(
                "rounded-full px-2.5 py-1 text-[10px] font-medium uppercase tracking-[0.16em]",
                workerSummary.tone === "success"
                  ? "bg-emerald-500/12 text-emerald-300"
                  : "bg-amber-500/12 text-amber-300",
              )}
            >
              {workerSummary.tone}
            </span>
          }
        />
      </div>

      {openPanel === "workspace" ? (
        <section className="rounded-[1rem] border border-border bg-card p-4 shadow-[0_12px_35px_rgba(15,23,42,0.18)]">
          <div className="flex flex-wrap items-start justify-between gap-3 border-b border-border/80 pb-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                Active Workspace Trigger
              </p>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                Workspace context is session-backed. The switcher adapter is intentionally kept
                separate until membership and dirty-state confirmation contracts are available.
              </p>
            </div>
            <PanelActionButton
              label="Refresh session"
              spinning={isSessionRefreshing}
              disabled={isSessionLoading}
              onClick={() => {
                void refreshSession();
              }}
            />
          </div>

          <div className="mt-4 grid gap-3 md:grid-cols-3">
            <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-3">
              <p className="text-[11px] uppercase tracking-[0.16em] text-muted-foreground">
                Workspace
              </p>
              <p className="mt-2 text-sm font-semibold text-foreground">
                {workspace?.displayName ?? "Unavailable"}
              </p>
            </div>
            <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-3">
              <p className="text-[11px] uppercase tracking-[0.16em] text-muted-foreground">Role</p>
              <p className="mt-2 text-sm font-semibold text-foreground">
                {workspace?.role ?? "Pending"}
              </p>
            </div>
            <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-3">
              <p className="text-[11px] uppercase tracking-[0.16em] text-muted-foreground">
                Task Scope
              </p>
              <p className="mt-2 text-sm font-semibold text-foreground">
                {workspace?.defaultTaskScope ?? "Pending"}
              </p>
            </div>
          </div>
        </section>
      ) : null}

      {openPanel === "dataset" ? (
        <section className="rounded-[1rem] border border-border bg-card p-4 shadow-[0_12px_35px_rgba(15,23,42,0.18)]">
          <div className="flex flex-wrap items-start justify-between gap-3 border-b border-border/80 pb-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                Active Dataset Trigger
              </p>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                Dataset context follows session authority. Selection and search stay in Data
                Browser; the shell only surfaces the current active dataset and recovery actions.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <PanelActionButton
                label="Refresh dataset"
                spinning={isUpdatingActiveDataset || isRouteSyncPending}
                disabled={isUpdatingActiveDataset}
                onClick={() => {
                  void refreshActiveDataset();
                }}
              />
              {canRetryRouteSync && isRetryableError(activeDatasetError) ? (
                <PanelActionButton
                  label="Retry attach"
                  onClick={() => {
                    void retryRouteSync();
                  }}
                />
              ) : null}
              {source === "session" && activeDataset ? (
                <button
                  type="button"
                  onClick={() => {
                    void clearActiveDataset();
                  }}
                  className="inline-flex cursor-pointer items-center gap-2 rounded-md border border-border px-3 py-2 text-xs font-medium uppercase tracking-[0.16em] text-foreground transition hover:border-primary/40 hover:bg-primary/10"
                >
                  <X className="h-3.5 w-3.5" />
                  Clear dataset
                </button>
              ) : null}
              <Link
                href="/raw-data"
                className="inline-flex items-center rounded-md border border-border px-3 py-2 text-xs font-medium uppercase tracking-[0.16em] text-foreground transition hover:border-primary/40 hover:bg-primary/10"
              >
                Open Raw Data
              </Link>
            </div>
          </div>

          <div className="mt-4 grid gap-3 md:grid-cols-4">
            <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-3">
              <p className="text-[11px] uppercase tracking-[0.16em] text-muted-foreground">
                Dataset
              </p>
              <p className="mt-2 text-sm font-semibold text-foreground">
                {activeDataset?.name ?? "None selected"}
              </p>
            </div>
            <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-3">
              <p className="text-[11px] uppercase tracking-[0.16em] text-muted-foreground">
                Family
              </p>
              <p className="mt-2 text-sm font-semibold text-foreground">
                {activeDataset?.family ?? "Pending"}
              </p>
            </div>
            <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-3">
              <p className="text-[11px] uppercase tracking-[0.16em] text-muted-foreground">
                Status
              </p>
              <p className="mt-2 text-sm font-semibold text-foreground">
                {activeDataset?.status ?? "Pending"}
              </p>
            </div>
            <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-3">
              <p className="text-[11px] uppercase tracking-[0.16em] text-muted-foreground">
                Source
              </p>
              <p className="mt-2 text-sm font-semibold text-foreground">
                {source === "none" ? "No selection" : source}
              </p>
            </div>
          </div>
        </section>
      ) : null}

      {openPanel === "queue" ? (
        <section className="rounded-[1rem] border border-border bg-card p-4 shadow-[0_12px_35px_rgba(15,23,42,0.18)]">
          <div className="flex flex-wrap items-start justify-between gap-3 border-b border-border/80 pb-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                Tasks Queue Trigger
              </p>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                Queue visibility comes from persisted task authority. The shell exposes attachable
                entries and the latest attached task summary without taking over task-row workflows.
              </p>
            </div>
            <PanelActionButton
              label="Refresh queue"
              spinning={isTaskQueueRefreshing || isActiveTaskLoading}
              disabled={isTaskQueueLoading}
              onClick={() => {
                void refreshTaskQueue();
                void refreshActiveTask();
              }}
            />
          </div>

          <div className="mt-4 grid gap-3 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
            <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
              <p className="text-[11px] uppercase tracking-[0.16em] text-muted-foreground">
                Attached Task
              </p>
              <p className="mt-2 text-sm font-semibold text-foreground">
                {activeTaskDetail ? `#${activeTaskDetail.taskId}` : "No attached task"}
              </p>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                {activeTaskDetail
                  ? `${activeTaskDetail.progress.phase} · ${Math.round(activeTaskDetail.progress.percentComplete)}% · ${activeTaskDetail.progress.summary}`
                  : resolvedTaskId
                    ? `Waiting for task #${resolvedTaskId} detail`
                    : "Open a workflow surface or use queue links below to attach a task."}
              </p>
            </div>

            <div className="space-y-3">
              {queueRows.length > 0 ? (
                queueRows.map((task) => (
                  <Link
                    key={task.taskId}
                    href={resolveShellTaskHref(task)}
                    className="block rounded-[0.9rem] border border-border bg-surface px-4 py-3 transition hover:border-primary/25 hover:bg-surface-elevated"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-foreground">
                          #{task.taskId} · {resolveShellTaskLabel(task)}
                        </p>
                        <p className="mt-1 truncate text-xs uppercase tracking-[0.16em] text-muted-foreground">
                          {task.status} · {task.summary}
                        </p>
                      </div>
                      <span className="rounded-full border border-border px-2.5 py-1 text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
                        {task.lane}
                      </span>
                    </div>
                  </Link>
                ))
              ) : (
                <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4 text-sm text-muted-foreground">
                  No workspace-visible tasks are available yet.
                </div>
              )}
            </div>
          </div>
        </section>
      ) : null}
    </div>
  );
}
