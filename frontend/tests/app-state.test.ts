import { describe, expect, it } from "vitest";

import {
  parseDatasetIdFromSearch,
  resolveActiveDatasetId,
  resolveActiveDatasetSource,
} from "../src/lib/app-state/active-dataset-state";
import { mapSessionResponse } from "../src/lib/api/session";
import { mapTaskSummaryResponse } from "../src/lib/api/tasks";
import {
  summarizeTaskQueue,
} from "../src/lib/app-state/task-queue-store";

describe("active dataset state helpers", () => {
  it("parses dataset ids from URL search params", () => {
    expect(parseDatasetIdFromSearch("?datasetId=fluxonium-2025-031")).toBe("fluxonium-2025-031");
    expect(parseDatasetIdFromSearch("?datasetId=   ")).toBeNull();
    expect(parseDatasetIdFromSearch("")).toBeNull();
  });

  it("prefers route state over preferred in-memory state", () => {
    expect(resolveActiveDatasetId("route-dataset", "session-dataset")).toBe("route-dataset");
    expect(resolveActiveDatasetId(null, "session-dataset")).toBe("session-dataset");
    expect(resolveActiveDatasetSource("route-dataset", "session-dataset")).toBe("url");
    expect(resolveActiveDatasetSource(null, "session-dataset")).toBe("session");
    expect(resolveActiveDatasetSource(null, null)).toBe("none");
  });
});

describe("session contract mapping", () => {
  it("maps backend session payloads into the frontend session snapshot", () => {
    expect(
      mapSessionResponse({
        session_id: "session-dev-001",
        auth: {
          state: "authenticated",
          mode: "development_stub",
          scopes: ["tasks:submit", "datasets:manage"],
          can_submit_tasks: true,
          can_manage_datasets: true,
          user: {
            user_id: "user-dev-01",
            display_name: "Device Lab",
            email: "device-lab@example.com",
          },
        },
        active_dataset: {
          dataset_id: "fluxonium-2025-031",
          name: "Fluxonium sweep 031",
          family: "Fluxonium",
          status: "Ready",
        },
      }),
    ).toEqual({
      sessionId: "session-dev-001",
      authState: "authenticated",
      authMode: "development_stub",
      scopes: ["tasks:submit", "datasets:manage"],
      canSubmitTasks: true,
      canManageDatasets: true,
      user: {
        userId: "user-dev-01",
        displayName: "Device Lab",
        email: "device-lab@example.com",
      },
      activeDataset: {
        datasetId: "fluxonium-2025-031",
        name: "Fluxonium sweep 031",
        family: "Fluxonium",
        status: "Ready",
      },
    });
  });
});

describe("task queue store", () => {
  it("maps backend task summaries into the frontend task queue shape", () => {
    expect(
      mapTaskSummaryResponse({
        task_id: 14,
        kind: "simulation",
        lane: "simulation",
        status: "running",
        submitted_at: "2026-03-12 01:30:00",
        submitted_by: "Device Lab",
        dataset_id: "fluxonium-2025-031",
        definition_id: 18,
        summary: "Fluxonium sweep queued from workspace",
      }),
    ).toEqual({
      taskId: 14,
      kind: "simulation",
      lane: "simulation",
      status: "running",
      submittedAt: "2026-03-12 01:30:00",
      submittedBy: "Device Lab",
      datasetId: "fluxonium-2025-031",
      definitionId: 18,
      summary: "Fluxonium sweep queued from workspace",
    });
  });

  it("summarizes task counts by backend status", () => {
    const tasks = [
      mapTaskSummaryResponse({
        task_id: 11,
        kind: "simulation",
        lane: "simulation",
        status: "queued",
        submitted_at: "2026-03-12 01:20:00",
        submitted_by: "Device Lab",
        dataset_id: "fluxonium-2025-031",
        definition_id: 18,
        summary: "Queued simulation",
      }),
      mapTaskSummaryResponse({
        task_id: 12,
        kind: "characterization",
        lane: "characterization",
        status: "running",
        submitted_at: "2026-03-12 01:21:00",
        submitted_by: "Device Lab",
        dataset_id: "fluxonium-2025-031",
        definition_id: 18,
        summary: "Running characterization",
      }),
      mapTaskSummaryResponse({
        task_id: 13,
        kind: "post_processing",
        lane: "characterization",
        status: "failed",
        submitted_at: "2026-03-12 01:22:00",
        submitted_by: "Device Lab",
        dataset_id: "fluxonium-2025-031",
        definition_id: null,
        summary: "Failed post-processing",
      }),
      mapTaskSummaryResponse({
        task_id: 14,
        kind: "simulation",
        lane: "simulation",
        status: "completed",
        submitted_at: "2026-03-12 01:23:00",
        submitted_by: "Device Lab",
        dataset_id: "fluxonium-2025-031",
        definition_id: 18,
        summary: "Completed simulation",
      }),
    ];

    expect(summarizeTaskQueue(tasks)).toEqual({
      total: 4,
      queuedCount: 1,
      runningCount: 1,
      failedCount: 1,
      completedCount: 1,
    });
  });
});
