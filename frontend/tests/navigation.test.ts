import { describe, expect, it } from "vitest";

import {
  isWorkspaceNavigationItemActive,
  resolveWorkspacePageIdentity,
  workspaceNavigation,
  workspaceNavigationGroups,
} from "../src/lib/navigation";

describe("workspaceNavigation", () => {
  it("covers the canonical shell route families", () => {
    expect(workspaceNavigation).toHaveLength(6);
    expect(workspaceNavigation.map((item) => item.label)).toEqual([
      "Dashboard",
      "Raw Data",
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
      sectionLabel: "Dashboard",
      pageTitle: "Dashboard",
    });
    expect(resolveWorkspacePageIdentity("/schemas")).toEqual({
      sectionLabel: "Circuit Simulation",
      pageTitle: "Schemas",
    });
    expect(resolveWorkspacePageIdentity("/circuit-definition-editor")).toEqual({
      sectionLabel: "Circuit Simulation",
      pageTitle: "Schema Editor",
    });
    expect(resolveWorkspacePageIdentity("/raw-data")).toEqual({
      sectionLabel: "Pipeline",
      pageTitle: "Raw Data Browser",
    });
  });

  it("does not treat the schema editor route as an active alias of the schemas nav item", () => {
    const schemasNavItem = workspaceNavigation.find((item) => item.href === "/schemas");

    expect(schemasNavItem).toBeDefined();
    expect(schemasNavItem?.aliases ?? []).not.toContain("/circuit-definition-editor");
    expect(isWorkspaceNavigationItemActive(schemasNavItem!, "/schemas")).toBe(true);
    expect(isWorkspaceNavigationItemActive(schemasNavItem!, "/circuit-definition-editor")).toBe(
      false,
    );
  });
});
