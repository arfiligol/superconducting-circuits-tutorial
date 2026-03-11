"use client";

import { Database, Shield, Workflow, X } from "lucide-react";

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
  const { session } = useAppSession();
  const { activeDataset, source, clearPreferredDataset } = useActiveDataset();
  const { tasks, summary } = useTaskQueue();

  const latestTask = tasks[0];
  const datasetLabel = activeDataset?.name ?? activeDataset?.datasetId ?? "No active dataset";
  const datasetDetail =
    source === "url"
      ? "URL-driven selection"
      : source === "memory"
        ? "Pinned in app memory"
        : "Select a dataset from a route-enabled workspace";
  const sessionDetail =
    session.status === "authenticated"
      ? `${session.roleLabel} via ${session.authSource}`
      : "Backend auth not wired yet";
  const taskValue =
    summary.total === 0
      ? "Queue idle"
      : `${summary.runningCount} running · ${summary.queuedCount} queued`;
  const taskDetail =
    latestTask?.detail ?? "Task queue provider is ready for future backend status integration";

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
          source === "memory" ? (
            <button
              type="button"
              aria-label="Clear pinned dataset"
              onClick={clearPreferredDataset}
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
        value={session.displayName}
        detail={sessionDetail}
      />
    </div>
  );
}
