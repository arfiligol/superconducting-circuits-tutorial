import { describe, expect, it } from "vitest";

import {
  resolveShellTaskHref,
  resolveShellTaskLabel,
  resolveShellUserInitials,
  resolveShellWorkerSummary,
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
      }),
    ).toEqual({
      label: "Worker Summary",
      value: "Awaiting Authority",
      detail: "Lab A has no runtime summary surface yet.",
      tone: "warning",
    });
  });
});
