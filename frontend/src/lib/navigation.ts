import type { LucideIcon } from "lucide-react";
import {
  ActivitySquare,
  Binary,
  CircuitBoard,
  Database,
  FilePenLine,
} from "lucide-react";

export type WorkspaceNavigationItem = Readonly<{
  href: string;
  label: string;
  summary: string;
  group: "dashboard" | "pipeline" | "circuit-workbench";
  icon: LucideIcon;
  aliases?: readonly string[];
}>;

export const workspaceNavigation: readonly WorkspaceNavigationItem[] = [
  {
    href: "/data-browser",
    label: "Data Browser",
    summary: "Inspect trace catalogs, metadata summaries, and lineage details.",
    group: "dashboard",
    icon: Database,
  },
  {
    href: "/circuit-definition-editor",
    label: "Schemas",
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
