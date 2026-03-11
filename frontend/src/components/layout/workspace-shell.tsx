"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  Activity,
  CircuitBoard,
  Database,
  FileJson2,
  FlaskConical,
  LineChart,
  Menu,
  PanelLeftClose,
  PanelLeftOpen,
} from "lucide-react";

import { ThemeToggle } from "@/components/layout/theme-toggle";
import { workspaceNavigationGroups } from "@/lib/navigation";

type WorkspaceShellProps = Readonly<{
  children: React.ReactNode;
}>;

export function WorkspaceShell({ children }: WorkspaceShellProps) {
  const pathname = usePathname();
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [desktopSidebarCollapsed, setDesktopSidebarCollapsed] = useState(false);

  function closeSidebar() {
    setMobileSidebarOpen(false);
  }

  function isActiveRoute(href: string) {
    return pathname === href || pathname.startsWith(`${href}/`);
  }

  function renderNavIcon(icon: string, active: boolean) {
    const className = active ? "text-primary-foreground" : "text-muted-foreground";

    switch (icon) {
      case "database":
        return <Database size={16} className={className} />;
      case "file-json":
        return <FileJson2 size={16} className={className} />;
      case "circuit-board":
        return <CircuitBoard size={16} className={className} />;
      case "flask-conical":
        return <FlaskConical size={16} className={className} />;
      case "activity":
        return <Activity size={16} className={className} />;
      case "line-chart":
        return <LineChart size={16} className={className} />;
      default:
        return null;
    }
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
          <div className="space-y-6">
            {workspaceNavigationGroups.map((group, groupIndex) => (
              <section
                key={group.id}
                className={groupIndex === 0 ? "" : "border-t border-border pt-5"}
              >
                <p className="px-3 text-[11px] font-bold uppercase tracking-[0.22em] text-muted-foreground">
                  {group.label}
                </p>
                <nav className="mt-2 space-y-1.5">
                  {group.items.map((item) => {
                    const active = isActiveRoute(item.href);

                    return (
                      <Link
                        key={item.href}
                        href={item.href}
                        onClick={closeSidebar}
                        className={[
                          "block rounded-xl px-3 py-3 transition",
                          active
                            ? "bg-primary/14 text-primary"
                            : "bg-transparent text-foreground hover:bg-surface-elevated",
                        ].join(" ")}
                      >
                        <span className="flex items-center gap-3">
                          <span className="shrink-0">{renderNavIcon(item.icon, active)}</span>
                          <span className="min-w-0 text-sm font-medium">{item.label}</span>
                        </span>
                      </Link>
                    );
                  })}
                </nav>
              </section>
            ))}
          </div>
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

          <main className="flex-1 px-5 py-5 md:px-6 md:py-6">
            <div className="mx-auto flex w-full max-w-[1580px] flex-col gap-6">{children}</div>
          </main>
        </div>
      </div>
    </div>
  );
}
