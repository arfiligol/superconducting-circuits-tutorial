"use client";

import Link from "next/link";
import { ArrowRight, LogIn, LogOut, RefreshCw } from "lucide-react";

import { ShellNotice } from "@/components/layout/shell-notice";
import {
  describeShellError,
  resolveShellAuthSummary,
  resolveShellUserInitials,
} from "@/components/layout/workspace-shell-contract";
import { cx } from "@/features/shared/components/surface-kit";
import { useAppSession } from "@/lib/app-state";

type AuthEntrySurfaceProps = Readonly<{
  mode: "login" | "logout";
}>;

function ActionLink({
  href,
  label,
  icon,
  secondary = false,
}: Readonly<{
  href: string;
  label: string;
  icon: React.ReactNode;
  secondary?: boolean;
}>) {
  return (
    <Link
      href={href}
      className={cx(
        "inline-flex items-center justify-center gap-2 rounded-[0.95rem] border px-4 py-3 text-sm font-medium transition",
        secondary
          ? "border-border bg-surface text-foreground hover:border-primary/35 hover:bg-primary/10"
          : "border-primary/35 bg-primary/10 text-foreground hover:border-primary/50 hover:bg-primary/14",
      )}
    >
      {icon}
      {label}
    </Link>
  );
}

export function AuthEntrySurface({ mode }: AuthEntrySurfaceProps) {
  const { session, sessionError, status, refreshSession } = useAppSession();
  const authSummary = resolveShellAuthSummary({
    session,
    status,
    error: sessionError,
  });
  const initials = resolveShellUserInitials(authSummary.triggerName);
  const sessionErrorDetail = describeShellError(sessionError);
  const isLogin = mode === "login";
  const heading = isLogin ? "Authentication Entry" : "Logout Entry";
  const title =
    authSummary.state === "authenticated"
      ? isLogin
        ? "You are already signed in."
        : "Review the authenticated session before leaving."
      : authSummary.state === "anonymous"
        ? isLogin
          ? "This shell is currently anonymous."
          : "The shell is already signed out or anonymous."
        : authSummary.state === "degraded"
          ? isLogin
            ? "Session recovery is required before sign-in can be trusted."
            : "Session recovery is required before sign-out can be trusted."
          : isLogin
            ? "Resolving authentication state..."
            : "Resolving session before logout...";
  const description =
    authSummary.state === "authenticated"
      ? "Header identity, workspace context, and user-menu state are all coming from the shared session surface. This entry keeps that authority explicit instead of inventing a separate auth state."
      : authSummary.state === "anonymous"
        ? "The app can now show a clear anonymous state and route you back into the workspace or the user-menu auth entry, even before a full sign-in mutation lands."
        : authSummary.state === "degraded"
          ? "Session authority could not be resolved cleanly. Fixing that comes before any trusted login or logout action."
          : "The app is still waiting for the backend-owned session surface to settle.";

  return (
    <main className="min-h-screen bg-app px-4 py-10 text-foreground md:px-6">
      <div className="mx-auto flex w-full max-w-[980px] flex-col gap-6">
        <section className="rounded-[1.4rem] border border-border bg-card px-6 py-6 shadow-[0_18px_50px_rgba(15,23,42,0.16)]">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
            <div className="min-w-0">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                {heading}
              </p>
              <h1 className="mt-3 text-[2rem] font-semibold tracking-tight text-foreground">
                {title}
              </h1>
              <p className="mt-3 max-w-3xl text-sm leading-6 text-muted-foreground">
                {description}
              </p>
            </div>

            <div className="flex items-center gap-4 rounded-[1rem] border border-border bg-surface px-4 py-4">
              <span className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-primary/12 text-sm font-semibold text-primary">
                {initials}
              </span>
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-foreground">
                  {authSummary.triggerName}
                </p>
                <p className="truncate text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  {authSummary.badgeLabel} session
                </p>
              </div>
            </div>
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <ActionLink href="/dashboard" label="Return to app" icon={<ArrowRight className="h-4 w-4" />} />
            <ActionLink
              href={authSummary.primaryActionHref}
              label={authSummary.primaryActionLabel}
              icon={isLogin ? <LogIn className="h-4 w-4" /> : <LogOut className="h-4 w-4" />}
              secondary
            />
            <button
              type="button"
              onClick={() => {
                void refreshSession();
              }}
              className="inline-flex cursor-pointer items-center justify-center gap-2 rounded-[0.95rem] border border-border bg-surface px-4 py-3 text-sm font-medium text-foreground transition hover:border-primary/35 hover:bg-primary/10"
            >
              <RefreshCw className={cx("h-4 w-4", status === "refreshing" ? "animate-spin" : undefined)} />
              Refresh session
            </button>
          </div>
        </section>

        <ShellNotice tone={authSummary.tone} title={authSummary.menuTitle}>
          {authSummary.menuDescription}
        </ShellNotice>

        {authSummary.state !== "authenticated" ? (
          <ShellNotice
            tone={authSummary.state === "degraded" ? "error" : "warning"}
            title={isLogin ? "Next Step" : "Current Logout State"}
          >
            {isLogin
              ? "Interactive sign-in transport is not exposed through the shared frontend session surface in this milestone. Use this page to confirm whether the shell is anonymous, degraded, or already authenticated."
              : "Interactive sign-out transport is not exposed through the shared frontend session surface in this milestone. Use this page to confirm whether the shell is already anonymous or needs session recovery."}
          </ShellNotice>
        ) : null}

        {sessionErrorDetail ? (
          <ShellNotice tone="error" title="Session Error">
            {sessionErrorDetail}
          </ShellNotice>
        ) : null}

        <section className="grid gap-4 md:grid-cols-3">
          <div className="rounded-[1rem] border border-border bg-surface px-4 py-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
              Auth State
            </p>
            <p className="mt-2 text-sm font-semibold text-foreground">{authSummary.badgeLabel}</p>
          </div>
          <div className="rounded-[1rem] border border-border bg-surface px-4 py-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
              Workspace
            </p>
            <p className="mt-2 text-sm font-semibold text-foreground">
              {session?.workspace.displayName ?? "Unavailable"}
            </p>
          </div>
          <div className="rounded-[1rem] border border-border bg-surface px-4 py-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
              Session Mode
            </p>
            <p className="mt-2 text-sm font-semibold text-foreground">
              {session?.authMode ?? "Pending"}
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}
