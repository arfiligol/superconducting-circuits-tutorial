"use client";

import { useState } from "react";
import { Menu, X } from "lucide-react";

import { ThemeToggle } from "@/components/layout/theme-toggle";
import { WorkspaceNav } from "@/components/layout/workspace-nav";

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
        <div className="flex h-[74px] items-center gap-4 px-4 md:px-6">
          <button
            type="button"
            aria-label="Toggle navigation menu"
            onClick={() => {
              setMobileSidebarOpen((open) => !open);
              setDesktopSidebarCollapsed((collapsed) => !collapsed);
            }}
            className="inline-flex h-10 w-10 items-center justify-center rounded-lg text-primary transition hover:bg-surface-elevated"
          >
            <Menu size={18} strokeWidth={2} />
          </button>

          <div className="min-w-0 shrink-0">
            <p className="truncate text-base font-semibold text-foreground md:text-lg">
              🔬 SC Tutorial App
            </p>
          </div>

          <div className="hidden min-w-0 flex-1 lg:flex">
            <div className="flex min-h-[48px] w-full items-center justify-between rounded-lg border border-border bg-surface px-3 py-2">
              <div className="min-w-0">
                <p className="text-[11px] font-medium text-muted-foreground">Active Datasets</p>
                <div className="mt-1 inline-flex max-w-full items-center gap-2 rounded-full bg-surface-elevated px-3 py-1.5 text-sm text-foreground">
                  <span className="truncate">FloatingQubitWithXYLine Post 0308_1819</span>
                  <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-muted text-muted-foreground">
                    <X size={12} />
                  </span>
                </div>
              </div>
              <div className="ml-3 flex items-center gap-3 text-muted-foreground">
                <X size={18} />
                <span className="text-xs">▾</span>
              </div>
            </div>
          </div>

          <ThemeToggle />
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
          <div className="border-b border-border bg-header px-4 py-3 lg:hidden">
            <div className="rounded-lg border border-border bg-surface px-3 py-2">
              <p className="text-[11px] font-medium text-muted-foreground">Active Datasets</p>
              <div className="mt-1 inline-flex max-w-full items-center gap-2 rounded-full bg-surface-elevated px-3 py-1.5 text-sm text-foreground">
                <span className="truncate">FloatingQubitWithXYLine Post 0308_1819</span>
                <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-muted text-muted-foreground">
                  <X size={12} />
                </span>
              </div>
            </div>
          </div>

          <main className="flex-1 px-4 py-5 md:px-6 md:py-5">
            <div className="mx-auto flex w-full max-w-[1600px] flex-col gap-6">{children}</div>
          </main>
        </div>
      </div>
    </div>
  );
}
