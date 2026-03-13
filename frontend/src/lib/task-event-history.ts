import type { TaskDetail, TaskEvent } from "@/lib/api/tasks";

type SurfaceTone = "default" | "primary" | "success" | "warning";

export type TaskEventMetadataEntry = Readonly<{
  key: string;
  label: string;
  value: string;
}>;

export type TaskEventHistoryEntry = Readonly<{
  eventKey: string;
  eventType: TaskEvent["eventType"];
  eventTypeLabel: string;
  eventTone: SurfaceTone;
  level: TaskEvent["level"];
  levelTone: SurfaceTone;
  occurredAt: string;
  message: string;
  metadataEntries: readonly TaskEventMetadataEntry[];
}>;

export type TaskEventHistorySummary = Readonly<{
  total: number;
  infoCount: number;
  warningCount: number;
  errorCount: number;
  latestEventLabel: string | null;
  latestOccurredAt: string | null;
  dispatchStatusLabel: string | null;
  progressLabel: string | null;
  terminalStateLabel: string;
}>;

function toTitleCase(value: string) {
  return value
    .split("_")
    .filter((segment) => segment.length > 0)
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");
}

function formatTaskEventTypeLabel(eventType: TaskEvent["eventType"]) {
  switch (eventType) {
    case "task_submitted":
      return "Submitted";
    case "task_running":
      return "Running";
    case "task_completed":
      return "Completed";
    case "task_failed":
      return "Failed";
    default:
      return toTitleCase(eventType);
  }
}

function resolveTaskEventTone(event: TaskEvent): SurfaceTone {
  if (event.level === "error" || event.eventType === "task_failed") {
    return "warning";
  }

  if (event.eventType === "task_completed") {
    return "success";
  }

  if (event.eventType === "task_running" || event.eventType === "task_submitted") {
    return "primary";
  }

  return "default";
}

function resolveTaskEventLevelTone(level: TaskEvent["level"]): SurfaceTone {
  if (level === "error" || level === "warning") {
    return "warning";
  }

  return "default";
}

function formatMetadataValue(
  value: string | number | boolean | readonly string[] | null,
): string {
  if (Array.isArray(value)) {
    return value.join(", ");
  }

  if (value === null) {
    return "null";
  }

  return String(value);
}

function compareEventsDescending(left: TaskEvent, right: TaskEvent) {
  if (left.occurredAt === right.occurredAt) {
    return right.eventKey.localeCompare(left.eventKey);
  }

  return right.occurredAt.localeCompare(left.occurredAt);
}

export function buildTaskEventHistoryEntries(
  task: TaskDetail | undefined,
): readonly TaskEventHistoryEntry[] {
  return [...(task?.events ?? [])]
    .sort(compareEventsDescending)
    .map((event) => ({
      eventKey: event.eventKey,
      eventType: event.eventType,
      eventTypeLabel: formatTaskEventTypeLabel(event.eventType),
      eventTone: resolveTaskEventTone(event),
      level: event.level,
      levelTone: resolveTaskEventLevelTone(event.level),
      occurredAt: event.occurredAt,
      message: event.message,
      metadataEntries: Object.entries(event.metadata).map(([key, value]) => ({
        key,
        label: toTitleCase(key),
        value: formatMetadataValue(value),
      })),
    }));
}

export function summarizeTaskEventHistory(
  task: TaskDetail | undefined,
): TaskEventHistorySummary {
  const entries = buildTaskEventHistoryEntries(task);
  const latestEvent = entries[0] ?? null;
  const terminalStateLabel =
    task?.progress.phase === "failed" || task?.dispatch.status === "failed"
      ? "Failure persisted"
      : task?.progress.phase === "completed" || task?.dispatch.status === "completed"
        ? "Completion persisted"
        : task?.progress.phase === "running" || task?.dispatch.status === "running"
          ? "Execution active"
          : entries.length > 0
            ? "Event trail attached"
            : "Awaiting events";

  return {
    total: entries.length,
    infoCount: entries.filter((entry) => entry.level === "info").length,
    warningCount: entries.filter((entry) => entry.level === "warning").length,
    errorCount: entries.filter((entry) => entry.level === "error").length,
    latestEventLabel: latestEvent?.eventTypeLabel ?? null,
    latestOccurredAt: latestEvent?.occurredAt ?? null,
    dispatchStatusLabel: task ? toTitleCase(task.dispatch.status) : null,
    progressLabel: task ? `${task.progress.phase} · ${task.progress.percentComplete}%` : null,
    terminalStateLabel,
  };
}
