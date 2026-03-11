"use client";

import { usePathname } from "next/navigation";

import { workspaceNavigation } from "@/lib/navigation";

export function WorkspaceHeader() {
  const pathname = usePathname();
  const activeSurface = workspaceNavigation.find((item) => item.href === pathname);

  return (
    <div>
      <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Workspace Surface</p>
      <p className="mt-1 text-lg font-semibold">
        {activeSurface?.label ?? "Superconducting Circuits Workbench"}
      </p>
      <p className="mt-1 text-sm text-muted-foreground">
        {activeSurface?.summary ?? "Theme, navigation, and dense layout boundaries are ready for migration."}
      </p>
    </div>
  );
}
