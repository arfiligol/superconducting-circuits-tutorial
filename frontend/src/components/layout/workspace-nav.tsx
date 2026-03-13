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
    <div className="space-y-8">
      {workspaceNavigationGroups.map((group, groupIndex) => (
        <section key={group.id} className={groupIndex === 0 ? "" : "border-t border-border pt-7"}>
          <p className="px-1 text-[12px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
            {group.label}
          </p>
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
                    "block rounded-lg px-1 py-2 transition",
                    active ? "text-primary" : "text-foreground hover:text-primary",
                  )}
                >
                  <span className="flex items-center gap-3">
                    <Icon
                      className={cx("h-5 w-5 shrink-0", active ? "text-primary" : "text-primary/80")}
                    />
                    <span className="min-w-0 text-[15px] font-medium">{item.label}</span>
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
