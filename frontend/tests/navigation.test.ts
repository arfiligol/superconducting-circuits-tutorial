import { describe, expect, it } from "vitest";

import { workspaceNavigation } from "../src/lib/navigation";

describe("workspaceNavigation", () => {
  it("covers the rewrite foundation routes", () => {
    expect(workspaceNavigation).toHaveLength(6);
    expect(workspaceNavigation.map((item) => item.href)).toEqual([
      "/data-browser",
      "/circuit-definition-editor",
      "/circuit-schemdraw",
      "/circuit-simulation",
      "/characterization",
      "/analysis",
    ]);
  });

  it("keeps routes unique and absolute", () => {
    const hrefs = workspaceNavigation.map((item) => item.href);

    expect(new Set(hrefs).size).toBe(hrefs.length);
    expect(hrefs.every((href) => href.startsWith("/"))).toBe(true);
  });
});
