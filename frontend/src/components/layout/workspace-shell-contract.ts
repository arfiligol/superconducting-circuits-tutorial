"use client";

import type { SessionSnapshot } from "@/lib/api/session";
import type { TaskSummary } from "@/lib/api/tasks";
import type {
  ActiveDatasetSnapshot,
  ActiveDatasetSource,
  ActiveDatasetStatus,
} from "@/lib/app-state/active-dataset";

export function resolveShellUserInitials(displayName: string | null | undefined) {
  const normalized = displayName?.trim();
  if (!normalized) {
    return "AN";
  }

  const parts = normalized.split(/\s+/).slice(0, 2);
  return parts
    .map((part) => part.charAt(0).toUpperCase())
    .join("")
    .slice(0, 2);
}

export function resolveShellTaskHref(task: Pick<TaskSummary, "lane" | "taskId">) {
  const basePath = task.lane === "characterization" ? "/characterization" : "/circuit-simulation";
  return `${basePath}?taskId=${task.taskId}`;
}

export function resolveShellTaskLabel(task: Pick<TaskSummary, "kind" | "executionMode">) {
  const kindLabel =
    task.kind === "post_processing"
      ? "Post-processing"
      : task.kind === "characterization"
        ? "Characterization"
        : "Simulation";

  return `${kindLabel} · ${task.executionMode === "smoke" ? "Smoke" : "Run"}`;
}

export function resolveShellWorkerSummary(
  workspace: SessionSnapshot["workspace"] | undefined,
  hasRuntimeSummary = false,
) {
  if (hasRuntimeSummary && workspace) {
    return {
      label: "Runtime Summary",
      value: "Connected",
      detail: `${workspace.displayName} runtime summary is available.`,
      tone: "success",
    } as const;
  }

  return {
    label: "Worker Summary",
    value: "Awaiting Authority",
    detail: workspace
      ? `${workspace.displayName} has no runtime summary surface yet.`
      : "Runtime summary is unavailable until the session resolves.",
    tone: "warning",
  } as const;
}

export function resolveShellActiveDatasetSummary(
  dataset: ActiveDatasetSnapshot | null,
  options: Readonly<{
    status: ActiveDatasetStatus;
    source: ActiveDatasetSource;
    errorDetail?: string | null;
    isUpdating: boolean;
  }>,
) {
  if (options.status === "syncing-route" || options.isUpdating) {
    return {
      value: "Syncing active dataset...",
      detail: "Session authority is updating the dataset selection.",
      badge: "Syncing",
    } as const;
  }

  if (options.errorDetail && !dataset) {
    return {
      value: "No active dataset",
      detail: options.errorDetail,
      badge: "Error",
    } as const;
  }

  if (!dataset) {
    return {
      value: "No active dataset",
      detail: "Select one from Raw Data to attach it to the session.",
      badge: null,
    } as const;
  }

  return {
    value: dataset.name ?? dataset.datasetId,
    detail: null,
    badge:
      dataset.status ??
      (options.source === "url" ? "Attached" : options.source === "session" ? "Session" : null),
  } as const;
}
