import { describe, expect, it } from "vitest";

import {
  resolveWorkspacePageIdentity,
  workspaceNavigation,
  workspaceNavigationGroups,
} from "../src/lib/navigation";

describe("workspaceNavigation", () => {
  it("covers the canonical shell route families", () => {
    expect(workspaceNavigation).toHaveLength(6);
    expect(workspaceNavigation.map((item) => item.label)).toEqual([
      "Dashboard",
      "Data Browser",
      "Schemas",
      "Schemdraw",
      "Simulation",
      "Characterization",
    ]);
  });

  it("keeps routes unique and absolute", () => {
    const hrefs = workspaceNavigation.map((item) => item.href);

    expect(new Set(hrefs).size).toBe(hrefs.length);
    expect(hrefs.every((href) => href.startsWith("/"))).toBe(true);
  });

  it("keeps the NiceGUI-style drawer grouping stable", () => {
    expect(workspaceNavigationGroups.map((group) => group.label)).toEqual([
      "Dashboard",
      "Pipeline",
      "Circuit Simulation",
    ]);
    expect(workspaceNavigationGroups.map((group) => group.items.length)).toEqual([1, 2, 3]);
  });

  it("includes concise summaries and icons for the shell", () => {
    expect(workspaceNavigation.every((item) => typeof item.summary === "string")).toBe(true);
    expect(workspaceNavigation.every((item) => Boolean(item.icon))).toBe(true);
  });

  it("realigns route family and page identity for header consumers", () => {
    expect(resolveWorkspacePageIdentity("/")).toEqual({
      routeFamily: "Dashboard",
      pageTitle: "Dashboard",
      summary: "Review session-backed workspace context before entering a workflow surface.",
    });
    expect(resolveWorkspacePageIdentity("/circuit-definition-editor")).toEqual({
      routeFamily: "Circuit Simulation",
      pageTitle: "Schema Editor",
      summary: "Edit canonical circuit definitions with validation-ready structure.",
    });
    expect(resolveWorkspacePageIdentity("/data-browser")).toEqual({
      routeFamily: "Pipeline",
      pageTitle: "Raw Data Browser",
      summary: "Inspect dataset catalogs, metadata summaries, and lineage within the active workspace.",
    });
  });
});
