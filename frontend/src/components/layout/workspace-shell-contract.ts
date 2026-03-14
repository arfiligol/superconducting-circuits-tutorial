"use client";

import type { SessionSnapshot } from "@/lib/api/session";
import type { TaskSummary } from "@/lib/api/tasks";

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
