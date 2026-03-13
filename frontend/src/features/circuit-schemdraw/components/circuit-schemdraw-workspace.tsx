"use client";

import { useEffect, useState, useTransition } from "react";
import {
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  FileCode2,
  LoaderCircle,
  Package,
  RefreshCcw,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  Waypoints,
} from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

import { useCircuitSchemdrawData } from "@/features/circuit-schemdraw/hooks/use-circuit-schemdraw-data";
import {
  parseSchemdrawDefinitionIdParam,
} from "@/features/circuit-schemdraw/lib/definition-id";
import { inferSchemdrawReadiness } from "@/features/circuit-schemdraw/lib/readiness";
import {
  buildSchemdrawStructuredPreview,
  filterAndSortSchemdrawCatalog,
  partitionSchemdrawNotices,
  pinActiveSchemdrawDefinition,
  resolveSchemdrawAttachmentState,
  resolveSchemdrawSelectionRecovery,
  summarizeSchemdrawCatalog,
  type SchemdrawCatalogFilter,
  type SchemdrawCatalogSortMode,
  type SchemdrawPreviewMode,
} from "@/features/circuit-schemdraw/lib/workflow";
import {
  SurfacePanel,
  SurfaceStat,
  SurfaceTag,
  cx,
} from "@/features/shared/components/surface-kit";
import { ApiError } from "@/lib/api/client";

function definitionSearchHref(pathname: string, searchParamsValue: string, definitionId: string) {
  const params = new URLSearchParams(searchParamsValue);
  params.set("definitionId", definitionId);
  return `${pathname}?${params.toString()}`;
}

function lineCount(value: string) {
  return value.split("\n").length;
}

function readinessTone(status: "ready" | "warning" | "pending") {
  if (status === "ready") {
    return "success" as const;
  }

  if (status === "warning") {
    return "warning" as const;
  }

  return "default" as const;
}

function describeApiError(error: Error | undefined) {
  if (!error) {
    return null;
  }

  if (error instanceof ApiError) {
    const retryHint = error.retryable === true ? " Retry is available." : "";
    const debugHint = error.debugRef ? ` Ref: ${error.debugRef}.` : "";
    return `${error.message}${retryHint}${debugHint}`;
  }

  return error.message;
}

function artifactTone(artifact: string) {
  if (artifact.endsWith(".json")) {
    return "primary" as const;
  }

  if (artifact.endsWith(".yaml") || artifact.endsWith(".yml")) {
    return "success" as const;
  }

  return "default" as const;
}

type CatalogCardProps = Readonly<{
  createdAt: string;
  definitionId: number;
  elementCount: number;
  isActive: boolean;
  isAttachedSnapshot: boolean;
  isPinned: boolean;
  name: string;
  onSelect: (definitionId: number) => void;
  previewArtifactCount: number;
  validationStatus: "ok" | "warning";
}>;

function CatalogCard({
  createdAt,
  definitionId,
  elementCount,
  isActive,
  isAttachedSnapshot,
  isPinned,
  name,
  onSelect,
  previewArtifactCount,
  validationStatus,
}: CatalogCardProps) {
  return (
    <button
      type="button"
      onClick={() => {
        onSelect(definitionId);
      }}
      className={cx(
        "w-full cursor-pointer rounded-[1rem] border px-4 py-4 text-left shadow-[0_10px_30px_rgba(0,0,0,0.08)] transition",
        isActive
          ? "border-primary/40 bg-card"
          : "border-border bg-card hover:border-primary/25 hover:bg-primary/5",
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h2 className="truncate text-base font-semibold text-foreground">{name}</h2>
          <p className="mt-1 text-xs uppercase tracking-[0.14em] text-muted-foreground">
            Definition #{definitionId}
          </p>
        </div>
        <SurfaceTag tone={previewArtifactCount > 0 ? "primary" : "default"}>
          {previewArtifactCount} artifacts
        </SurfaceTag>
      </div>

      <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
        {isActive ? <SurfaceTag tone="primary">Active target</SurfaceTag> : null}
        {isAttachedSnapshot ? <SurfaceTag tone="success">Attached snapshot</SurfaceTag> : null}
        {isPinned ? <SurfaceTag tone="warning">Pinned while filtered</SurfaceTag> : null}
        <SurfaceTag tone={validationStatus === "warning" ? "warning" : "success"}>
          {validationStatus === "warning" ? "Warnings present" : "Validation clean"}
        </SurfaceTag>
      </div>

      <div className="mt-4 grid gap-2 text-xs text-muted-foreground sm:grid-cols-2">
        <span>Created: {createdAt}</span>
        <span className="sm:text-right">{elementCount} elements</span>
      </div>
    </button>
  );
}

export function CircuitSchemdrawWorkspace() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [isNavigating, startTransition] = useTransition();
  const [isRefreshingCatalog, setIsRefreshingCatalog] = useState(false);
  const [isRefreshingDefinition, setIsRefreshingDefinition] = useState(false);
  const [catalogQuery, setCatalogQuery] = useState("");
  const [catalogFilter, setCatalogFilter] = useState<SchemdrawCatalogFilter>("all");
  const [catalogSort, setCatalogSort] = useState<SchemdrawCatalogSortMode>("recent");
  const [previewMode, setPreviewMode] = useState<SchemdrawPreviewMode>("structured");

  const requestedDefinitionId = searchParams.get("definitionId");
  const rawDefinitionId = parseSchemdrawDefinitionIdParam(requestedDefinitionId);
  const {
    definitions,
    definitionsError,
    isDefinitionsLoading,
    resolvedDefinitionId,
    selectedDefinitionSummary,
    activeDefinition,
    activeDefinitionError,
    isDefinitionTransitioning,
    refreshDefinitions,
    refreshActiveDefinition,
  } = useCircuitSchemdrawData(rawDefinitionId);

  const readiness = inferSchemdrawReadiness(activeDefinition);
  const catalogSummary = summarizeSchemdrawCatalog(definitions);
  const filteredDefinitions = filterAndSortSchemdrawCatalog(definitions, {
    searchQuery: catalogQuery,
    filter: catalogFilter,
    sort: catalogSort,
  });
  const pinnedDefinitionId = pinActiveSchemdrawDefinition(
    filteredDefinitions,
    resolvedDefinitionId,
  );
  const pinnedDefinition =
    pinnedDefinitionId === null
      ? undefined
      : definitions?.find((definition) => definition.definition_id === pinnedDefinitionId);
  const selectionRecovery = resolveSchemdrawSelectionRecovery(
    requestedDefinitionId,
    resolvedDefinitionId,
    definitions,
  );
  const attachmentState = resolveSchemdrawAttachmentState(
    activeDefinition,
    resolvedDefinitionId,
  );
  const noticeGroups = partitionSchemdrawNotices(
    activeDefinition?.validation_notices ?? [],
  );
  const structuredPreview = buildSchemdrawStructuredPreview(
    activeDefinition?.normalized_output ?? '{\n  "schemdraw_ready": false\n}',
  );
  const activeDefinitionIndex =
    typeof resolvedDefinitionId === "number"
      ? (definitions ?? []).findIndex((definition) => definition.definition_id === resolvedDefinitionId)
      : -1;
  const previousDefinition =
    activeDefinitionIndex > 0 ? definitions?.[activeDefinitionIndex - 1] : undefined;
  const nextDefinition =
    activeDefinitionIndex >= 0 && definitions && activeDefinitionIndex < definitions.length - 1
      ? definitions[activeDefinitionIndex + 1]
      : undefined;
  const catalogErrorMessage = describeApiError(definitionsError);
  const activeDefinitionErrorMessage = describeApiError(activeDefinitionError);

  useEffect(() => {
    if (resolvedDefinitionId === null || resolvedDefinitionId === rawDefinitionId) {
      return;
    }

    startTransition(() => {
      router.replace(
        definitionSearchHref(pathname, searchParams.toString(), String(resolvedDefinitionId)),
        { scroll: false },
      );
    });
  }, [pathname, rawDefinitionId, resolvedDefinitionId, router, searchParams]);

  function replaceDefinitionId(definitionId: number) {
    startTransition(() => {
      router.replace(definitionSearchHref(pathname, searchParams.toString(), String(definitionId)), {
        scroll: false,
      });
    });
  }

  async function handleRefreshCatalog() {
    setIsRefreshingCatalog(true);
    try {
      await refreshDefinitions();
    } finally {
      setIsRefreshingCatalog(false);
    }
  }

  async function handleRefreshDefinition() {
    setIsRefreshingDefinition(true);
    try {
      await Promise.all([refreshDefinitions(), refreshActiveDefinition()]);
    } finally {
      setIsRefreshingDefinition(false);
    }
  }

  function resetCatalogControls() {
    setCatalogQuery("");
    setCatalogFilter("all");
    setCatalogSort("recent");
  }

  const targetDefinitionName =
    selectedDefinitionSummary?.name ?? activeDefinition?.name ?? "None selected";

  return (
    <div className="space-y-8">
      <section className="space-y-6">
        <div>
          <h1 className="text-[2.05rem] font-semibold tracking-tight text-foreground">
            Circuit Schemdraw
          </h1>
          <p className="mt-2 max-w-4xl text-sm leading-6 text-muted-foreground">
            Work against the canonical circuit-definition contract, inspect normalized output, and
            verify whether the current definition detail is ready to support downstream schemdraw
            migration.
          </p>
        </div>

        <div className="grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_minmax(180px,0.4fr)_minmax(180px,0.4fr)_minmax(180px,0.4fr)]">
          <div className="rounded-[1rem] border border-border bg-card px-4 py-4 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
            <div className="flex items-center gap-4">
              <span className="text-base font-semibold text-foreground">Definition</span>
              <div className="min-w-0 flex-1">
                <select
                  value={resolvedDefinitionId ?? ""}
                  onChange={(event) => {
                    replaceDefinitionId(Number(event.target.value));
                  }}
                  disabled={
                    isDefinitionsLoading || !definitions || definitions.length === 0 || isNavigating
                  }
                  className="min-h-11 w-full rounded-md border border-border bg-surface px-4 text-sm text-foreground transition focus:border-primary/40 focus:outline-none"
                >
                  <option value="" disabled>
                    {isDefinitionsLoading ? "Loading definitions..." : "Select a definition"}
                  </option>
                  {(definitions ?? []).map((definition) => (
                    <option key={definition.definition_id} value={definition.definition_id}>
                      {definition.name}
                    </option>
                  ))}
                </select>
              </div>
              {isNavigating ? (
                <LoaderCircle className="h-4 w-4 animate-spin text-muted-foreground" />
              ) : null}
            </div>

            <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
              <SurfaceTag tone="primary">{targetDefinitionName}</SurfaceTag>
              {selectionRecovery ? (
                <SurfaceTag tone={selectionRecovery.tone === "warning" ? "warning" : "default"}>
                  {selectionRecovery.title}
                </SurfaceTag>
              ) : null}
              {attachmentState.isStaleSnapshot ? (
                <SurfaceTag tone="warning">Holding previous snapshot</SurfaceTag>
              ) : null}
            </div>
          </div>

          <SurfaceStat label="Definitions" value={String(catalogSummary.total)} />
          <SurfaceStat label="Ready Candidates" value={String(catalogSummary.readyCount)} tone="primary" />
          <SurfaceStat label="Artifact-backed" value={String(catalogSummary.artifactBackedCount)} />
        </div>
      </section>

      {definitionsError ? (
        <div className="rounded-[1rem] border border-rose-500/30 bg-rose-500/8 px-4 py-3 text-sm text-rose-100">
          Unable to load circuit definitions. {catalogErrorMessage}
        </div>
      ) : null}

      <section className="grid gap-5 xl:grid-cols-[minmax(320px,0.78fr)_minmax(0,1.22fr)]">
        <div className="space-y-4">
          <SurfacePanel
            title="Canonical Definition Catalog"
            description="Filter the summary rows first, then attach the selected canonical detail without leaving the schemdraw workspace."
            actions={
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  aria-label="Refresh definition catalog"
                  onClick={() => {
                    void handleRefreshCatalog();
                  }}
                  disabled={isRefreshingCatalog}
                  className="inline-flex h-9 w-9 cursor-pointer items-center justify-center rounded-full border border-border bg-surface text-foreground transition hover:border-primary/40 hover:bg-primary/10 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <RefreshCcw className={cx("h-4 w-4", isRefreshingCatalog && "animate-spin")} />
                </button>
                <button
                  type="button"
                  aria-label="Select previous definition"
                  disabled={!previousDefinition || isNavigating}
                  onClick={() => {
                    if (previousDefinition) {
                      replaceDefinitionId(previousDefinition.definition_id);
                    }
                  }}
                  className="inline-flex h-9 w-9 cursor-pointer items-center justify-center rounded-full border border-border bg-surface text-foreground transition hover:border-primary/40 hover:bg-primary/10 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <button
                  type="button"
                  aria-label="Select next definition"
                  disabled={!nextDefinition || isNavigating}
                  onClick={() => {
                    if (nextDefinition) {
                      replaceDefinitionId(nextDefinition.definition_id);
                    }
                  }}
                  className="inline-flex h-9 w-9 cursor-pointer items-center justify-center rounded-full border border-border bg-surface text-foreground transition hover:border-primary/40 hover:bg-primary/10 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            }
          >
            <div className="grid gap-3 md:grid-cols-[minmax(0,1fr)_180px_180px]">
              <label className="rounded-[0.9rem] border border-border bg-surface px-4 py-3">
                <span className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  <Search className="h-3.5 w-3.5" />
                  Search
                </span>
                <input
                  value={catalogQuery}
                  onChange={(event) => {
                    setCatalogQuery(event.target.value);
                  }}
                  placeholder="Find by name or id"
                  className="w-full bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground"
                />
              </label>

              <label className="rounded-[0.9rem] border border-border bg-surface px-4 py-3">
                <span className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  <SlidersHorizontal className="h-3.5 w-3.5" />
                  Filter
                </span>
                <select
                  value={catalogFilter}
                  onChange={(event) => {
                    setCatalogFilter(event.target.value as SchemdrawCatalogFilter);
                  }}
                  className="w-full bg-transparent text-sm text-foreground outline-none"
                >
                  <option value="all">All definitions</option>
                  <option value="ready">Ready candidates</option>
                  <option value="warning">Warnings present</option>
                  <option value="artifacts">Artifact-backed</option>
                </select>
              </label>

              <label className="rounded-[0.9rem] border border-border bg-surface px-4 py-3">
                <span className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  <Waypoints className="h-3.5 w-3.5" />
                  Sort
                </span>
                <select
                  value={catalogSort}
                  onChange={(event) => {
                    setCatalogSort(event.target.value as SchemdrawCatalogSortMode);
                  }}
                  className="w-full bg-transparent text-sm text-foreground outline-none"
                >
                  <option value="recent">Newest first</option>
                  <option value="warnings">Warnings first</option>
                  <option value="name">Name A-Z</option>
                </select>
              </label>
            </div>

            <div className="mt-4 flex items-center justify-between gap-3 rounded-[0.9rem] border border-border bg-surface px-4 py-3 text-xs text-muted-foreground">
              <span>
                Showing {filteredDefinitions.length} of {catalogSummary.total} definitions
              </span>
              <button
                type="button"
                onClick={resetCatalogControls}
                disabled={
                  catalogQuery.length === 0 &&
                  catalogFilter === "all" &&
                  catalogSort === "recent"
                }
                className="cursor-pointer rounded-full border border-border px-3 py-1.5 text-foreground transition hover:border-primary/40 hover:bg-primary/10 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Reset filters
              </button>
            </div>

            {selectionRecovery ? (
              <div
                className={cx(
                  "mt-4 rounded-[0.9rem] border px-4 py-3 text-sm",
                  selectionRecovery.tone === "warning"
                    ? "border-amber-500/30 bg-amber-500/8 text-foreground"
                    : "border-border bg-surface text-muted-foreground",
                )}
              >
                <p className="font-medium text-foreground">{selectionRecovery.title}</p>
                <p className="mt-1">{selectionRecovery.message}</p>
              </div>
            ) : null}

            {isDefinitionsLoading && !definitions ? (
              <div className="mt-4 rounded-[0.9rem] border border-border bg-surface px-4 py-5 text-sm text-muted-foreground">
                Loading canonical definitions...
              </div>
            ) : null}

            {!isDefinitionsLoading && (definitions?.length ?? 0) === 0 ? (
              <div className="mt-4 rounded-[0.9rem] border border-dashed border-border bg-surface px-4 py-5 text-sm text-muted-foreground">
                No canonical definitions are available yet.
              </div>
            ) : null}

            {pinnedDefinition ? (
              <div className="mt-4 space-y-2">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Pinned active definition
                </p>
                <CatalogCard
                  createdAt={pinnedDefinition.created_at}
                  definitionId={pinnedDefinition.definition_id}
                  elementCount={pinnedDefinition.element_count}
                  isActive
                  isAttachedSnapshot={activeDefinition?.definition_id === pinnedDefinition.definition_id}
                  isPinned
                  name={pinnedDefinition.name}
                  onSelect={replaceDefinitionId}
                  previewArtifactCount={pinnedDefinition.preview_artifact_count}
                  validationStatus={pinnedDefinition.validation_status}
                />
              </div>
            ) : null}

            {filteredDefinitions.length > 0 ? (
              <div className="mt-4 space-y-3">
                {filteredDefinitions.map((definition) => (
                  <CatalogCard
                    key={definition.definition_id}
                    createdAt={definition.created_at}
                    definitionId={definition.definition_id}
                    elementCount={definition.element_count}
                    isActive={definition.definition_id === resolvedDefinitionId}
                    isAttachedSnapshot={activeDefinition?.definition_id === definition.definition_id}
                    isPinned={false}
                    name={definition.name}
                    onSelect={replaceDefinitionId}
                    previewArtifactCount={definition.preview_artifact_count}
                    validationStatus={definition.validation_status}
                  />
                ))}
              </div>
            ) : null}

            {filteredDefinitions.length === 0 && (definitions?.length ?? 0) > 0 ? (
              <div className="mt-4 rounded-[0.9rem] border border-dashed border-border bg-surface px-4 py-5 text-sm text-muted-foreground">
                No definitions match the current catalog controls. Reset the filters or search for a
                different canonical definition.
              </div>
            ) : null}
          </SurfacePanel>
        </div>

        <div className="space-y-4">
          <SurfacePanel
            title="Selection / Recovery"
            description="The URL remains shareable, but the attached canonical definition detail is the live source for this schemdraw workspace."
            actions={
              <button
                type="button"
                onClick={() => {
                  void handleRefreshDefinition();
                }}
                disabled={isRefreshingDefinition}
                className="inline-flex cursor-pointer items-center gap-2 rounded-full border border-border bg-surface px-3 py-1.5 text-xs font-medium text-foreground transition hover:border-primary/40 hover:bg-primary/10 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <RefreshCcw className={cx("h-3.5 w-3.5", isRefreshingDefinition && "animate-spin")} />
                Refresh snapshot
              </button>
            }
          >
            <div className="grid gap-3 md:grid-cols-4">
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Target Definition
                </p>
                <p className="mt-2 text-lg font-semibold text-foreground">{targetDefinitionName}</p>
              </div>
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  URL Selection
                </p>
                <p className="mt-2 text-lg font-semibold text-foreground">
                  {resolvedDefinitionId ?? "--"}
                </p>
              </div>
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Attached Snapshot
                </p>
                <p className="mt-2 text-lg font-semibold text-foreground">
                  {activeDefinition?.definition_id ?? "--"}
                </p>
              </div>
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Preview Keys
                </p>
                <p className="mt-2 text-lg font-semibold text-foreground">
                  {structuredPreview.topLevelCount}
                </p>
              </div>
            </div>

            {activeDefinitionError ? (
              <div className="mt-4 rounded-[0.9rem] border border-rose-500/30 bg-rose-500/8 px-4 py-3 text-sm text-rose-100">
                Unable to load definition detail. {activeDefinitionErrorMessage}
              </div>
            ) : null}

            {attachmentState.isStaleSnapshot && activeDefinition ? (
              <div className="mt-4 rounded-[0.9rem] border border-amber-500/30 bg-amber-500/8 px-4 py-3 text-sm text-foreground">
                Retaining definition #{activeDefinition.definition_id} while definition #
                {resolvedDefinitionId} attaches. The previous snapshot stays visible so the preview
                surface remains readable during navigation.
              </div>
            ) : null}

            {isDefinitionTransitioning && resolvedDefinitionId !== null ? (
              <div className="mt-4 flex items-center gap-3 rounded-[0.9rem] border border-border bg-surface px-4 py-4 text-sm text-muted-foreground">
                <LoaderCircle className="h-4 w-4 animate-spin" />
                Refreshing canonical definition detail...
              </div>
            ) : null}

            {!activeDefinition && !isDefinitionsLoading ? (
              <div className="mt-4 rounded-[0.9rem] border border-dashed border-border bg-surface px-4 py-5 text-sm text-muted-foreground">
                Select a definition to attach a canonical schemdraw snapshot.
              </div>
            ) : null}
          </SurfacePanel>

          <SurfacePanel
            title="Schematic Readiness"
            description="Readiness is inferred from normalized output, validation notices, and preview artifacts on the selected canonical definition."
            actions={<SurfaceTag tone={readinessTone(readiness.status)}>{readiness.label}</SurfaceTag>}
          >
            <div className="grid gap-3 md:grid-cols-4">
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Notice Count
                </p>
                <p className="mt-2 text-lg font-semibold text-foreground">{readiness.noticeCount}</p>
              </div>
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Warning Count
                </p>
                <p className="mt-2 text-lg font-semibold text-foreground">{readiness.warningCount}</p>
              </div>
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Artifacts
                </p>
                <p className="mt-2 text-lg font-semibold text-foreground">{readiness.artifactCount}</p>
              </div>
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Ports
                </p>
                <p className="mt-2 text-lg font-semibold text-foreground">
                  {readiness.normalizedOutput?.ports ?? "not declared"}
                </p>
              </div>
            </div>

            <div className="mt-4 rounded-[0.9rem] border border-border bg-surface px-4 py-4 text-sm text-muted-foreground">
              {readiness.summary}
            </div>

            <div className="mt-4 grid gap-4 xl:grid-cols-2">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                    Migration Warnings
                  </p>
                  <SurfaceTag tone="warning">{noticeGroups.warnings.length}</SurfaceTag>
                </div>
                {noticeGroups.warnings.length > 0 ? (
                  noticeGroups.warnings.map((notice, index) => (
                    <div
                      key={`${notice.level}-${index}`}
                      className="flex items-start gap-3 rounded-[0.9rem] border border-amber-500/30 bg-amber-500/8 px-4 py-3 text-sm text-foreground"
                    >
                      <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-300" />
                      <span>{notice.message}</span>
                    </div>
                  ))
                ) : (
                  <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4 text-sm text-muted-foreground">
                    No schemdraw-blocking warnings are attached to the current definition.
                  </div>
                )}
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                    Structural Checks
                  </p>
                  <SurfaceTag tone="success">{noticeGroups.checks.length}</SurfaceTag>
                </div>
                {noticeGroups.checks.length > 0 ? (
                  noticeGroups.checks.map((notice, index) => (
                    <div
                      key={`${notice.level}-${index}`}
                      className="flex items-start gap-3 rounded-[0.9rem] border border-border bg-surface px-4 py-3 text-sm text-muted-foreground"
                    >
                      <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                      <span>{notice.message}</span>
                    </div>
                  ))
                ) : (
                  <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4 text-sm text-muted-foreground">
                    No clean validation checks are attached to the current definition.
                  </div>
                )}
              </div>
            </div>
          </SurfacePanel>

          <SurfacePanel
            title="Normalized Output Preview"
            description="Inspect the backend-provided canonical payload in structured form first, then fall back to raw JSON for contract-level debugging."
            actions={
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setPreviewMode("structured");
                  }}
                  className={cx(
                    "cursor-pointer rounded-full border px-3 py-1.5 text-xs font-medium transition",
                    previewMode === "structured"
                      ? "border-primary/30 bg-primary/10 text-foreground"
                      : "border-border bg-surface text-muted-foreground hover:border-primary/30 hover:bg-primary/10 hover:text-foreground",
                  )}
                >
                  Structured
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setPreviewMode("json");
                  }}
                  className={cx(
                    "cursor-pointer rounded-full border px-3 py-1.5 text-xs font-medium transition",
                    previewMode === "json"
                      ? "border-primary/30 bg-primary/10 text-foreground"
                      : "border-border bg-surface text-muted-foreground hover:border-primary/30 hover:bg-primary/10 hover:text-foreground",
                  )}
                >
                  Raw JSON
                </button>
              </div>
            }
          >
            {structuredPreview.parseError ? (
              <div className="rounded-[0.9rem] border border-amber-500/30 bg-amber-500/8 px-4 py-3 text-sm text-foreground">
                {structuredPreview.parseError}
              </div>
            ) : null}

            {previewMode === "structured" ? (
              <div className="space-y-4">
                <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                  {structuredPreview.rows.map((row) => (
                    <div
                      key={row.key}
                      className={cx(
                        "rounded-[0.9rem] border px-4 py-4",
                        row.tone === "success" && "border-emerald-500/25 bg-emerald-500/8",
                        row.tone === "primary" && "border-primary/25 bg-primary/8",
                        row.tone === "default" && "border-border bg-surface",
                      )}
                    >
                      <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                        {row.key}
                      </p>
                      <p className="mt-2 text-sm font-semibold text-foreground">{row.value}</p>
                    </div>
                  ))}
                </div>

                <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-3 text-xs text-muted-foreground">
                  {structuredPreview.topLevelCount} top-level keys ·{" "}
                  {activeDefinition ? `${lineCount(activeDefinition.normalized_output)} lines` : "--"}
                </div>

                <div className="rounded-[0.9rem] border border-border bg-background">
                  <div className="flex items-center justify-between border-b border-border bg-surface px-4 py-3 text-xs uppercase tracking-[0.16em] text-muted-foreground">
                    <span>normalized_output.json</span>
                    <span>canonical snapshot</span>
                  </div>
                  <pre className="max-h-[18rem] overflow-auto px-4 py-4 text-sm leading-6 text-foreground">
                    {structuredPreview.formattedJson}
                  </pre>
                </div>
              </div>
            ) : (
              <div className="rounded-[0.9rem] border border-border bg-background">
                <div className="flex items-center justify-between border-b border-border bg-surface px-4 py-3 text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  <span>normalized_output.json</span>
                  <span>{activeDefinition ? `${lineCount(activeDefinition.normalized_output)} lines` : "--"}</span>
                </div>
                <pre className="max-h-[28rem] overflow-auto px-4 py-4 text-sm leading-6 text-foreground">
                  {activeDefinition?.normalized_output ?? "{\n  \"schemdraw_ready\": false\n}"}
                </pre>
              </div>
            )}
          </SurfacePanel>

          <section className="grid gap-4 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
            <SurfacePanel
              title="Preview Artifacts"
              description="Artifact names come from the selected definition detail and indicate what the current migration surface already exposes."
            >
              {activeDefinition?.preview_artifacts.length ? (
                <div className="space-y-3">
                  {activeDefinition.preview_artifacts.map((artifact, index) => (
                    <div
                      key={artifact}
                      className="flex items-center justify-between rounded-[0.8rem] border border-border bg-surface px-4 py-3"
                    >
                      <div className="flex min-w-0 items-center gap-3">
                        <Package className="h-4 w-4 shrink-0 text-primary" />
                        <div className="min-w-0">
                          <span className="block truncate text-sm text-foreground">{artifact}</span>
                          <span className="text-xs text-muted-foreground">Artifact {index + 1}</span>
                        </div>
                      </div>
                      <SurfaceTag tone={artifactTone(artifact)}>
                        {artifact.split(".").pop() ?? "current"}
                      </SurfaceTag>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  No preview artifacts are attached to the current definition.
                </p>
              )}
            </SurfacePanel>

            <SurfacePanel
              title="Canonical Source Snapshot"
              description="Keep the source definition and normalized output close together so schemdraw review stays grounded in the persisted backend contract."
            >
              <div className="grid gap-3 md:grid-cols-3">
                <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                  <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                    Definition
                  </p>
                  <p className="mt-2 text-lg font-semibold text-foreground">
                    {activeDefinition?.name ?? "None selected"}
                  </p>
                </div>
                <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                  <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                    Created At
                  </p>
                  <p className="mt-2 text-lg font-semibold text-foreground">
                    {activeDefinition?.created_at ?? "--"}
                  </p>
                </div>
                <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                  <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                    Source Lines
                  </p>
                  <p className="mt-2 text-lg font-semibold text-foreground">
                    {activeDefinition ? lineCount(activeDefinition.source_text) : 0}
                  </p>
                </div>
              </div>

              <div className="mt-4 rounded-[0.9rem] border border-border bg-background">
                <div className="flex items-center justify-between border-b border-border bg-surface px-4 py-3 text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <FileCode2 className="h-4 w-4" />
                    <span>source_text.yml</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Waypoints className="h-4 w-4" />
                    <span>canonical input</span>
                  </div>
                </div>
                <pre className="max-h-[22rem] overflow-auto px-4 py-4 text-sm leading-6 text-foreground">
                  {activeDefinition?.source_text ?? "circuit:\n  name: pending_selection\n"}
                </pre>
              </div>
            </SurfacePanel>
          </section>
        </div>
      </section>
    </div>
  );
}
