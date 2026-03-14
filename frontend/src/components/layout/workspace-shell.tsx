"use client";

import { useState } from "react";
import { Menu } from "lucide-react";

import { WorkspaceHeader } from "@/components/layout/workspace-header";
import { WorkspaceNav } from "@/components/layout/workspace-nav";
import { WorkspaceStatusStrip } from "@/components/layout/workspace-status-strip";

type WorkspaceShellProps = Readonly<{
  children: React.ReactNode;
}>;

export function WorkspaceShell({ children }: WorkspaceShellProps) {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [desktopSidebarCollapsed, setDesktopSidebarCollapsed] = useState(false);

  function closeSidebar() {
    setMobileSidebarOpen(false);
  }

  return (
    <div className="min-h-screen bg-app text-foreground">
      {mobileSidebarOpen ? (
        <button
          type="button"
          aria-label="Close navigation menu"
          className="fixed inset-0 z-30 bg-slate-950/45 lg:hidden"
          onClick={closeSidebar}
        />
      ) : null}

      <header className="sticky top-0 z-20 border-b border-border bg-header shadow-[0_1px_0_rgba(255,255,255,0.04)]">
        <div className="flex min-h-[74px] items-center gap-4 px-4 py-4 md:px-6">
          <button
            type="button"
            aria-label="Toggle navigation menu"
            onClick={() => {
              if (window.innerWidth < 1024) {
                setMobileSidebarOpen((open) => !open);
                return;
              }

              setDesktopSidebarCollapsed((collapsed) => !collapsed);
            }}
            className="inline-flex h-10 w-10 items-center justify-center rounded-lg text-primary transition hover:bg-surface-elevated"
          >
            <Menu size={18} strokeWidth={2} />
          </button>

          <WorkspaceHeader />
        </div>

        <div className="border-t border-border/80 px-4 py-3 md:px-6">
          <WorkspaceStatusStrip compact />
        </div>
      </header>

      <div className="flex min-h-[calc(100vh-4rem)]">
        <aside
          className={[
            "fixed inset-y-[74px] left-0 z-40 w-[220px] border-r border-border bg-sidebar px-4 py-5 transition-[transform,width,padding] duration-200 lg:static lg:inset-y-0 lg:translate-x-0 lg:shrink-0",
            mobileSidebarOpen ? "translate-x-0" : "-translate-x-full",
            desktopSidebarCollapsed ? "lg:w-0 lg:overflow-hidden lg:border-r-0 lg:px-0 lg:py-0" : "",
          ].join(" ")}
        >
          <WorkspaceNav onNavigate={closeSidebar} />
        </aside>

        <div className="flex min-w-0 flex-1 flex-col bg-background">
          <main className="flex-1 px-4 py-5 md:px-6 md:py-5">
            <div className="mx-auto flex w-full max-w-[1600px] flex-col gap-6">{children}</div>
          </main>
        </div>
      </div>
    </div>
  );
}
