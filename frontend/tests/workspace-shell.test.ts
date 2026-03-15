import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

const shellSource = readFileSync(
  fileURLToPath(new URL("../src/components/layout/workspace-shell.tsx", import.meta.url)),
  "utf8",
);
const headerSource = readFileSync(
  fileURLToPath(new URL("../src/components/layout/workspace-header.tsx", import.meta.url)),
  "utf8",
);
const navSource = readFileSync(
  fileURLToPath(new URL("../src/components/layout/workspace-nav.tsx", import.meta.url)),
  "utf8",
);
const authEntrySource = readFileSync(
  fileURLToPath(new URL("../src/components/layout/auth-entry-surface.tsx", import.meta.url)),
  "utf8",
);
const statusStripSource = readFileSync(
  fileURLToPath(new URL("../src/components/layout/workspace-status-strip.tsx", import.meta.url)),
  "utf8",
);
const loginPageSource = readFileSync(
  fileURLToPath(new URL("../src/app/login/page.tsx", import.meta.url)),
  "utf8",
);
const logoutPageSource = readFileSync(
  fileURLToPath(new URL("../src/app/logout/page.tsx", import.meta.url)),
  "utf8",
);

describe("workspace shell source contracts", () => {
  it("keeps the sticky header layered above the sidebar and gives the hamburger trigger feedback", () => {
    expect(shellSource).toContain("sticky top-0 z-50");
    expect(shellSource).toContain("z-30 w-[220px]");
    expect(shellSource).toContain("hover:border-primary/35 hover:bg-primary/10");
    expect(shellSource).toContain("focus-visible:ring-2");
  });

  it("keeps header page identity concise", () => {
    expect(headerSource).toContain("identity.pageTitle");
    expect(headerSource).toContain("identity.sectionLabel");
    expect(headerSource).not.toContain("identity.summary");
    expect(headerSource).not.toContain("WORKSPACE SURFACE");
  });

  it("keeps the sidebar title-only without intro copy, item summaries, or active badges", () => {
    expect(navSource).toContain("Superconducting Circuits");
    expect(navSource).not.toContain("Research Workbench");
    expect(navSource).toContain("group.label");
    expect(navSource).toContain("item.label");
    expect(navSource).not.toContain("Open dashboard");
    expect(navSource).not.toContain("item.summary");
    expect(navSource).not.toContain("active route");
    expect(navSource).not.toContain("Session-backed landing and shell context.");
  });

  it("moves the secondary shell identity into the header instead of duplicating it in the sidebar", () => {
    expect(headerSource).toContain("Research Workbench");
    expect(navSource).not.toContain("Research Workbench");
  });

  it("routes the collapsed active dataset trigger through the compact shell helper", () => {
    expect(statusStripSource).toContain("resolveShellActiveDatasetSummary");
    expect(statusStripSource).toContain("datasetSummary.value");
    expect(statusStripSource).toContain("datasetSummary.badge");
  });

  it("keeps workspace and dataset switchers inside the shared shell", () => {
    expect(statusStripSource).toContain("switchWorkspace(");
    expect(statusStripSource).toContain("Search Datasets");
    expect(statusStripSource).toContain("handleDatasetSelection(");
    expect(statusStripSource).toContain("syncRouteDataset(");
  });

  it("adopts explicit auth entry routes instead of disabled user-menu wording", () => {
    expect(headerSource).toContain("authSummary.primaryActionHref");
    expect(headerSource).not.toContain("Account settings are not expanded");
    expect(loginPageSource).toContain('mode="login"');
    expect(logoutPageSource).toContain('mode="logout"');
    expect(authEntrySource).toContain("useForm<LoginFormValues>");
    expect(authEntrySource).toContain("await login(values)");
    expect(authEntrySource).toContain("await logout()");
  });

  it("removes low-contrast auth-adjacent rose notices from the shared shell", () => {
    expect(statusStripSource).not.toContain("text-rose-100");
    expect(headerSource).not.toContain("text-rose-100");
  });
});
