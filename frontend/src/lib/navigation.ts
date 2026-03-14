import type { LucideIcon } from "lucide-react";
import {
  ActivitySquare,
  Binary,
  CircuitBoard,
  Database,
  FilePenLine,
  LayoutDashboard,
} from "lucide-react";

export type WorkspaceNavigationItem = Readonly<{
  href: string;
  label: string;
  summary: string;
  group: "dashboard" | "pipeline" | "circuit-workbench";
  pageTitle?: string;
  icon: LucideIcon;
  aliases?: readonly string[];
}>;

export const workspaceNavigation: readonly WorkspaceNavigationItem[] = [
  {
    href: "/dashboard",
    label: "Dashboard",
    pageTitle: "Dashboard",
    summary: "Review session-backed workspace context before entering a workflow surface.",
    group: "dashboard",
    icon: LayoutDashboard,
    aliases: ["/"],
  },
  {
    href: "/data-browser",
    label: "Data Browser",
    pageTitle: "Raw Data Browser",
    summary: "Inspect dataset catalogs, metadata summaries, and lineage within the active workspace.",
    group: "pipeline",
    icon: Database,
  },
  {
    href: "/circuit-definition-editor",
    label: "Schemas",
    pageTitle: "Schema Editor",
    summary: "Edit canonical circuit definitions with validation-ready structure.",
    group: "circuit-workbench",
    icon: FilePenLine,
  },
  {
    href: "/circuit-schemdraw",
    label: "Schemdraw",
    summary: "Preview canonical schematics generated from circuit definitions.",
    group: "circuit-workbench",
    icon: CircuitBoard,
  },
  {
    href: "/circuit-simulation",
    label: "Simulation",
    pageTitle: "Circuit Simulation",
    summary: "Stage simulation runs, sweeps, and result inspection workflows.",
    group: "circuit-workbench",
    icon: ActivitySquare,
  },
  {
    href: "/characterization",
    label: "Characterization",
    summary:
      "Run shared characterization, post-processing, fitting, and comparison workflows.",
    group: "pipeline",
    icon: Binary,
    aliases: ["/analysis"],
  },
] as const;

export type WorkspaceNavigationGroup = Readonly<{
  id: WorkspaceNavigationItem["group"];
  label: string;
  items: readonly WorkspaceNavigationItem[];
}>;

export const workspaceNavigationGroups: readonly WorkspaceNavigationGroup[] = [
  {
    id: "dashboard",
    label: "Dashboard",
    items: workspaceNavigation.filter((item) => item.group === "dashboard"),
  },
  {
    id: "pipeline",
    label: "Pipeline",
    items: workspaceNavigation.filter((item) => item.group === "pipeline"),
  },
  {
    id: "circuit-workbench",
    label: "Circuit Simulation",
    items: workspaceNavigation.filter((item) => item.group === "circuit-workbench"),
  },
] as const;

export type WorkspaceNavigationMatch = Readonly<{
  item: WorkspaceNavigationItem;
  group: WorkspaceNavigationGroup;
}>;

function matchesWorkspacePath(pathname: string, path: string) {
  return pathname === path || pathname.startsWith(`${path}/`);
}

export function resolveWorkspaceNavigationMatch(
  pathname: string,
): WorkspaceNavigationMatch | null {
  const item =
    workspaceNavigation.find((candidate) =>
      [candidate.href, ...(candidate.aliases ?? [])].some((path) =>
        matchesWorkspacePath(pathname, path),
      ),
    ) ?? null;

  if (!item) {
    return null;
  }

  const group =
    workspaceNavigationGroups.find((candidate) => candidate.id === item.group) ?? null;

  if (!group) {
    return null;
  }

  return {
    item,
    group,
  };
}

export function resolveWorkspacePageIdentity(pathname: string) {
  const match = resolveWorkspaceNavigationMatch(pathname);
  if (!match) {
    return {
      routeFamily: "Workspace",
      pageTitle: "Superconducting Circuits Workbench",
      summary: "Shared shell context for datasets, queue activity, and research workflows.",
    } as const;
  }

  return {
    routeFamily: match.group.label,
    pageTitle: match.item.pageTitle ?? match.item.label,
    summary: match.item.summary,
  } as const;
}
