import { describe, expect, it } from "vitest";

import { summarizeResearchWorkflowSurface } from "../src/lib/research-workflow-surface";

describe("research workflow surface helpers", () => {
  it("summarizes a latest-following workflow with materialized results", () => {
    expect(
      summarizeResearchWorkflowSurface({
        connectionState: {
          mode: "latest",
          latestTaskId: 84,
          selectedTaskId: 84,
          attachedTaskId: 84,
          hasNewerLatestTask: false,
          isFollowingLatest: true,
          isAttached: true,
          isStaleSnapshot: false,
        },
        lifecycleSummary: {
          stage: "completed",
          statusLabel: "Dispatch completed",
          tone: "success",
          summary: "The task completed and result refs remain reattachable.",
          progressPercent: 100,
          progressSummary: "Completed",
          backendStatusLabel: "completed",
          workerTaskName: "simulation_run_task",
          submissionSourceLabel: "Active dataset session",
          acceptedAt: "2026-03-13 11:00:00",
          lastUpdatedAt: "2026-03-13 11:04:00",
          taskDatasetId: "fluxonium-2026-003",
          dispatchKey: "dispatch:84:simulation",
          requestReady: true,
          submittedFromActiveDataset: true,
          executionMode: "run",
          visibilityScope: "workspace",
        },
        eventHistorySummary: {
          total: 4,
          infoCount: 3,
          warningCount: 0,
          errorCount: 0,
          latestEventLabel: "Completed",
          latestOccurredAt: "2026-03-13 11:04:00",
          dispatchStatusLabel: "Completed",
          progressLabel: "completed · 100%",
          terminalStateLabel: "Completion persisted",
        },
        resultSummary: {
          metadataRecordCount: 2,
          resultHandleCount: 3,
          materializedHandleCount: 2,
          pendingHandleCount: 1,
          hasTracePayload: true,
          traceBatchId: 18,
          analysisRunId: 7,
          handleKindCounts: [
            { kind: "plot_bundle", count: 1 },
            { kind: "simulation_trace", count: 2 },
          ],
        },
      }),
    ).toEqual({
      statusLabel: "Dispatch completed",
      statusTone: "success",
      persistenceLabel: "Persisted task #84 attached",
      warningEventCount: 0,
      errorEventCount: 0,
      materializedHandleCount: 2,
      pendingHandleCount: 1,
      hasTracePayload: true,
      cards: [
        {
          id: "attachment",
          label: "Attachment",
          value: "Latest #84",
          detail:
            "The surface follows the newest persisted task until a URL-pinned task overrides it.",
          tone: "success",
        },
        {
          id: "dispatch",
          label: "Dispatch",
          value: "Dispatch completed",
          detail: "The task completed and result refs remain reattachable.",
          tone: "success",
        },
        {
          id: "events",
          label: "Events",
          value: "Completed",
          detail: "4 persisted events · completed · 100%",
          tone: "primary",
        },
        {
          id: "results",
          label: "Results",
          value: "2 materialized",
          detail: "1 pending handles remain and a trace payload is attached.",
          tone: "success",
        },
      ],
    });
  });

  it("preserves stale attachment context while a pinned task reattaches", () => {
    expect(
      summarizeResearchWorkflowSurface({
        connectionState: {
          mode: "explicit",
          latestTaskId: 84,
          selectedTaskId: 80,
          attachedTaskId: 79,
          hasNewerLatestTask: true,
          isFollowingLatest: false,
          isAttached: false,
          isStaleSnapshot: true,
        },
        lifecycleSummary: {
          stage: "running",
          statusLabel: "Dispatch running",
          tone: "primary",
          summary: "Worker execution is active.",
          progressPercent: 52,
          progressSummary: "Running fit updates",
          backendStatusLabel: "running",
          workerTaskName: "characterization_run_task",
          submissionSourceLabel: "Active dataset session",
          acceptedAt: "2026-03-13 12:00:00",
          lastUpdatedAt: "2026-03-13 12:04:00",
          taskDatasetId: "fluxonium-2026-003",
          dispatchKey: "dispatch:80:characterization",
          requestReady: true,
          submittedFromActiveDataset: true,
          executionMode: "run",
          visibilityScope: "workspace",
        },
        eventHistorySummary: {
          total: 2,
          infoCount: 1,
          warningCount: 1,
          errorCount: 0,
          latestEventLabel: "Running",
          latestOccurredAt: "2026-03-13 12:04:00",
          dispatchStatusLabel: "Running",
          progressLabel: "running · 52%",
          terminalStateLabel: "Execution active",
        },
        resultSummary: {
          metadataRecordCount: 0,
          resultHandleCount: 1,
          materializedHandleCount: 0,
          pendingHandleCount: 1,
          hasTracePayload: false,
          traceBatchId: null,
          analysisRunId: null,
          handleKindCounts: [{ kind: "fit_summary", count: 1 }],
        },
      }),
    ).toMatchObject({
      persistenceLabel: "Persisted snapshot #79 retained during reattach",
      warningEventCount: 1,
      cards: [
        {
          id: "attachment",
          value: "Holding #79",
          tone: "warning",
        },
        {
          id: "dispatch",
          value: "Dispatch running",
          tone: "primary",
        },
        {
          id: "events",
          value: "Running",
          tone: "warning",
        },
        {
          id: "results",
          value: "1 pending",
          tone: "primary",
        },
      ],
    });
  });
});
