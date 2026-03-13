"use client";

import { Database, LoaderCircle, RefreshCw, Shield, Workflow, X } from "lucide-react";

import { cx } from "@/features/shared/components/surface-kit";
import {
  useActiveDataset,
  useAppSession,
  useTaskQueue,
  useActiveTask,
} from "@/lib/app-state";
import { ApiError } from "@/lib/api/client";

type WorkspaceStatusStripProps = Readonly<{
  compact?: boolean;
}>;

type StatusCardProps = Readonly<{
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
  detail: string;
  action?: React.ReactNode;
}>;

type StatusActionButtonProps = Readonly<{
  label: string;
  onClick?: () => void;
  icon: React.ComponentType<{ className?: string }>;
  disabled?: boolean;
  spinning?: boolean;
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

function StatusCard({ icon: Icon, label, value, detail, action }: StatusCardProps) {
  return (
    <div className="flex min-h-[48px] items-center justify-between gap-3 rounded-lg border border-border bg-surface px-3 py-2">
      <div className="flex min-w-0 items-center gap-3">
        <span className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-surface-elevated text-primary">
          <Icon className="h-4 w-4" />
        </span>
        <div className="min-w-0">
          <p className="text-[11px] font-medium text-muted-foreground">{label}</p>
          <p className="truncate text-sm font-medium text-foreground">{value}</p>
          <p className="truncate text-[11px] text-muted-foreground">{detail}</p>
        </div>
      </div>
      {action}
    </div>
  );
}

function StatusActionButton({
  label,
  onClick,
  icon: Icon,
  disabled = false,
  spinning = false,
}: StatusActionButtonProps) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      disabled={disabled}
      onClick={onClick}
      className="inline-flex h-8 w-8 cursor-pointer items-center justify-center rounded-full border border-border bg-surface-elevated text-muted-foreground transition hover:border-primary/40 hover:bg-primary/10 hover:text-foreground disabled:cursor-not-allowed disabled:opacity-60"
    >
      <Icon className={cx("h-4 w-4", spinning ? "animate-spin" : undefined)} />
    </button>
  );
}

export function WorkspaceStatusStrip({ compact = false }: WorkspaceStatusStripProps) {
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
    activeTasks,
    summary,
    status: taskQueueStatus,
    isTaskQueueLoading,
    isTaskQueueRefreshing,
    taskQueueError,
    refreshTaskQueue,
  } = useTaskQueue();
  const {
    activeTaskDetail,
    activeTaskError,
    status: activeTaskStatus,
    resolvedTaskId,
    isActiveTaskLoading,
    refreshActiveTask,
  } = useActiveTask();

  const datasetLabel =
    activeDatasetStatus === "syncing-route" || isUpdatingActiveDataset
      ? "Restoring active dataset..."
      : activeDatasetStatus === "loading"
        ? "Loading active dataset..."
        : activeDatasetStatus === "error" && !activeDataset
          ? "Active dataset unavailable"
          : activeDatasetStatus === "empty"
            ? "No active dataset"
            : activeDataset?.name ?? activeDataset?.datasetId ?? "No active dataset";
  const datasetDetail = activeDatasetError
    ? getStatusErrorDetail(activeDatasetError)
    : activeDatasetStatus === "loading"
      ? "Waiting for GET /session"
      : activeDatasetStatus === "syncing-route"
        ? "Reattaching the URL-selected dataset to the backend session"
        : source === "url" && routeDatasetId === sessionDatasetId
          ? "URL selection is attached to the session contract"
          : source === "url"
            ? "URL-selected dataset has not attached to the session yet"
            : source === "session" && workspace
              ? `${workspace.displayName} session-backed dataset`
              : "No active dataset has been restored for this session";
  const datasetAction = isDatasetDetailLoading ? (
    <span className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-border bg-surface-elevated text-muted-foreground">
      <LoaderCircle className="h-4 w-4 animate-spin" />
    </span>
  ) : (
    <div className="flex shrink-0 items-center gap-2">
      <StatusActionButton
        label="Refresh active dataset state"
        icon={RefreshCw}
        spinning={isUpdatingActiveDataset || isRouteSyncPending}
        disabled={isUpdatingActiveDataset || isRouteSyncPending}
        onClick={() => {
          void refreshActiveDataset();
        }}
      />
      {canRetryRouteSync && isRetryableError(activeDatasetError) ? (
        <StatusActionButton
          label="Retry dataset restore"
          icon={RefreshCw}
          onClick={() => {
            void retryRouteSync();
          }}
        />
      ) : null}
      {source === "session" && activeDataset ? (
        <StatusActionButton
          label="Clear active dataset"
          icon={X}
          disabled={isUpdatingActiveDataset}
          onClick={() => {
            void clearActiveDataset();
          }}
        />
      ) : null}
    </div>
  );

  const sessionValue =
    sessionStatus === "loading"
      ? "Loading session..."
      : sessionStatus === "error" && !session
        ? "Session unavailable"
        : session?.user?.displayName ?? "Anonymous session";
  const sessionDetail = sessionError
    ? getStatusErrorDetail(sessionError)
    : !session
      ? "Waiting for GET /session"
      : isSessionRefreshing
        ? "Refreshing backend session state"
        : `${workspace?.displayName ?? "Unknown workspace"} · ${session.authMode} · ${session.scopes.length} scopes`;

  const taskValue =
    taskQueueStatus === "loading"
      ? "Loading tasks..."
      : taskQueueStatus === "error" && summary.total === 0
        ? "Task queue unavailable"
        : summary.total === 0
          ? "Queue idle"
          : activeTasks.length > 0
            ? `${activeTasks.length} active · ${summary.failedCount} failed`
            : `${summary.completedCount} completed · ${summary.failedCount} failed`;
  const taskDetail = taskQueueError
    ? getStatusErrorDetail(taskQueueError)
    : activeTaskError
      ? `Failed to load detailed state for task #${resolvedTaskId}: ${getStatusErrorDetail(activeTaskError)}`
      : isActiveTaskLoading
        ? `Fetching task #${resolvedTaskId} details...`
        : activeTaskStatus === "empty" || !activeTaskDetail
          ? "No task history returned from GET /tasks"
          : activeTaskDetail.status === "queued" || activeTaskDetail.status === "running"
            ? `Recovered #${activeTaskDetail.taskId} · ${activeTaskDetail.progress.phase} · ${Math.round(activeTaskDetail.progress.percentComplete)}% · ${activeTaskDetail.progress.summary}`
            : `Latest #${activeTaskDetail.taskId} · ${activeTaskDetail.status} · ${activeTaskDetail.summary}`;

  return (
    <div
      className={cx(
        "grid gap-3",
        compact ? "lg:grid-cols-[minmax(0,1.25fr)_minmax(0,0.9fr)_minmax(0,1fr)]" : "grid-cols-1",
      )}
    >
      <StatusCard
        icon={Database}
        label="Active Dataset"
        value={datasetLabel}
        detail={datasetDetail}
        action={datasetAction}
      />

      <StatusCard
        icon={Workflow}
        label="Task Queue"
        value={taskValue}
        detail={taskDetail}
        action={
          <StatusActionButton
            label="Refresh task queue"
            icon={RefreshCw}
            spinning={isTaskQueueRefreshing || isActiveTaskLoading}
            disabled={isTaskQueueLoading || isActiveTaskLoading}
            onClick={() => {
              void refreshTaskQueue();
              void refreshActiveTask();
            }}
          />
        }
      />

      <StatusCard
        icon={Shield}
        label="Session"
        value={sessionValue}
        detail={sessionDetail}
        action={
          <StatusActionButton
            label="Refresh session"
            icon={RefreshCw}
            spinning={isSessionRefreshing}
            disabled={isSessionLoading}
            onClick={() => {
              void refreshSession();
            }}
          />
        }
      />
    </div>
  );
}
