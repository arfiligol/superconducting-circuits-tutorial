"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { resolveWorkspaceNavigationMatch, workspaceNavigationGroups } from "@/lib/navigation";

function cx(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

type WorkspaceNavProps = Readonly<{
  onNavigate?: () => void;
}>;

export function WorkspaceNav({ onNavigate }: WorkspaceNavProps) {
  const pathname = usePathname();
  const activeMatch = resolveWorkspaceNavigationMatch(pathname);

  return (
    <div className="flex h-full flex-col gap-8">
      <div className="rounded-[1rem] border border-border bg-surface px-4 py-4">
        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
          Superconducting Circuits
        </p>
        <p className="mt-2 text-base font-semibold text-foreground">Research Workbench</p>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">
          Stable shell navigation for dataset, definition, simulation, and characterization
          workflows.
        </p>
        <Link
          href="/dashboard"
          onClick={onNavigate}
          className="mt-4 inline-flex rounded-md border border-border px-3 py-2 text-xs font-medium uppercase tracking-[0.16em] text-foreground transition hover:border-primary/40 hover:bg-primary/10"
        >
          Open dashboard
        </Link>
      </div>

      <div className="space-y-8">
        {workspaceNavigationGroups.map((group) => (
          <section key={group.id}>
            <div className="px-1">
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                {group.label}
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                {group.id === "dashboard"
                  ? "Session-backed landing and shell context."
                  : group.id === "pipeline"
                    ? "Dataset-driven browse and analysis surfaces."
                    : "Definition-driven design and research surfaces."}
              </p>
            </div>

            <nav className="mt-4 space-y-2">
              {group.items.map((item) => {
                const activePaths = [item.href, ...(item.aliases ?? [])];
                const active = activePaths.some(
                  (path) => pathname === path || pathname.startsWith(`${path}/`),
                );
                const Icon = item.icon;

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={onNavigate}
                    className={cx(
                      "block rounded-[0.95rem] border px-3 py-3 transition",
                      active
                        ? "border-primary/35 bg-primary/10 text-foreground"
                        : "border-transparent text-foreground hover:border-primary/20 hover:bg-surface hover:text-primary",
                    )}
                  >
                    <span className="flex items-start gap-3">
                      <span
                        className={cx(
                          "inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full",
                          active ? "bg-primary/12 text-primary" : "bg-surface text-primary/80",
                        )}
                      >
                        <Icon className="h-4 w-4" />
                      </span>
                      <span className="min-w-0">
                        <span className="block text-[15px] font-medium">{item.label}</span>
                        <span className="mt-1 block text-xs leading-5 text-muted-foreground">
                          {item.summary}
                        </span>
                        {activeMatch?.item.href === item.href ? (
                          <span className="mt-2 inline-flex rounded-full border border-primary/30 px-2.5 py-1 text-[10px] font-medium uppercase tracking-[0.16em] text-primary">
                            active route
                          </span>
                        ) : null}
                      </span>
                    </span>
                  </Link>
                );
              })}
            </nav>
          </section>
        ))}
      </div>
    </div>
  );
}
