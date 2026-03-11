export type WorkspaceNavigationItem = Readonly<{
  href: string;
  label: string;
  description: string;
}>;

export const workspaceNavigation: readonly WorkspaceNavigationItem[] = [
  {
    href: "/data-browser",
    label: "Data Browser",
    description: "Inspect trace catalogs, metadata summaries, and lineage details.",
  },
  {
    href: "/circuit-definition-editor",
    label: "Circuit Definition Editor",
    description: "Edit canonical circuit definitions with validation-ready structure.",
  },
  {
    href: "/circuit-schemdraw",
    label: "Circuit Schemdraw",
    description: "Preview canonical schematics generated from circuit definitions.",
  },
  {
    href: "/circuit-simulation",
    label: "Circuit Simulation",
    description: "Stage simulation runs, sweeps, and result inspection workflows.",
  },
  {
    href: "/characterization",
    label: "Characterization",
    description: "Prepare shared analysis pipelines for simulation and measurement traces.",
  },
  {
    href: "/analysis",
    label: "Analysis",
    description: "Host post-processing, fitting, comparison, and reporting surfaces.",
  },
] as const;
