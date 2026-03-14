import { describe, expect, it } from "vitest";

import {
  canRetryRouteDatasetSync,
  parseDatasetIdFromSearch,
  resolveActiveDatasetId,
  resolveActiveDatasetSource,
  shouldAutoSyncRouteDataset,
} from "../src/lib/app-state/active-dataset-state";
import { resolveUrlSnapshot } from "../src/lib/app-state/url-state";
import { mapSessionResponse } from "../src/lib/api/session";
import { mapTaskSummaryResponse } from "../src/lib/api/tasks";
import {
  resolveLatestTask,
  resolveTaskQueueRefreshInterval,
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

  it("suppresses repeated automatic route sync after a failed attach until inputs change", () => {
    expect(
      shouldAutoSyncRouteDataset("route-dataset", "session-dataset", {
        targetDatasetId: null,
        status: "idle",
      }),
    ).toBe(true);
    expect(
      shouldAutoSyncRouteDataset("route-dataset", "session-dataset", {
        targetDatasetId: "route-dataset",
        status: "error",
      }),
    ).toBe(false);
    expect(
      canRetryRouteDatasetSync("route-dataset", "session-dataset", {
        targetDatasetId: "route-dataset",
        status: "error",
      }),
    ).toBe(true);
    expect(
      canRetryRouteDatasetSync("route-dataset", "route-dataset", {
        targetDatasetId: "route-dataset",
        status: "error",
      }),
    ).toBe(false);
  });
});

describe("url state snapshot helpers", () => {
  it("reuses the previous snapshot object when pathname and search are unchanged", () => {
    const snapshot = {
      pathname: "/circuit-simulation",
      search: "?definitionId=18&taskId=31",
    } as const;

    expect(resolveUrlSnapshot(snapshot, snapshot.pathname, snapshot.search)).toBe(snapshot);
  });

  it("returns a new snapshot when pathname or search changes", () => {
    const snapshot = {
      pathname: "/circuit-simulation",
      search: "?definitionId=18",
    } as const;

    expect(resolveUrlSnapshot(snapshot, "/circuit-simulation", "?definitionId=24")).toEqual({
      pathname: "/circuit-simulation",
      search: "?definitionId=24",
    });
    expect(resolveUrlSnapshot(snapshot, "/raw-data", "?datasetId=fluxonium-2025-031")).toEqual({
      pathname: "/raw-data",
      search: "?datasetId=fluxonium-2025-031",
    });
  });
});

describe("session contract mapping", () => {
  it("maps backend session payloads into the frontend session snapshot", () => {
    expect(
      mapSessionResponse({
        session_id: "session-dev-001",
        auth: {
          state: "authenticated",
          mode: "local_stub",
        },
        user: {
          id: "user-dev-01",
          display_name: "Device Lab",
          email: "device-lab@example.com",
          platform_role: "user",
        },
        workspace: {
          id: "workspace-lab",
          slug: "device-lab",
          name: "Device Lab",
          role: "owner",
          default_task_scope: "workspace",
          allowed_actions: {
            switch_to: true,
            activate_dataset: true,
            invite_members: true,
            remove_members: true,
            transfer_owner: true,
          },
        },
        memberships: [
          {
            id: "workspace-lab",
            slug: "device-lab",
            name: "Device Lab",
            role: "owner",
            default_task_scope: "workspace",
            is_active: true,
            allowed_actions: {
              switch_to: true,
              activate_dataset: true,
              invite_members: true,
              remove_members: true,
              transfer_owner: true,
            },
          },
        ],
        active_dataset: {
          id: "fluxonium-2025-031",
          name: "Fluxonium sweep 031",
          family: "Fluxonium",
          status: "Ready",
          owner_user_id: "user-dev-01",
          owner_display_name: "Device Lab",
          workspace_id: "workspace-lab",
          visibility_scope: "workspace",
          lifecycle_state: "active",
        },
        capabilities: {
          can_switch_workspace: false,
          can_switch_dataset: true,
          can_invite_members: true,
          can_remove_members: true,
          can_transfer_workspace_owner: true,
          can_submit_tasks: true,
          can_manage_workspace_tasks: true,
          can_manage_definitions: true,
          can_manage_datasets: true,
          can_view_audit_logs: false,
        },
      }),
    ).toEqual({
      sessionId: "session-dev-001",
      authState: "authenticated",
      authMode: "local_stub",
      canSubmitTasks: true,
      canManageDatasets: true,
      user: {
        userId: "user-dev-01",
        displayName: "Device Lab",
        email: "device-lab@example.com",
        platformRole: "user",
      },
      workspace: {
        workspaceId: "workspace-lab",
        slug: "device-lab",
        displayName: "Device Lab",
        role: "owner",
        defaultTaskScope: "workspace",
      },
      memberships: [
        {
          workspaceId: "workspace-lab",
          slug: "device-lab",
          displayName: "Device Lab",
          role: "owner",
          defaultTaskScope: "workspace",
          isActive: true,
        },
      ],
      activeDataset: {
        datasetId: "fluxonium-2025-031",
        name: "Fluxonium sweep 031",
        family: "Fluxonium",
        status: "Ready",
        ownerUserId: "user-dev-01",
        owner: "Device Lab",
        workspaceId: "workspace-lab",
        visibilityScope: "workspace",
        lifecycleState: "active",
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
        execution_mode: "run",
        status: "running",
        submitted_at: "2026-03-12 01:30:00",
        owner_user_id: "user-dev-01",
        owner_display_name: "Device Lab",
        workspace_id: "workspace-lab",
        workspace_slug: "device-lab",
        visibility_scope: "workspace",
        dataset_id: "fluxonium-2025-031",
        definition_id: 18,
        summary: "Fluxonium sweep queued from workspace",
      }),
    ).toEqual({
      taskId: 14,
      kind: "simulation",
      lane: "simulation",
      executionMode: "run",
      status: "running",
      submittedAt: "2026-03-12 01:30:00",
      ownerUserId: "user-dev-01",
      ownerDisplayName: "Device Lab",
      workspaceId: "workspace-lab",
      workspaceSlug: "device-lab",
      visibilityScope: "workspace",
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
        execution_mode: "run",
        status: "queued",
        submitted_at: "2026-03-12 01:20:00",
        owner_user_id: "user-dev-01",
        owner_display_name: "Device Lab",
        workspace_id: "workspace-lab",
        workspace_slug: "device-lab",
        visibility_scope: "workspace",
        dataset_id: "fluxonium-2025-031",
        definition_id: 18,
        summary: "Queued simulation",
      }),
      mapTaskSummaryResponse({
        task_id: 12,
        kind: "characterization",
        lane: "characterization",
        execution_mode: "run",
        status: "running",
        submitted_at: "2026-03-12 01:21:00",
        owner_user_id: "user-dev-01",
        owner_display_name: "Device Lab",
        workspace_id: "workspace-lab",
        workspace_slug: "device-lab",
        visibility_scope: "workspace",
        dataset_id: "fluxonium-2025-031",
        definition_id: 18,
        summary: "Running characterization",
      }),
      mapTaskSummaryResponse({
        task_id: 13,
        kind: "post_processing",
        lane: "characterization",
        execution_mode: "smoke",
        status: "failed",
        submitted_at: "2026-03-12 01:22:00",
        owner_user_id: "user-dev-01",
        owner_display_name: "Device Lab",
        workspace_id: "workspace-lab",
        workspace_slug: "device-lab",
        visibility_scope: "owned",
        dataset_id: "fluxonium-2025-031",
        definition_id: null,
        summary: "Failed post-processing",
      }),
      mapTaskSummaryResponse({
        task_id: 14,
        kind: "simulation",
        lane: "simulation",
        execution_mode: "run",
        status: "completed",
        submitted_at: "2026-03-12 01:23:00",
        owner_user_id: "user-dev-01",
        owner_display_name: "Device Lab",
        workspace_id: "workspace-lab",
        workspace_slug: "device-lab",
        visibility_scope: "workspace",
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

  it("keeps polling while the backend still reports active tasks", () => {
    const activeTasks = [
      mapTaskSummaryResponse({
        task_id: 21,
        kind: "simulation",
        lane: "simulation",
        execution_mode: "run",
        status: "running",
        submitted_at: "2026-03-12 01:40:00",
        owner_user_id: "user-dev-01",
        owner_display_name: "Device Lab",
        workspace_id: "workspace-lab",
        workspace_slug: "device-lab",
        visibility_scope: "workspace",
        dataset_id: "fluxonium-2025-031",
        definition_id: 18,
        summary: "Running simulation",
      }),
    ];
    const settledTasks = [
      mapTaskSummaryResponse({
        task_id: 22,
        kind: "simulation",
        lane: "simulation",
        execution_mode: "run",
        status: "completed",
        submitted_at: "2026-03-12 01:41:00",
        owner_user_id: "user-dev-01",
        owner_display_name: "Device Lab",
        workspace_id: "workspace-lab",
        workspace_slug: "device-lab",
        visibility_scope: "workspace",
        dataset_id: "fluxonium-2025-031",
        definition_id: 18,
        summary: "Completed simulation",
      }),
    ];

    expect(resolveTaskQueueRefreshInterval(activeTasks)).toBe(5_000);
    expect(resolveTaskQueueRefreshInterval(settledTasks)).toBe(0);
    expect(resolveLatestTask(activeTasks)?.taskId).toBe(21);
    expect(resolveLatestTask(settledTasks)?.taskId).toBe(22);
  });
});
