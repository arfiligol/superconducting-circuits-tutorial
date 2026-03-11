import Link from "next/link";

import { ThemeToggle } from "@/components/layout/theme-toggle";
import { workspaceNavigation } from "@/lib/navigation";

type WorkspaceShellProps = Readonly<{
  children: React.ReactNode;
}>;

export function WorkspaceShell({ children }: WorkspaceShellProps) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-6 px-4 py-4 md:px-6 lg:flex-row">
        <aside className="w-full rounded-[2rem] border border-border bg-card/90 p-5 shadow-sm backdrop-blur lg:max-w-xs">
          <div className="space-y-2">
            <p className="text-sm uppercase tracking-[0.24em] text-muted-foreground">
              Rewrite Foundation
            </p>
            <h1 className="text-2xl font-semibold">Superconducting Circuits Workbench</h1>
            <p className="text-sm leading-6 text-muted-foreground">
              Minimal App Router shell for migrating product surfaces without reusing legacy
              NiceGUI screens.
            </p>
          </div>

          <nav className="mt-8 space-y-2">
            {workspaceNavigation.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="block rounded-2xl border border-transparent bg-muted/50 px-4 py-3 transition hover:border-border hover:bg-muted"
              >
                <span className="block text-sm font-medium">{item.label}</span>
                <span className="mt-1 block text-xs text-muted-foreground">{item.description}</span>
              </Link>
            ))}
          </nav>
        </aside>

        <div className="flex min-h-[80vh] flex-1 flex-col gap-4">
          <header className="flex flex-col gap-3 rounded-[2rem] border border-border bg-card/90 px-5 py-4 shadow-sm backdrop-blur md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">
                Workspace Shell
              </p>
              <p className="mt-1 text-sm text-muted-foreground">
                Theme, navigation, and layout boundaries are ready for feature migration.
              </p>
            </div>
            <ThemeToggle />
          </header>

          <main className="flex-1">{children}</main>
        </div>
      </div>
    </div>
  );
}
