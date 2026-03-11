export type WorkspaceNavigationItem = Readonly<{
  href: string;
  label: string;
  description: string;
  group: "dashboard" | "pipeline" | "circuit-workbench";
  icon:
    | "database"
    | "file-json"
    | "circuit-board"
    | "flask-conical"
    | "activity"
    | "line-chart";
}>;

export const workspaceNavigation: readonly WorkspaceNavigationItem[] = [
  {
    href: "/data-browser",
    label: "Data Browser",
    description: "Inspect trace catalogs, metadata summaries, and lineage details.",
    group: "dashboard",
    icon: "database",
  },
  {
    href: "/circuit-definition-editor",
    label: "Circuit Definition Editor",
    description: "Edit canonical circuit definitions with validation-ready structure.",
    group: "circuit-workbench",
    icon: "file-json",
  },
  {
    href: "/circuit-schemdraw",
    label: "Circuit Schemdraw",
    description: "Preview canonical schematics generated from circuit definitions.",
    group: "circuit-workbench",
    icon: "circuit-board",
  },
  {
    href: "/circuit-simulation",
    label: "Circuit Simulation",
    description: "Stage simulation runs, sweeps, and result inspection workflows.",
    group: "circuit-workbench",
    icon: "flask-conical",
  },
  {
    href: "/characterization",
    label: "Characterization",
    description: "Prepare shared analysis pipelines for simulation and measurement traces.",
    group: "pipeline",
    icon: "activity",
  },
  {
    href: "/analysis",
    label: "Analysis",
    description: "Host post-processing, fitting, comparison, and reporting surfaces.",
    group: "pipeline",
    icon: "line-chart",
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
