export type TaskQueueScope = "dataset" | "definition" | "system";
export type TaskQueueStatus = "queued" | "running" | "succeeded" | "failed";

export type TaskQueueItem = Readonly<{
  taskId: string;
  label: string;
  detail: string;
  scope: TaskQueueScope;
  status: TaskQueueStatus;
  createdAt: string;
  updatedAt: string;
}>;

export type TaskQueueSummary = Readonly<{
  total: number;
  queuedCount: number;
  runningCount: number;
  failedCount: number;
  succeededCount: number;
}>;

export type TaskQueueAction =
  | Readonly<{ type: "enqueue"; task: TaskQueueItem }>
  | Readonly<{
      type: "update";
      taskId: string;
      patch: Partial<Pick<TaskQueueItem, "label" | "detail" | "status" | "updatedAt">>;
    }>
  | Readonly<{ type: "remove"; taskId: string }>
  | Readonly<{ type: "clear" }>
  | Readonly<{ type: "replace"; tasks: readonly TaskQueueItem[] }>;

export function createTaskQueueItem(
  input: Readonly<{
    taskId: string;
    label: string;
    detail: string;
    scope: TaskQueueScope;
    status?: TaskQueueStatus;
    createdAt?: string;
    updatedAt?: string;
  }>,
): TaskQueueItem {
  const timestamp = input.createdAt ?? new Date().toISOString();

  return {
    taskId: input.taskId,
    label: input.label,
    detail: input.detail,
    scope: input.scope,
    status: input.status ?? "queued",
    createdAt: timestamp,
    updatedAt: input.updatedAt ?? timestamp,
  };
}

export function taskQueueReducer(
  state: readonly TaskQueueItem[],
  action: TaskQueueAction,
): readonly TaskQueueItem[] {
  switch (action.type) {
    case "enqueue": {
      const existingIndex = state.findIndex((task) => task.taskId === action.task.taskId);

      if (existingIndex >= 0) {
        return state.map((task, index) =>
          index === existingIndex ? { ...task, ...action.task } : task,
        );
      }

      return [action.task, ...state];
    }

    case "update":
      return state.map((task) =>
        task.taskId === action.taskId ? { ...task, ...action.patch } : task,
      );

    case "remove":
      return state.filter((task) => task.taskId !== action.taskId);

    case "clear":
      return [];

    case "replace":
      return [...action.tasks];
  }
}

export function summarizeTaskQueue(tasks: readonly TaskQueueItem[]): TaskQueueSummary {
  return tasks.reduce<TaskQueueSummary>(
    (summary, task) => ({
      total: summary.total + 1,
      queuedCount: summary.queuedCount + (task.status === "queued" ? 1 : 0),
      runningCount: summary.runningCount + (task.status === "running" ? 1 : 0),
      failedCount: summary.failedCount + (task.status === "failed" ? 1 : 0),
      succeededCount: summary.succeededCount + (task.status === "succeeded" ? 1 : 0),
    }),
    {
      total: 0,
      queuedCount: 0,
      runningCount: 0,
      failedCount: 0,
      succeededCount: 0,
    },
  );
}
