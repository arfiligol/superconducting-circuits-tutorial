"use client";

import Link from "next/link";
import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowRight, LoaderCircle, LogIn, LogOut, RefreshCw } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { ShellNotice, type ShellNoticeTone } from "@/components/layout/shell-notice";
import {
  describeShellError,
  resolveShellAuthModeLabel,
  resolveShellAuthSummary,
  resolveShellUserInitials,
} from "@/components/layout/workspace-shell-contract";
import { cx } from "@/features/shared/components/surface-kit";
import { useAppSession } from "@/lib/app-state";

const loginFormSchema = z.object({
  username: z.string().trim().min(1, "Username is required."),
  password: z.string().min(1, "Password is required."),
});

type LoginFormValues = z.infer<typeof loginFormSchema>;

type AuthEntrySurfaceProps = Readonly<{
  mode: "login" | "logout";
}>;

type MutationNotice = Readonly<{
  tone: ShellNoticeTone;
  title: string;
  description: string;
}> | null;

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

function FieldLabel({
  htmlFor,
  label,
}: Readonly<{
  htmlFor: string;
  label: string;
}>) {
  return (
    <label
      htmlFor={htmlFor}
      className="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground"
    >
      {label}
    </label>
  );
}

export function AuthEntrySurface({ mode }: AuthEntrySurfaceProps) {
  const { session, sessionError, status, refreshSession, login, logout } = useAppSession();
  const authSummary = resolveShellAuthSummary({
    session,
    status,
    error: sessionError,
  });
  const initials = resolveShellUserInitials(authSummary.triggerName);
  const sessionErrorDetail = describeShellError(sessionError);
  const isLogin = mode === "login";
  const [mutationNotice, setMutationNotice] = useState<MutationNotice>(null);
  const [isSubmittingLogout, setIsSubmittingLogout] = useState(false);
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginFormSchema),
    defaultValues: {
      username: "",
      password: "",
    },
  });
  const isSubmittingLogin = form.formState.isSubmitting;
  const isMutating = isSubmittingLogin || isSubmittingLogout;
  const alternateAction =
    isLogin && authSummary.state === "authenticated"
      ? {
          href: "/logout",
          label: "Review logout",
          icon: <LogOut className="h-4 w-4" />,
        }
      : !isLogin && authSummary.state !== "authenticated"
        ? {
            href: "/login",
            label: "Go to login",
            icon: <LogIn className="h-4 w-4" />,
          }
        : null;

  const title = isLogin
    ? authSummary.state === "authenticated"
      ? "You are already signed in."
      : authSummary.state === "degraded"
        ? "Recover the session and sign in again."
        : authSummary.state === "loading"
          ? "Resolving shell session..."
          : "Sign in to continue."
    : authSummary.state === "authenticated"
      ? "Sign out from this shell session."
      : authSummary.state === "degraded"
        ? "Resolve the session before logging out."
        : authSummary.state === "loading"
          ? "Resolving session before logout..."
          : "This shell is already signed out.";
  const description = isLogin
    ? authSummary.state === "authenticated"
      ? "The shared session already has an authenticated user. Return to the app or sign out first if you need a different session."
      : "This page uses the shared app session as the only auth authority. A successful login is only trusted after the canonical session surface refreshes."
    : authSummary.state === "authenticated"
      ? "Signing out clears the current backend-backed session and then refreshes the shared shell authority."
      : "Logout remains a session-owned flow. If the shell is already anonymous or degraded, resolve the session state before treating logout as complete.";

  async function handleLogin(values: LoginFormValues) {
    setMutationNotice(null);

    try {
      const nextSession = await login(values);

      if (nextSession?.authState === "authenticated") {
        form.reset({
          username: values.username,
          password: "",
        });
        setMutationNotice({
          tone: "success",
          title: "Login complete",
          description: nextSession.user?.email
            ? `Signed in as ${nextSession.user.email}.`
            : `Signed in as ${nextSession.user?.displayName ?? values.username}.`,
        });
        return;
      }

      setMutationNotice({
        tone: "error",
        title: "Session did not attach",
        description:
          "The login request returned, but the canonical session surface did not resolve as authenticated.",
      });
    } catch (error) {
      setMutationNotice({
        tone: "error",
        title: "Login failed",
        description:
          describeShellError(error instanceof Error ? error : undefined) ??
          "The shell could not complete the login request.",
      });
    }
  }

  async function handleLogout() {
    setMutationNotice(null);
    setIsSubmittingLogout(true);

    try {
      const nextSession = await logout();
      if (!nextSession || nextSession.authState === "anonymous") {
        setMutationNotice({
          tone: "success",
          title: "Logout complete",
          description: "The shared session now reports an anonymous shell state.",
        });
        return;
      }

      setMutationNotice({
        tone: "error",
        title: "Session still attached",
        description:
          "The logout request completed, but the canonical session surface still resolved as authenticated.",
      });
    } catch (error) {
      setMutationNotice({
        tone: "error",
        title: "Logout failed",
        description:
          describeShellError(error instanceof Error ? error : undefined) ??
          "The shell could not complete the logout request.",
      });
    } finally {
      setIsSubmittingLogout(false);
    }
  }

  return (
    <main className="min-h-screen bg-app px-4 py-10 text-foreground md:px-6">
      <div className="mx-auto flex w-full max-w-[980px] flex-col gap-6">
        <section className="rounded-[1.4rem] border border-border bg-card px-6 py-6 shadow-[0_18px_50px_rgba(15,23,42,0.16)]">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
            <div className="min-w-0">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                {isLogin ? "Login" : "Logout"}
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
            <ActionLink
              href="/dashboard"
              label="Return to app"
              icon={<ArrowRight className="h-4 w-4" />}
            />
            {alternateAction ? (
              <ActionLink
                href={alternateAction.href}
                label={alternateAction.label}
                icon={alternateAction.icon}
                secondary
              />
            ) : null}
            <button
              type="button"
              onClick={() => {
                void refreshSession();
              }}
              className="inline-flex cursor-pointer items-center justify-center gap-2 rounded-[0.95rem] border border-border bg-surface px-4 py-3 text-sm font-medium text-foreground transition hover:border-primary/35 hover:bg-primary/10"
            >
              <RefreshCw
                className={cx("h-4 w-4", status === "refreshing" ? "animate-spin" : undefined)}
              />
              Refresh session
            </button>
          </div>
        </section>

        <ShellNotice tone={authSummary.tone} title={authSummary.menuTitle}>
          {authSummary.menuDescription}
        </ShellNotice>

        {mutationNotice ? (
          <ShellNotice tone={mutationNotice.tone} title={mutationNotice.title}>
            {mutationNotice.description}
          </ShellNotice>
        ) : null}

        {sessionErrorDetail ? (
          <ShellNotice tone="error" title="Session Error">
            {sessionErrorDetail}
          </ShellNotice>
        ) : null}

        <section className="grid gap-4 lg:grid-cols-[minmax(0,1.4fr)_minmax(0,0.9fr)]">
          <div className="rounded-[1.2rem] border border-border bg-card px-5 py-5 shadow-[0_10px_28px_rgba(15,23,42,0.08)]">
            {isLogin ? (
              authSummary.state === "authenticated" ? (
                <ShellNotice tone="success" title="Authenticated">
                  This shell is already authenticated. Sign out first if you need to replace the
                  current local session.
                </ShellNotice>
              ) : (
                <form className="space-y-4" onSubmit={form.handleSubmit(handleLogin)}>
                  <div>
                    <FieldLabel htmlFor="login-username" label="Username" />
                    <input
                      id="login-username"
                      autoComplete="username"
                      {...form.register("username")}
                      className="mt-2 w-full rounded-[0.95rem] border border-border bg-surface px-3.5 py-3 text-sm text-foreground outline-none transition placeholder:text-muted-foreground focus:border-primary/45 focus:ring-2 focus:ring-primary/20"
                      placeholder="lab.operator"
                    />
                    {form.formState.errors.username ? (
                      <p className="mt-2 text-sm text-rose-900">
                        {form.formState.errors.username.message}
                      </p>
                    ) : null}
                  </div>

                  <div>
                    <FieldLabel htmlFor="login-password" label="Password" />
                    <input
                      id="login-password"
                      type="password"
                      autoComplete="current-password"
                      {...form.register("password")}
                      className="mt-2 w-full rounded-[0.95rem] border border-border bg-surface px-3.5 py-3 text-sm text-foreground outline-none transition placeholder:text-muted-foreground focus:border-primary/45 focus:ring-2 focus:ring-primary/20"
                      placeholder="Enter the local session password"
                    />
                    {form.formState.errors.password ? (
                      <p className="mt-2 text-sm text-rose-900">
                        {form.formState.errors.password.message}
                      </p>
                    ) : null}
                  </div>

                  <div className="flex flex-wrap items-center gap-3 pt-1">
                    <button
                      type="submit"
                      disabled={isMutating}
                      className="inline-flex cursor-pointer items-center justify-center gap-2 rounded-[0.95rem] border border-primary/35 bg-primary/10 px-4 py-3 text-sm font-medium text-foreground transition hover:border-primary/50 hover:bg-primary/16 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {isSubmittingLogin ? (
                        <LoaderCircle className="h-4 w-4 animate-spin" />
                      ) : (
                        <LogIn className="h-4 w-4" />
                      )}
                      Log in
                    </button>
                    <p className="text-xs leading-5 text-muted-foreground">
                      The shell trusts login only after the canonical session surface refreshes as
                      authenticated.
                    </p>
                  </div>
                </form>
              )
            ) : authSummary.state === "authenticated" ? (
              <div className="space-y-4">
                <ShellNotice tone="warning" title="Confirm logout">
                  This will clear the current backend-backed shell session and return the app to an
                  anonymous state.
                </ShellNotice>
                <button
                  type="button"
                  onClick={() => {
                    void handleLogout();
                  }}
                  disabled={isMutating}
                  className="inline-flex cursor-pointer items-center justify-center gap-2 rounded-[0.95rem] border border-rose-600/35 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-950 transition hover:border-rose-700/45 hover:bg-rose-100 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isSubmittingLogout ? (
                    <LoaderCircle className="h-4 w-4 animate-spin" />
                  ) : (
                    <LogOut className="h-4 w-4" />
                  )}
                  Log out
                </button>
              </div>
            ) : (
              <ShellNotice tone={authSummary.state === "degraded" ? "error" : "info"} title="No logout action needed">
                {authSummary.state === "anonymous"
                  ? "The shell is already anonymous. Use the login entry if you need to establish a session."
                  : "Resolve the session first, then retry logout only if the shell becomes authenticated."}
              </ShellNotice>
            )}
          </div>

          <section className="grid gap-4">
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
                {session?.authMode ? resolveShellAuthModeLabel(session.authMode) : "Pending"}
              </p>
            </div>
          </section>
        </section>
      </div>
    </main>
  );
}
