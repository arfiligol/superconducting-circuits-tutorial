"use client";

import { useState } from "react";
import { Menu, PanelLeftClose, PanelLeftOpen } from "lucide-react";

import { ThemeToggle } from "@/components/layout/theme-toggle";
import { WorkspaceHeader } from "@/components/layout/workspace-header";
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

      <header className="sticky top-0 z-20 border-b border-border bg-header/95 backdrop-blur">
        <div className="flex h-16 items-center gap-3 px-4 md:px-5">
          <button
            type="button"
            aria-label="Toggle navigation menu"
            onClick={() => setMobileSidebarOpen((open) => !open)}
            className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-border bg-surface-elevated text-foreground transition hover:border-primary hover:text-primary lg:hidden"
          >
            <Menu size={18} strokeWidth={2} />
          </button>

          <button
            type="button"
            aria-label={desktopSidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            onClick={() => setDesktopSidebarCollapsed((collapsed) => !collapsed)}
            className="hidden h-10 w-10 items-center justify-center rounded-xl border border-border bg-surface-elevated text-foreground transition hover:border-primary hover:text-primary lg:inline-flex"
          >
            {desktopSidebarCollapsed ? (
              <PanelLeftOpen size={18} strokeWidth={2} />
            ) : (
              <PanelLeftClose size={18} strokeWidth={2} />
            )}
          </button>

          <div className="min-w-0">
            <p className="truncate text-base font-semibold text-foreground md:text-lg">
              SC Tutorial App
            </p>
          </div>

          <div className="hidden min-w-0 flex-1 items-center lg:flex">
            <button
              type="button"
              disabled
              className="flex w-full items-center justify-between rounded-xl border border-border bg-surface px-4 py-2 text-left text-sm text-muted-foreground"
            >
              <span className="truncate">Active Datasets</span>
              <span className="rounded-full bg-muted px-2 py-0.5 text-[11px] uppercase tracking-[0.16em] text-foreground/80">
                API Pending
              </span>
            </button>
          </div>

          <ThemeToggle />
        </div>
      </header>

      <div className="flex min-h-[calc(100vh-4rem)]">
        <aside
          className={[
            "fixed inset-y-16 left-0 z-40 w-[220px] border-r border-border bg-sidebar px-3 py-5 transition-[transform,width,padding] duration-200 lg:static lg:inset-y-0 lg:translate-x-0 lg:shrink-0",
            mobileSidebarOpen ? "translate-x-0" : "-translate-x-full",
            desktopSidebarCollapsed ? "lg:w-0 lg:overflow-hidden lg:border-r-0 lg:px-0 lg:py-0" : "",
          ].join(" ")}
        >
          <WorkspaceNav onNavigate={closeSidebar} />
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <div className="border-b border-border bg-header px-4 py-3 lg:hidden">
            <button
              type="button"
              disabled
              className="flex w-full items-center justify-between rounded-xl border border-border bg-surface px-4 py-2 text-left text-sm text-muted-foreground"
            >
              <span className="truncate">Active Datasets</span>
              <span className="rounded-full bg-muted px-2 py-0.5 text-[11px] uppercase tracking-[0.16em] text-foreground/80">
                API Pending
              </span>
            </button>
          </div>

          <div className="hidden border-b border-border bg-header px-5 py-4 lg:block">
            <WorkspaceHeader />
          </div>

          <main className="flex-1 px-5 py-5 md:px-6 md:py-6">
            <div className="mx-auto flex w-full max-w-[1580px] flex-col gap-6">{children}</div>
          </main>
        </div>
      </div>
    </div>
  );
}
