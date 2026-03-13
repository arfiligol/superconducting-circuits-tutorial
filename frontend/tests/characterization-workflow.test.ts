import { describe, expect, it } from "vitest";

import { mapTaskDetailResponse } from "../src/lib/api/tasks";
import {
  parseCharacterizationTaskIdParam,
  resolveCharacterizationTaskId,
} from "../src/features/characterization/lib/task-id";
import {
  buildCharacterizationRequestSummary,
  filterCharacterizationTasks,
  groupCharacterizationResultHandles,
  resolveCharacterizationTaskAttachmentState,
  resolveCharacterizationTaskConnectionState,
  resolveCharacterizationTaskRecovery,
  resolveLatestCharacterizationTask,
  summarizeCharacterizationDispatch,
  summarizeCharacterizationTaskResults,
  summarizeCharacterizationTasks,
} from "../src/features/characterization/lib/workflow";

describe("characterization task routing helpers", () => {
  it("parses and resolves route task ids", () => {
    expect(parseCharacterizationTaskIdParam("41")).toBe(41);
    expect(parseCharacterizationTaskIdParam("bad")).toBeNull();
    expect(resolveCharacterizationTaskId(41, 55)).toBe(41);
    expect(resolveCharacterizationTaskId(null, 55)).toBe(55);
    expect(resolveCharacterizationTaskId(null, null)).toBeNull();
  });
});

describe("characterization workflow helpers", () => {
  const tasks = [
    {
      taskId: 41,
      kind: "characterization",
      lane: "characterization",
      executionMode: "run",
      status: "running",
      submittedAt: "2026-03-13 09:20:00",
      ownerUserId: "user-dev-01",
      ownerDisplayName: "Device Lab",
      workspaceId: "workspace-lab",
      workspaceSlug: "device-lab",
      visibilityScope: "workspace",
      datasetId: "fluxonium-2025-031",
      definitionId: null,
      summary: "Characterization request for Fluxonium sweep 031",
    },
    {
      taskId: 37,
      kind: "characterization",
      lane: "characterization",
      executionMode: "run",
      status: "completed",
      submittedAt: "2026-03-12 16:18:00",
      ownerUserId: "user-dev-01",
      ownerDisplayName: "Device Lab",
      workspaceId: "workspace-lab",
      workspaceSlug: "device-lab",
      visibilityScope: "workspace",
      datasetId: "fluxonium-2025-031",
      definitionId: null,
      summary: "Earlier characterization request",
    },
    {
      taskId: 29,
      kind: "simulation",
      lane: "simulation",
      executionMode: "run",
      status: "completed",
      submittedAt: "2026-03-12 12:00:00",
      ownerUserId: "user-dev-02",
      ownerDisplayName: "Simulation",
      workspaceId: "workspace-lab",
      workspaceSlug: "device-lab",
      visibilityScope: "workspace",
      datasetId: "fluxonium-2025-031",
      definitionId: 18,
      summary: "Simulation request",
    },
  ] as const;

  it("builds request summaries and filters characterization tasks", () => {
    expect(
      buildCharacterizationRequestSummary({
        datasetId: "fluxonium-2025-031",
        datasetName: "Fluxonium sweep 031",
        note: "fit refresh",
      }),
    ).toBe("Characterization request for Fluxonium sweep 031 · fit refresh");
    expect(resolveLatestCharacterizationTask(tasks)?.taskId).toBe(41);

    const filtered = filterCharacterizationTasks(tasks, {
      searchQuery: "fluxonium",
      scope: "dataset",
      statusFilter: "all",
      activeDatasetId: "fluxonium-2025-031",
    });

    expect(filtered.map((task) => task.taskId)).toEqual([41, 37]);
    expect(summarizeCharacterizationTasks(filtered)).toEqual({
      total: 2,
      activeCount: 1,
      completedCount: 1,
      failedCount: 0,
      resultBackedCount: 1,
    });
  });

  it("summarizes dispatch, result refs, and connection state", () => {
    const detail = mapTaskDetailResponse({
      task_id: 41,
      kind: "characterization",
      lane: "characterization",
      execution_mode: "run",
      status: "running",
      submitted_at: "2026-03-13 09:20:00",
      owner_user_id: "user-dev-01",
      owner_display_name: "Device Lab",
      workspace_id: "workspace-lab",
      workspace_slug: "device-lab",
      visibility_scope: "workspace",
      dataset_id: "fluxonium-2025-031",
      definition_id: null,
      summary: "Characterization request for Fluxonium sweep 031",
      queue_backend: "in_memory_scaffold",
      worker_task_name: "characterization_run_task",
      request_ready: true,
      submitted_from_active_dataset: true,
      dispatch: {
        dispatch_key: "dispatch:41:characterization_run_task",
        status: "running",
        submission_source: "active_dataset",
        accepted_at: "2026-03-13 09:20:00",
        last_updated_at: "2026-03-13 09:21:00",
      },
      events: [
        {
          event_key: "task-event-41-submitted",
          event_type: "task_submitted",
          level: "info",
          occurred_at: "2026-03-13 09:20:00",
          message: "Characterization task was submitted.",
          metadata: {
            task_id: 41,
            lane: "characterization",
          },
        },
        {
          event_key: "task-event-41-running",
          event_type: "task_running",
          level: "info",
          occurred_at: "2026-03-13 09:21:00",
          message: "Task entered the running state.",
          metadata: {
            progress_percent_complete: 58,
          },
        },
      ],
      progress: {
        phase: "running",
        percent_complete: 58,
        summary: "Fitting admittance curves",
        updated_at: "2026-03-13 09:21:00",
      },
      result_refs: {
        trace_batch_id: 44,
        analysis_run_id: 12,
        metadata_records: [
          {
            backend: "sqlite_metadata",
            record_type: "analysis_run",
            record_id: "analysis-run-12",
            version: 1,
            schema_version: "analysis-run/v1",
          },
        ],
        trace_payload: {
          contract_version: "trace-payload/v1",
          backend: "local_zarr",
          payload_role: "analysis_projection",
          store_key: "characterization-41",
          store_uri: "/data/characterization-41.zarr",
          group_path: "/fits",
          array_path: "/quality_factor",
          dtype: "float64",
          shape: [128],
          chunk_shape: [32],
          schema_version: "zarr/v2",
        },
        result_handles: [
          {
            contract_version: "result-handle/v1",
            handle_id: "handle-fit-41",
            kind: "fit_summary",
            status: "materialized",
            label: "Quality factor fit",
            metadata_record: {
              backend: "sqlite_metadata",
              record_type: "result_handle",
              record_id: "handle-fit-41",
              version: 1,
              schema_version: "result-handle/v1",
            },
            payload_backend: "json_artifact",
            payload_format: "json",
            payload_role: "report_artifact",
            payload_locator: "/artifacts/fit-41.json",
            provenance_task_id: 41,
            provenance: {
              source_dataset_id: "fluxonium-2025-031",
              source_task_id: 41,
              trace_batch_record: null,
              analysis_run_record: null,
            },
          },
          {
            contract_version: "result-handle/v1",
            handle_id: "handle-report-41",
            kind: "characterization_report",
            status: "pending",
            label: "Research summary",
            metadata_record: {
              backend: "sqlite_metadata",
              record_type: "result_handle",
              record_id: "handle-report-41",
              version: 1,
              schema_version: "result-handle/v1",
            },
            payload_backend: "markdown_artifact",
            payload_format: "markdown",
            payload_role: "report_artifact",
            payload_locator: null,
            provenance_task_id: 41,
            provenance: {
              source_dataset_id: "fluxonium-2025-031",
              source_task_id: 41,
              trace_batch_record: null,
              analysis_run_record: null,
            },
          },
        ],
      },
    });

    expect(summarizeCharacterizationDispatch(detail)).toEqual({
      stage: "running",
      statusLabel: "Dispatch running",
      tone: "primary",
      summary:
        "The worker is still producing characterization outputs. Progress and result refs remain recoverable from the persisted task contract.",
      submissionSourceLabel: "Active dataset session",
      acceptedAt: "2026-03-13 09:20:00",
      lastUpdatedAt: "2026-03-13 09:21:00",
    });
    expect(summarizeCharacterizationTaskResults(detail)).toEqual({
      metadataRecordCount: 1,
      resultHandleCount: 2,
      materializedHandleCount: 1,
      pendingHandleCount: 1,
      reportHandleCount: 1,
      fitSummaryCount: 1,
      plotBundleCount: 0,
      hasTracePayload: true,
      traceBatchId: 44,
      analysisRunId: 12,
    });
    expect(groupCharacterizationResultHandles(detail)).toEqual({
      materialized: [detail.resultRefs.resultHandles[0]],
      pending: [detail.resultRefs.resultHandles[1]],
    });
    expect(
      resolveCharacterizationTaskConnectionState({
        requestedTaskId: 37,
        resolvedTaskId: 37,
        latestTaskId: 41,
        activeTask: detail,
      }),
    ).toEqual({
      mode: "explicit",
      latestTaskId: 41,
      selectedTaskId: 37,
      attachedTaskId: 41,
      hasNewerLatestTask: true,
      isFollowingLatest: false,
    });
    expect(resolveCharacterizationTaskAttachmentState(detail, 37)).toEqual({
      isAttached: false,
      isStaleSnapshot: true,
    });
    expect(
      resolveCharacterizationTaskRecovery(37, 41, new Error("not found"))?.title,
    ).toBe("Task reattach available");
  });
});
