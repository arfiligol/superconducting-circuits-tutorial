"use client";

import { usePathname } from "next/navigation";

import { workspaceNavigation } from "@/lib/navigation";

export function WorkspaceHeader() {
  const pathname = usePathname();
  const activeSurface = workspaceNavigation.find(
    (item) =>
      [item.href, ...(item.aliases ?? [])].some(
        (path) => pathname === path || pathname.startsWith(`${path}/`),
      ),
  );

  return (
    <div className="min-w-0">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
        Workspace Surface
      </p>
      <p className="mt-1 truncate text-base font-semibold text-foreground md:text-lg">
        {activeSurface?.label ?? "Superconducting Circuits Workbench"}
      </p>
      <p className="mt-1 hidden text-sm text-muted-foreground lg:block">
        {activeSurface?.summary ?? "Theme, navigation, and dense layout boundaries are ready for migration."}
      </p>
    </div>
  );
}
