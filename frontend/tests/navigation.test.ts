import { describe, expect, it } from "vitest";

import { workspaceNavigation, workspaceNavigationGroups } from "../src/lib/navigation";

describe("workspaceNavigation", () => {
  it("covers the rewrite foundation routes", () => {
    expect(workspaceNavigation).toHaveLength(5);
    expect(workspaceNavigation.map((item) => item.label)).toEqual([
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
    expect(workspaceNavigationGroups.map((group) => group.items.length)).toEqual([1, 1, 3]);
  });

  it("includes concise summaries and icons for the shell", () => {
    expect(workspaceNavigation.every((item) => typeof item.summary === "string")).toBe(true);
    expect(workspaceNavigation.every((item) => Boolean(item.icon))).toBe(true);
  });
});
