"use client";

import type {
  SessionAuthMode,
  SessionSnapshot,
  WorkspaceSwitchResult,
} from "@/lib/api/session";
import type { DatasetCatalogRow } from "@/features/data-browser/lib/contracts";
import type { TaskSummary } from "@/lib/api/tasks";
import type {
  ActiveDatasetSnapshot,
  ActiveDatasetSource,
  ActiveDatasetStatus,
} from "@/lib/app-state/active-dataset";
import type { AppSessionStatus } from "@/lib/app-state/app-session";
import { ApiError } from "@/lib/api/client";

export type ShellAuthViewState = "loading" | "authenticated" | "anonymous" | "degraded";

type ShellAuthSummaryInput = Readonly<{
  session: SessionSnapshot | undefined;
  status: AppSessionStatus;
  error: Error | undefined;
}>;

export function describeShellError(error: Error | undefined): string | null {
  if (!error) {
    return null;
  }

  if (error instanceof ApiError) {
    const errorCode = error.errorCode ? ` (${error.errorCode})` : "";
    const debugRef = error.debugRef ? ` · Ref ${error.debugRef}` : "";
    return `${error.message}${errorCode}${debugRef}`;
  }

  return error.message;
}

export function resolveShellAuthViewState({
  session,
  status,
  error,
}: ShellAuthSummaryInput): ShellAuthViewState {
  if (status === "loading" && !session && !error) {
    return "loading";
  }

  if (session?.authState === "degraded" || (status === "error" && !session)) {
    return "degraded";
  }

  return session?.authState ?? "anonymous";
}

export function resolveShellAuthModeLabel(mode: SessionAuthMode | undefined) {
  switch (mode) {
    case "jwt_cookie":
      return "JWT cookie";
    case "local_stub":
    default:
      return "Local stub";
  }
}

export function resolveShellAuthSummary(input: ShellAuthSummaryInput) {
  const state = resolveShellAuthViewState(input);
  const errorDetail = describeShellError(input.error);

  if (state === "loading") {
    return {
      state,
      tone: "info",
      badgeLabel: "Resolving",
      triggerName: "Session resolving",
      triggerDetail: "Checking session authority",
      menuTitle: "Resolving session",
      menuDescription: "The shell is still waiting for the backend session authority.",
      primaryActionHref: "/login",
      primaryActionLabel: "Go to login",
    } as const;
  }

  if (state === "authenticated") {
    const displayName = input.session?.user?.displayName ?? "Authenticated User";
    const workspaceName = input.session?.workspace.displayName ?? "Workspace pending";

    return {
      state,
      tone: "success",
      badgeLabel: "Authenticated",
      triggerName: displayName,
      triggerDetail: `${workspaceName} · ${resolveShellAuthModeLabel(input.session?.authMode)}`,
      menuTitle: "Authenticated session",
      menuDescription: input.session?.user?.email
        ? `${displayName} is signed in as ${input.session.user.email}.`
        : `${displayName} is signed in and backed by the shared session surface.`,
      primaryActionHref: "/logout",
      primaryActionLabel: "Log out",
    } as const;
  }

  if (state === "anonymous") {
    return {
      state,
      tone: "warning",
      badgeLabel: "Anonymous",
      triggerName: "Anonymous session",
      triggerDetail: "No authenticated user is attached to the shell session",
      menuTitle: "Anonymous session",
      menuDescription:
        "This shell is running without an authenticated user. Use the login entry to establish a session before trusting workspace actions.",
      primaryActionHref: "/login",
      primaryActionLabel: "Log in",
    } as const;
  }

  return {
    state,
    tone: "error",
    badgeLabel: "Degraded",
    triggerName: "Session degraded",
    triggerDetail: errorDetail ?? "The shell could not resolve a healthy session.",
    menuTitle: "Degraded session",
    menuDescription:
      errorDetail ??
      "The shell could not confirm the current session. Retry session resolution before trusting auth or workspace context.",
    primaryActionHref: "/login",
    primaryActionLabel: "Recover session",
  } as const;
}

export function resolveShellUserInitials(displayName: string | null | undefined) {
  const normalized = displayName?.trim();
  if (!normalized) {
    return "AN";
  }

  const parts = normalized.split(/\s+/).slice(0, 2);
  return parts
    .map((part) => part.charAt(0).toUpperCase())
    .join("")
    .slice(0, 2);
}

export function resolveShellTaskHref(task: Pick<TaskSummary, "lane" | "taskId">) {
  const basePath = task.lane === "characterization" ? "/characterization" : "/circuit-simulation";
  return `${basePath}?taskId=${task.taskId}`;
}

export function resolveShellTaskLabel(task: Pick<TaskSummary, "kind" | "executionMode">) {
  const kindLabel =
    task.kind === "post_processing"
      ? "Post-processing"
      : task.kind === "characterization"
        ? "Characterization"
        : "Simulation";

  return `${kindLabel} · ${task.executionMode === "smoke" ? "Smoke" : "Run"}`;
}

export function resolveShellWorkerSummary(
  workspace: SessionSnapshot["workspace"] | undefined,
  hasRuntimeSummary = false,
) {
  if (hasRuntimeSummary && workspace) {
    return {
      label: "Runtime Summary",
      value: "Connected",
      detail: `${workspace.displayName} runtime summary is available.`,
      tone: "success",
    } as const;
  }

  return {
    label: "Worker Summary",
    value: "Awaiting Authority",
    detail: workspace
      ? `${workspace.displayName} has no runtime summary surface yet.`
      : "Runtime summary is unavailable until the session resolves.",
    tone: "warning",
  } as const;
}

export function resolveShellActiveDatasetSummary(
  dataset: ActiveDatasetSnapshot | null,
  options: Readonly<{
    status: ActiveDatasetStatus;
    source: ActiveDatasetSource;
    errorDetail?: string | null;
    isUpdating: boolean;
  }>,
) {
  if (options.status === "syncing-route" || options.isUpdating) {
    return {
      value: "Syncing active dataset...",
      detail: "Session authority is updating the dataset selection.",
      badge: "Syncing",
    } as const;
  }

  if (options.errorDetail && !dataset) {
    return {
      value: "No active dataset",
      detail: options.errorDetail,
      badge: "Error",
    } as const;
  }

  if (!dataset) {
    return {
      value: "No active dataset",
      detail: "Select one from Raw Data to attach it to the session.",
      badge: null,
    } as const;
  }

  return {
    value: dataset.name ?? dataset.datasetId,
    detail: null,
    badge:
      dataset.status ??
      (options.source === "url" ? "Attached" : options.source === "session" ? "Session" : null),
  } as const;
}

export function resolveShellWorkspaceMemberships(
  memberships: SessionSnapshot["memberships"] | undefined,
) {
  if (!memberships) {
    return [];
  }

  const switchableMemberships = memberships.filter(
    (membership) => membership.allowedActions.switchTo || membership.isActive,
  );

  return [...switchableMemberships].sort((left, right) => {
    if (left.isActive === right.isActive) {
      return left.displayName.localeCompare(right.displayName);
    }
    return left.isActive ? -1 : 1;
  });
}

export function filterShellDatasets(
  rows: readonly DatasetCatalogRow[],
  query: string,
  activeDatasetId: string | null,
) {
  const normalizedQuery = query.trim().toLowerCase();
  const filteredRows =
    normalizedQuery.length === 0
      ? rows
      : rows.filter((row) =>
          [row.name, row.dataset_id, row.family, row.owner_display_name, row.device_type]
            .filter(Boolean)
            .some((value) => value.toLowerCase().includes(normalizedQuery)),
        );

  return [...filteredRows].sort((left, right) => {
    const leftActive = left.dataset_id === activeDatasetId;
    const rightActive = right.dataset_id === activeDatasetId;
    if (leftActive === rightActive) {
      return left.name.localeCompare(right.name);
    }
    return leftActive ? -1 : 1;
  });
}

export function resolveWorkspaceSwitchNotice(result: WorkspaceSwitchResult) {
  const detachedCount = result.detachedTaskIds.length;
  const detachedSuffix =
    detachedCount > 0
      ? ` ${detachedCount} task${detachedCount === 1 ? "" : "s"} detached from queue visibility.`
      : "";

  if (result.activeDatasetResolution === "preserved" && result.session.activeDataset) {
    return {
      tone: "success",
      message: `Workspace switched. Active dataset stayed on ${result.session.activeDataset.name}.${detachedSuffix}`,
    } as const;
  }

  if (result.activeDatasetResolution === "rebound" && result.session.activeDataset) {
    return {
      tone: "primary",
      message: `Workspace switched. Active dataset rebound to ${result.session.activeDataset.name}.${detachedSuffix}`,
    } as const;
  }

  return {
    tone: "warning",
    message: `Workspace switched. Active dataset was cleared for this workspace.${detachedSuffix}`,
  } as const;
}
