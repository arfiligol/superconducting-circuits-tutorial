import { describe, expect, it } from "vitest";

import {
  parseDatasetIdFromSearch,
  resolveActiveDatasetId,
  resolveActiveDatasetSource,
} from "../src/lib/app-state/active-dataset-state";
import { createAnonymousSessionSnapshot } from "../src/lib/app-state/app-session";
import {
  createTaskQueueItem,
  summarizeTaskQueue,
  taskQueueReducer,
} from "../src/lib/app-state/task-queue-store";

describe("active dataset state helpers", () => {
  it("parses dataset ids from URL search params", () => {
    expect(parseDatasetIdFromSearch("?datasetId=fluxonium-2025-031")).toBe("fluxonium-2025-031");
    expect(parseDatasetIdFromSearch("?datasetId=   ")).toBeNull();
    expect(parseDatasetIdFromSearch("")).toBeNull();
  });

  it("prefers route state over preferred in-memory state", () => {
    expect(resolveActiveDatasetId("route-dataset", "memory-dataset")).toBe("route-dataset");
    expect(resolveActiveDatasetId(null, "memory-dataset")).toBe("memory-dataset");
    expect(resolveActiveDatasetSource("route-dataset", "memory-dataset")).toBe("url");
    expect(resolveActiveDatasetSource(null, "memory-dataset")).toBe("memory");
    expect(resolveActiveDatasetSource(null, null)).toBe("none");
  });
});

describe("app session defaults", () => {
  it("creates an anonymous placeholder session snapshot", () => {
    expect(createAnonymousSessionSnapshot()).toEqual({
      status: "anonymous",
      displayName: "Guest Session",
      roleLabel: "Rewrite Placeholder",
      authSource: "placeholder",
      capabilities: [],
    });
  });
});

describe("task queue store", () => {
  it("queues and updates tasks deterministically", () => {
    const queuedTask = createTaskQueueItem({
      taskId: "task-1",
      label: "Dataset sync",
      detail: "Waiting for worker",
      scope: "dataset",
      createdAt: "2026-03-12T00:00:00.000Z",
      updatedAt: "2026-03-12T00:00:00.000Z",
    });

    const queuedState = taskQueueReducer([], { type: "enqueue", task: queuedTask });
    const runningState = taskQueueReducer(queuedState, {
      type: "update",
      taskId: "task-1",
      patch: {
        status: "running",
        detail: "Worker claimed task",
        updatedAt: "2026-03-12T00:00:05.000Z",
      },
    });

    expect(runningState).toHaveLength(1);
    expect(runningState[0]?.status).toBe("running");
    expect(runningState[0]?.detail).toBe("Worker claimed task");
  });

  it("summarizes task counts by status", () => {
    const tasks = [
      createTaskQueueItem({
        taskId: "task-1",
        label: "Dataset sync",
        detail: "Waiting",
        scope: "dataset",
        status: "queued",
        createdAt: "2026-03-12T00:00:00.000Z",
      }),
      createTaskQueueItem({
        taskId: "task-2",
        label: "Definition validate",
        detail: "Running",
        scope: "definition",
        status: "running",
        createdAt: "2026-03-12T00:00:01.000Z",
      }),
      createTaskQueueItem({
        taskId: "task-3",
        label: "Session bootstrap",
        detail: "Failed",
        scope: "system",
        status: "failed",
        createdAt: "2026-03-12T00:00:02.000Z",
      }),
    ];

    expect(summarizeTaskQueue(tasks)).toEqual({
      total: 3,
      queuedCount: 1,
      runningCount: 1,
      failedCount: 1,
      succeededCount: 0,
    });
  });
});
