"use client";

import { Database, LoaderCircle, Shield, Workflow, X } from "lucide-react";

import { cx } from "@/features/shared/components/surface-kit";
import {
  useActiveDataset,
  useAppSession,
  useTaskQueue,
} from "@/lib/app-state";

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

export function WorkspaceStatusStrip({ compact = false }: WorkspaceStatusStripProps) {
  const { session, sessionError, isSessionLoading } = useAppSession();
  const {
    activeDataset,
    source,
    routeDatasetId,
    sessionDatasetId,
    isDatasetDetailLoading,
    isUpdatingActiveDataset,
    activeDatasetError,
    clearActiveDataset,
  } = useActiveDataset();
  const { latestTask, summary, isTaskQueueLoading, taskQueueError } = useTaskQueue();

  const datasetLabel = isUpdatingActiveDataset
    ? "Syncing active dataset..."
    : isSessionLoading && !activeDataset
      ? "Loading active dataset..."
    : activeDataset?.name ?? activeDataset?.datasetId ?? "No active dataset";
  const datasetDetail = activeDatasetError
    ? activeDatasetError.message
    : isSessionLoading && !activeDataset
      ? "Waiting for GET /session"
    : source === "url" && routeDatasetId !== sessionDatasetId
      ? "URL selection is being synced to the session contract"
      : source === "url"
        ? "URL-aware selection, backed by session state"
        : source === "session"
          ? "Session-backed active dataset"
          : "Set an active dataset from a route-enabled workspace";
  const sessionValue = isSessionLoading
    ? "Loading session..."
    : session?.user?.displayName ?? "Anonymous session";
  const sessionDetail = sessionError
    ? sessionError.message
    : !session
      ? "Waiting for GET /session"
      : session.authState === "authenticated"
        ? `${session.authMode} · ${session.scopes.length} scopes`
        : `${session.authMode} · anonymous`;
  const taskValue = isTaskQueueLoading
    ? "Loading tasks..."
    : summary.total === 0
      ? "Queue idle"
      : `${summary.runningCount} running · ${summary.queuedCount} queued`;
  const taskDetail = taskQueueError
    ? taskQueueError.message
    : latestTask
      ? `${latestTask.kind} · ${latestTask.summary}`
      : "No queued or running tasks from GET /tasks";

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
        action={
          isUpdatingActiveDataset || isDatasetDetailLoading ? (
            <span className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-border bg-surface-elevated text-muted-foreground">
              <LoaderCircle className="h-4 w-4 animate-spin" />
            </span>
          ) : source === "session" && activeDataset ? (
            <button
              type="button"
              aria-label="Clear active dataset"
              onClick={() => {
                void clearActiveDataset();
              }}
              className="inline-flex h-8 w-8 cursor-pointer items-center justify-center rounded-full border border-border bg-surface-elevated text-muted-foreground transition hover:border-primary/40 hover:bg-primary/10 hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          ) : null
        }
      />

      <StatusCard
        icon={Workflow}
        label="Task Queue"
        value={taskValue}
        detail={taskDetail}
      />

      <StatusCard
        icon={Shield}
        label="Session"
        value={sessionValue}
        detail={sessionDetail}
      />
    </div>
  );
}
