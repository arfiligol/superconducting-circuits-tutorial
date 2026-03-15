import { describe, expect, it } from "vitest";

import {
  filterShellDatasets,
  resolveShellActiveDatasetSummary,
  resolveShellTaskHref,
  resolveShellTaskLabel,
  resolveShellUserInitials,
  resolveShellWorkerSummary,
  resolveShellWorkspaceMemberships,
  resolveWorkspaceSwitchNotice,
} from "../src/components/layout/workspace-shell-contract";

describe("workspace shell contract helpers", () => {
  it("derives stable user initials for the header user menu", () => {
    expect(resolveShellUserInitials("Device Lab")).toBe("DL");
    expect(resolveShellUserInitials("  fluxonium  ")).toBe("F");
    expect(resolveShellUserInitials(null)).toBe("AN");
  });

  it("routes shell task links to the correct workflow family", () => {
    expect(resolveShellTaskHref({ lane: "simulation", taskId: 18 })).toBe(
      "/circuit-simulation?taskId=18",
    );
    expect(resolveShellTaskHref({ lane: "characterization", taskId: 31 })).toBe(
      "/characterization?taskId=31",
    );
  });

  it("formats task labels for queue entries and keeps worker slot authority explicit", () => {
    expect(
      resolveShellTaskLabel({
        kind: "simulation",
        executionMode: "run",
      }),
    ).toBe("Simulation · Run");
    expect(
      resolveShellTaskLabel({
        kind: "post_processing",
        executionMode: "smoke",
      }),
    ).toBe("Post-processing · Smoke");

    expect(
      resolveShellWorkerSummary({
        workspaceId: "ws-lab-a",
        slug: "lab-a",
        displayName: "Lab A",
        role: "owner",
        defaultTaskScope: "workspace",
        allowedActions: {
          switchTo: true,
          activateDataset: true,
          inviteMembers: true,
          removeMembers: true,
          transferOwner: true,
        },
      }),
    ).toEqual({
      label: "Worker Summary",
      value: "Awaiting Authority",
      detail: "Lab A has no runtime summary surface yet.",
      tone: "warning",
    });
  });

  it("keeps the collapsed active dataset trigger compact while staying single-authority", () => {
    expect(
      resolveShellActiveDatasetSummary(
        {
          datasetId: "fluxonium-2025-031",
          name: "Fluxonium sweep 031",
          owner: "Device Lab",
          family: "Fluxonium",
          status: "Ready",
          source: "session",
        },
        {
          status: "ready",
          source: "session",
          isUpdating: false,
        },
      ),
    ).toEqual({
      value: "Fluxonium sweep 031",
      detail: null,
      badge: "Ready",
    });

    expect(
      resolveShellActiveDatasetSummary(null, {
        status: "empty",
        source: "none",
        isUpdating: false,
      }),
    ).toEqual({
      value: "No active dataset",
      detail: "Select one from Raw Data to attach it to the session.",
      badge: null,
    });
  });

  it("derives switchable memberships and searchable dataset rows for shell switchers", () => {
    expect(
      resolveShellWorkspaceMemberships([
        {
          workspaceId: "ws-modeling",
          slug: "modeling",
          displayName: "Modeling",
          role: "member",
          defaultTaskScope: "owned",
          isActive: false,
          allowedActions: {
            switchTo: true,
            activateDataset: true,
            inviteMembers: false,
            removeMembers: false,
            transferOwner: false,
          },
        },
        {
          workspaceId: "ws-lab",
          slug: "lab",
          displayName: "Device Lab",
          role: "owner",
          defaultTaskScope: "workspace",
          isActive: true,
          allowedActions: {
            switchTo: true,
            activateDataset: true,
            inviteMembers: true,
            removeMembers: true,
            transferOwner: true,
          },
        },
      ]).map((membership) => membership.workspaceId),
    ).toEqual(["ws-lab", "ws-modeling"]);

    expect(
      filterShellDatasets(
        [
          {
            dataset_id: "resonator-chip-002",
            name: "Resonator chip 002",
            visibility_scope: "workspace",
            lifecycle_state: "active",
            device_type: "Resonator",
            updated_at: "2026-03-14T10:20:00Z",
            allowed_actions: {
              select: true,
              update_profile: true,
              publish: false,
              archive: false,
            },
            family: "Resonator",
            owner_display_name: "Modeling",
          },
          {
            dataset_id: "fluxonium-2025-031",
            name: "Fluxonium sweep 031",
            visibility_scope: "workspace",
            lifecycle_state: "active",
            device_type: "Fluxonium",
            updated_at: "2026-03-14T10:20:00Z",
            allowed_actions: {
              select: true,
              update_profile: true,
              publish: true,
              archive: true,
            },
            family: "Fluxonium",
            owner_display_name: "Device Lab",
          },
        ],
        "flux",
        "resonator-chip-002",
      ).map((row) => row.dataset_id),
    ).toEqual(["fluxonium-2025-031"]);
  });

  it("formats workspace switch notices from backend rebind outcomes", () => {
    expect(
      resolveWorkspaceSwitchNotice({
        session: {
          sessionId: "session-dev-001",
          authState: "authenticated",
          authMode: "local_stub",
          capabilities: {
            canSwitchWorkspace: true,
            canSwitchDataset: true,
            canInviteMembers: false,
            canRemoveMembers: false,
            canTransferWorkspaceOwner: false,
            canSubmitTasks: true,
            canManageWorkspaceTasks: false,
            canManageDefinitions: true,
            canManageDatasets: true,
            canViewAuditLogs: false,
          },
          canSubmitTasks: true,
          canManageDatasets: true,
          user: null,
          workspace: {
            workspaceId: "ws-modeling",
            slug: "modeling",
            displayName: "Modeling",
            role: "member",
            defaultTaskScope: "owned",
            allowedActions: {
              switchTo: true,
              activateDataset: true,
              inviteMembers: false,
              removeMembers: false,
              transferOwner: false,
            },
          },
          memberships: [],
          activeDataset: {
            datasetId: "transmon-coupler-014",
            name: "Transmon Coupler 014",
            family: "Transmon",
            status: "Review",
            ownerUserId: "user-dev-01",
            owner: "Device Lab",
            workspaceId: "ws-modeling",
            visibilityScope: "workspace",
            lifecycleState: "active",
          },
        },
        activeDatasetResolution: "rebound",
        detachedTaskIds: ["task_402"],
      }).message,
    ).toContain("rebound to Transmon Coupler 014");
  });
});
