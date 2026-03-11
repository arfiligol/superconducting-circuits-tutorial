"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { workspaceNavigationGroups } from "@/lib/navigation";

function cx(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

type WorkspaceNavProps = Readonly<{
  onNavigate?: () => void;
}>;

export function WorkspaceNav({ onNavigate }: WorkspaceNavProps) {
  const pathname = usePathname();

  return (
    <div className="space-y-6">
      {workspaceNavigationGroups.map((group, groupIndex) => (
        <section key={group.id} className={groupIndex === 0 ? "" : "border-t border-border pt-5"}>
          <p className="px-3 text-[11px] font-bold uppercase tracking-[0.22em] text-muted-foreground">
            {group.label}
          </p>
          <nav className="mt-2 space-y-1.5">
            {group.items.map((item) => {
              const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
              const Icon = item.icon;

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={onNavigate}
                  className={cx(
                    "block rounded-xl px-3 py-3 transition",
                    active
                      ? "bg-primary/14 text-primary"
                      : "bg-transparent text-foreground hover:bg-surface-elevated",
                  )}
                >
                  <span className="flex items-center gap-3">
                    <Icon
                      className={cx("h-4 w-4 shrink-0", active ? "text-primary" : "text-muted-foreground")}
                    />
                    <span className="min-w-0 text-sm font-medium">{item.label}</span>
                  </span>
                </Link>
              );
            })}
          </nav>
        </section>
      ))}
    </div>
  );
}
