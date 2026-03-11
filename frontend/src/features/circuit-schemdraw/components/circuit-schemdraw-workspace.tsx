"use client";

import { useEffect, useTransition } from "react";
import {
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  FileCode2,
  LoaderCircle,
  Package,
  Waypoints,
} from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

import { useCircuitSchemdrawData } from "@/features/circuit-schemdraw/hooks/use-circuit-schemdraw-data";
import {
  parseSchemdrawDefinitionIdParam,
} from "@/features/circuit-schemdraw/lib/definition-id";
import { inferSchemdrawReadiness } from "@/features/circuit-schemdraw/lib/readiness";
import {
  SurfacePanel,
  SurfaceStat,
  SurfaceTag,
  cx,
} from "@/features/shared/components/surface-kit";

function definitionSearchHref(pathname: string, searchParamsValue: string, definitionId: string) {
  const params = new URLSearchParams(searchParamsValue);
  params.set("definitionId", definitionId);
  return `${pathname}?${params.toString()}`;
}

function lineCount(value: string) {
  return value.split("\n").length;
}

function countWarnings(validationNotices: readonly { level: "ok" | "warning" }[]) {
  return validationNotices.filter((notice) => notice.level === "warning").length;
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

export function CircuitSchemdrawWorkspace() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [isNavigating, startTransition] = useTransition();

  const rawDefinitionId = parseSchemdrawDefinitionIdParam(searchParams.get("definitionId"));
  const {
    definitions,
    definitionsError,
    isDefinitionsLoading,
    resolvedDefinitionId,
    activeDefinition,
    activeDefinitionError,
    isActiveDefinitionLoading,
  } = useCircuitSchemdrawData(rawDefinitionId);
  const readiness = inferSchemdrawReadiness(activeDefinition);
  const warningCount = activeDefinition ? countWarnings(activeDefinition.validation_notices) : 0;
  const activeDefinitionIndex =
    typeof resolvedDefinitionId === "number"
      ? (definitions ?? []).findIndex((definition) => definition.definition_id === resolvedDefinitionId)
      : -1;
  const previousDefinition = activeDefinitionIndex > 0 ? definitions?.[activeDefinitionIndex - 1] : undefined;
  const nextDefinition =
    activeDefinitionIndex >= 0 && definitions && activeDefinitionIndex < definitions.length - 1
      ? definitions[activeDefinitionIndex + 1]
      : undefined;

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

  return (
    <div className="space-y-8">
      <section className="space-y-6">
        <div>
          <h1 className="text-[2.05rem] font-semibold tracking-tight text-foreground">
            Circuit Schemdraw
          </h1>
          <p className="mt-2 max-w-4xl text-sm leading-6 text-muted-foreground">
            Inspect the canonical circuit definition that will feed schemdraw migration work. This
            workspace stays read-first and uses the current rewrite definition contract as the
            source of truth.
          </p>
        </div>

        <div className="grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_minmax(180px,0.4fr)_minmax(180px,0.4fr)_minmax(180px,0.4fr)]">
          <div className="flex items-center gap-4 rounded-[1rem] border border-border bg-card px-4 py-4 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
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
                className="min-h-11 w-full rounded-md border border-border bg-surface px-4 text-sm text-foreground"
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

          <SurfaceStat label="Definitions" value={String(definitions?.length ?? 0)} />
          <SurfaceStat label="Warnings" value={String(warningCount)} tone="primary" />
          <SurfaceStat label="Artifacts" value={String(readiness.artifactCount)} />
        </div>
      </section>

      {definitionsError ? (
        <div className="rounded-[1rem] border border-rose-500/30 bg-rose-500/8 px-4 py-3 text-sm text-rose-100">
          Unable to load circuit definitions. {definitionsError.message}
        </div>
      ) : null}

      <section className="grid gap-5 xl:grid-cols-[minmax(320px,0.74fr)_minmax(0,1.26fr)]">
        <div className="space-y-4">
          <SurfacePanel
            title="Canonical Definition Catalog"
            description="Load summary rows first, then inspect the selected definition detail that will drive schemdraw migration."
            actions={
              <div className="flex items-center gap-2">
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
            {isDefinitionsLoading && !definitions ? (
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-5 text-sm text-muted-foreground">
                Loading canonical definitions...
              </div>
            ) : null}

            {!isDefinitionsLoading && (definitions?.length ?? 0) === 0 ? (
              <div className="rounded-[0.9rem] border border-dashed border-border bg-surface px-4 py-5 text-sm text-muted-foreground">
                No canonical definitions are available yet.
              </div>
            ) : null}

            <div className="space-y-3">
              {(definitions ?? []).map((definition) => {
                const isActive = definition.definition_id === resolvedDefinitionId;

                return (
                  <button
                    key={definition.definition_id}
                    type="button"
                    onClick={() => {
                      replaceDefinitionId(definition.definition_id);
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
                        <h2 className="truncate text-base font-semibold text-foreground">
                          {definition.name}
                        </h2>
                        <p className="mt-1 text-xs uppercase tracking-[0.14em] text-muted-foreground">
                          Definition #{definition.definition_id}
                        </p>
                      </div>
                      <SurfaceTag tone={isActive ? "primary" : "default"}>
                        {definition.element_count} elements
                      </SurfaceTag>
                    </div>
                    <div className="mt-4 grid gap-2 text-xs text-muted-foreground sm:grid-cols-2">
                      <span>Created: {definition.created_at}</span>
                      <span className="sm:text-right">
                        Detail fetch on selection
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </SurfacePanel>

          <SurfacePanel
            title="Schematic Readiness"
            description="Readiness is inferred from normalized output plus validation notices on the selected canonical definition."
            actions={<SurfaceTag tone={readinessTone(readiness.status)}>{readiness.label}</SurfaceTag>}
          >
            {activeDefinitionError ? (
              <div className="rounded-[0.9rem] border border-rose-500/30 bg-rose-500/8 px-4 py-3 text-sm text-rose-100">
                Unable to load definition detail. {activeDefinitionError.message}
              </div>
            ) : null}

            {isActiveDefinitionLoading && resolvedDefinitionId !== null ? (
              <div className="flex items-center gap-3 rounded-[0.9rem] border border-border bg-surface px-4 py-4 text-sm text-muted-foreground">
                <LoaderCircle className="h-4 w-4 animate-spin" />
                Loading definition detail...
              </div>
            ) : null}

            {!activeDefinition && !isDefinitionsLoading ? (
              <div className="rounded-[0.9rem] border border-dashed border-border bg-surface px-4 py-5 text-sm text-muted-foreground">
                Select a definition to inspect schemdraw readiness.
              </div>
            ) : null}

            <div className="grid gap-3 md:grid-cols-3">
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
                  Normalized Ports
                </p>
                <p className="mt-2 text-lg font-semibold text-foreground">
                  {readiness.normalizedOutput?.ports ?? "not declared"}
                </p>
              </div>
            </div>

            <div className="mt-4 rounded-[0.9rem] border border-border bg-surface px-4 py-4 text-sm text-muted-foreground">
              {readiness.summary}
            </div>

            {activeDefinition?.validation_notices.length ? (
              <div className="mt-4 space-y-3">
                {activeDefinition.validation_notices.map((notice, index) => (
                  <div
                    key={`${notice.level}-${index}`}
                    className={cx(
                      "flex items-start gap-3 rounded-[0.9rem] border px-4 py-3 text-sm",
                      notice.level === "warning"
                        ? "border-amber-500/30 bg-amber-500/8 text-foreground"
                        : "border-border bg-surface text-muted-foreground",
                    )}
                  >
                    <AlertTriangle
                      className={cx(
                        "mt-0.5 h-4 w-4 shrink-0",
                        notice.level === "warning" ? "text-amber-300" : "text-primary",
                      )}
                    />
                    <span>{notice.message}</span>
                  </div>
                ))}
              </div>
            ) : null}
          </SurfacePanel>
        </div>

        <div className="space-y-4">
          <SurfacePanel
            title="Normalized Output Preview"
            description="This is the current backend-provided canonical payload. No speculative schemdraw rendering contract is introduced here."
          >
            <div className="rounded-[0.9rem] border border-border bg-background">
              <div className="flex items-center justify-between border-b border-border bg-surface px-4 py-3 text-xs uppercase tracking-[0.16em] text-muted-foreground">
                <span>normalized_output.json</span>
                <span>{activeDefinition ? `${lineCount(activeDefinition.normalized_output)} lines` : "--"}</span>
              </div>
              <pre className="max-h-[28rem] overflow-auto px-4 py-4 text-sm leading-6 text-foreground">
                {activeDefinition?.normalized_output ?? "{\n  \"schemdraw_ready\": false\n}"}
              </pre>
            </div>
          </SurfacePanel>

          <SurfacePanel
            title="Preview Artifacts"
            description="Artifact names come directly from the selected definition detail and indicate what the current migration surface already exposes."
          >
            {activeDefinition?.preview_artifacts.length ? (
              <div className="space-y-3">
                {activeDefinition.preview_artifacts.map((artifact) => (
                  <div
                    key={artifact}
                    className="flex items-center justify-between rounded-[0.8rem] border border-border bg-surface px-4 py-3"
                  >
                    <div className="flex min-w-0 items-center gap-3">
                      <Package className="h-4 w-4 shrink-0 text-primary" />
                      <span className="truncate text-sm text-foreground">{artifact}</span>
                    </div>
                    <SurfaceTag tone="primary">current</SurfaceTag>
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
            description="The source definition remains the single migration input for schemdraw. Use it to compare normalized output and artifact readiness."
          >
            <div className="grid gap-3 md:grid-cols-3">
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">Definition</p>
                <p className="mt-2 text-lg font-semibold text-foreground">
                  {activeDefinition?.name ?? "None selected"}
                </p>
              </div>
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">Created At</p>
                <p className="mt-2 text-lg font-semibold text-foreground">
                  {activeDefinition?.created_at ?? "--"}
                </p>
              </div>
              <div className="rounded-[0.9rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">Source Lines</p>
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
        </div>
      </section>
    </div>
  );
}
