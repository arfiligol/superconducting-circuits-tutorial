"use client";

import {
  Search,
} from "lucide-react";

import { useCharacterizationWorkflowData } from "@/features/characterization/hooks/use-characterization-workflow-data";
import {
  characterizationStatusTone,
  resolveCharacterizationSelectionRecovery,
  summarizeCharacterizationResults,
  type CharacterizationResultStatusFilter,
} from "@/features/characterization/lib/workflow";
import {
  SurfaceHeader,
  SurfacePanel,
  SurfaceStat,
  SurfaceTag,
  cx,
} from "@/features/shared/components/surface-kit";
import { ApiError } from "@/lib/api/client";

const statusOptions = [
  { label: "All persisted results", value: "all" },
  { label: "Completed", value: "completed" },
  { label: "Failed", value: "failed" },
  { label: "Blocked", value: "blocked" },
] as const satisfies readonly Readonly<{
  label: string;
  value: CharacterizationResultStatusFilter;
}>[];

function describeApiError(error: Error | undefined) {
  if (!error) {
    return null;
  }

  if (error instanceof ApiError) {
    const debugHint = error.debugRef ? ` Ref: ${error.debugRef}.` : "";
    return `${error.message}${debugHint}`;
  }

  return error.message;
}

function formatCoverageLabel(sourceCoverage: Record<string, number>) {
  const segments = Object.entries(sourceCoverage).map(([source, count]) => `${source} ${count}`);
  return segments.length > 0 ? segments.join(" · ") : "No indexed source coverage";
}

function ResultPayloadPreview({ payload }: Readonly<{ payload: Readonly<Record<string, unknown>> }>) {
  return (
    <pre className="overflow-x-auto rounded-2xl border border-border bg-surface px-4 py-4 text-xs leading-6 text-muted-foreground">
      {JSON.stringify(payload, null, 2)}
    </pre>
  );
}

export function CharacterizationWorkspace() {
  const {
    activeDatasetState,
    designSearch,
    setDesignSearch,
    resultSearch,
    setResultSearch,
    statusFilter,
    setStatusFilter,
    designs,
    designsError,
    isDesignsLoading,
    requestedDesignId,
    selectedDesignId,
    setSelectedDesignId,
    results,
    resultsError,
    isResultsLoading,
    requestedResultId,
    selectedResultId,
    setSelectedResultId,
    resultDetail,
    resultDetailError,
    isResultDetailLoading,
  } = useCharacterizationWorkflowData();

  const selectionRecovery = resolveCharacterizationSelectionRecovery({
    activeDatasetName: activeDatasetState.activeDataset?.name ?? null,
    requestedDesignId,
    resolvedDesignId: selectedDesignId,
    requestedResultId,
    resolvedResultId: selectedResultId,
  });
  const resultSummary = summarizeCharacterizationResults(results);
  const activeDatasetErrorMessage = describeApiError(activeDatasetState.activeDatasetError);
  const designsErrorMessage = describeApiError(designsError);
  const resultsErrorMessage = describeApiError(resultsError);
  const resultDetailErrorMessage = describeApiError(resultDetailError);

  return (
    <div className="space-y-8">
      <SurfaceHeader
        eyebrow="Persisted Results"
        title="Characterization"
        description="Browse dataset-scoped characterization summaries, then open one persisted result detail without reusing task queue or execution controls."
        actions={
          <>
            <SurfaceTag
              tone={
                activeDatasetState.activeDataset ? "success" : activeDatasetState.status === "error"
                  ? "warning"
                  : "default"
              }
            >
              {activeDatasetState.activeDataset?.name ?? "Dataset not attached"}
            </SurfaceTag>
            {selectedDesignId ? <SurfaceTag tone="primary">{selectedDesignId}</SurfaceTag> : null}
          </>
        }
      />

      {selectionRecovery ? (
        <div
          className={cx(
            "rounded-[1rem] border px-4 py-4",
            selectionRecovery.tone === "warning"
              ? "border-amber-500/25 bg-amber-500/10"
              : "border-border bg-surface",
          )}
        >
          <p className="text-sm font-semibold text-foreground">{selectionRecovery.title}</p>
          <p className="mt-1 text-sm text-muted-foreground">{selectionRecovery.message}</p>
        </div>
      ) : null}

      <div className="grid gap-4 md:grid-cols-4">
        <SurfaceStat
          label="Visible Designs"
          value={String(designs.length)}
          tone="primary"
        />
        <SurfaceStat label="Visible Results" value={String(resultSummary.total)} />
        <SurfaceStat label="Completed" value={String(resultSummary.completedCount)} />
        <SurfaceStat label="Artifact Refs" value={String(resultSummary.artifactCount)} />
      </div>

      {!activeDatasetState.activeDataset ? (
        <SurfacePanel
          title="Attach Active Dataset"
          description="Characterization results are always scoped to the shared shell active dataset. Attach one from the header before browsing persisted summaries."
        >
          <p className="text-sm leading-6 text-muted-foreground">
            {activeDatasetErrorMessage ??
              "This page keeps only page-local design/result browse state. Dataset authority continues to come from the shared shell context."}
          </p>
        </SurfacePanel>
      ) : (
        <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr_1.2fr]">
          <SurfacePanel
            title="Design Scope"
            description="Pick one dataset-local design scope, then browse persisted characterization results within that scope."
          >
            <label className="relative block">
              <Search className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <input
                value={designSearch}
                onChange={(event) => {
                  setDesignSearch(event.target.value);
                }}
                placeholder="Search designs"
                className="w-full rounded-xl border border-border bg-surface py-2 pl-9 pr-3 text-sm outline-none transition focus:border-primary/40"
              />
            </label>

            <div className="mt-4 space-y-3">
              {designs.map((design) => (
                <button
                  key={design.design_id}
                  type="button"
                  onClick={() => {
                    setSelectedDesignId(design.design_id);
                  }}
                  className={cx(
                    "w-full rounded-[1rem] border px-4 py-4 text-left transition",
                    selectedDesignId === design.design_id
                      ? "border-primary/35 bg-primary/10"
                      : "border-border bg-surface hover:border-primary/25 hover:bg-primary/5",
                  )}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <h3 className="truncate text-sm font-semibold text-foreground">
                        {design.name}
                      </h3>
                      <p className="mt-1 text-xs uppercase tracking-[0.14em] text-muted-foreground">
                        {design.design_id}
                      </p>
                    </div>
                    <SurfaceTag tone="default">{design.compare_readiness}</SurfaceTag>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2 text-[11px] text-muted-foreground">
                    <span>{design.trace_count} traces</span>
                    <span>{formatCoverageLabel(design.source_coverage)}</span>
                  </div>
                </button>
              ))}

              {!isDesignsLoading && designs.length === 0 ? (
                <p className="rounded-[1rem] border border-dashed border-border px-4 py-6 text-sm text-muted-foreground">
                  No visible design scope matches this dataset search.
                </p>
              ) : null}
              {designsErrorMessage ? (
                <p className="text-sm text-amber-700">{designsErrorMessage}</p>
              ) : null}
            </div>
          </SurfacePanel>

          <SurfacePanel
            title="Result Summary List"
            description="Summary-first browse surface for persisted characterization results. Select one row to expand diagnostics, payload, and artifact references."
          >
            <div className="grid gap-3 md:grid-cols-[1fr_auto]">
              <label className="relative block">
                <Search className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <input
                  value={resultSearch}
                  onChange={(event) => {
                    setResultSearch(event.target.value);
                  }}
                  placeholder="Search results or analysis id"
                  className="w-full rounded-xl border border-border bg-surface py-2 pl-9 pr-3 text-sm outline-none transition focus:border-primary/40"
                />
              </label>
              <select
                value={statusFilter}
                onChange={(event) => {
                  setStatusFilter(event.target.value as CharacterizationResultStatusFilter);
                }}
                className="rounded-xl border border-border bg-surface px-3 py-2 text-sm outline-none transition focus:border-primary/40"
              >
                {statusOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="mt-4 space-y-3">
              {results.map((result) => (
                <button
                  key={result.resultId}
                  type="button"
                  onClick={() => {
                    setSelectedResultId(result.resultId);
                  }}
                  className={cx(
                    "w-full rounded-[1rem] border px-4 py-4 text-left transition",
                    selectedResultId === result.resultId
                      ? "border-primary/35 bg-card"
                      : "border-border bg-surface hover:border-primary/25 hover:bg-primary/5",
                  )}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <h3 className="truncate text-sm font-semibold text-foreground">
                        {result.title}
                      </h3>
                      <p className="mt-1 text-xs uppercase tracking-[0.14em] text-muted-foreground">
                        {result.analysisId}
                      </p>
                    </div>
                    <SurfaceTag tone={characterizationStatusTone(result.status)}>
                      {result.status}
                    </SurfaceTag>
                  </div>

                  <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
                    <SurfaceTag tone="default">{result.traceCount} traces</SurfaceTag>
                    <SurfaceTag tone="default">{result.artifactCount} artifacts</SurfaceTag>
                    <SurfaceTag tone="default">{result.updatedAt}</SurfaceTag>
                  </div>

                  <p className="mt-3 text-sm text-muted-foreground">{result.freshnessSummary}</p>
                  <p className="mt-1 text-xs text-muted-foreground">{result.provenanceSummary}</p>
                </button>
              ))}

              {!isResultsLoading && results.length === 0 ? (
                <p className="rounded-[1rem] border border-dashed border-border px-4 py-6 text-sm text-muted-foreground">
                  No persisted characterization result matches this design scope and filter set.
                </p>
              ) : null}
              {resultsErrorMessage ? (
                <p className="text-sm text-amber-700">{resultsErrorMessage}</p>
              ) : null}
            </div>
          </SurfacePanel>

          <SurfacePanel
            title="Persisted Result Detail"
            description="Detail path only. Payload, diagnostics, and artifact references expand here after one persisted result summary row is selected."
          >
            {!selectedResultId ? (
              <p className="rounded-[1rem] border border-dashed border-border px-4 py-6 text-sm text-muted-foreground">
                Select one persisted characterization result to inspect detail payload and artifact references.
              </p>
            ) : null}

            {resultDetail ? (
              <div className="space-y-5">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h3 className="text-base font-semibold text-foreground">
                      {resultDetail.title}
                    </h3>
                    <p className="mt-1 text-sm text-muted-foreground">
                      {resultDetail.analysisId} · {resultDetail.updatedAt}
                    </p>
                  </div>
                  <SurfaceTag tone={characterizationStatusTone(resultDetail.status)}>
                    {resultDetail.status}
                  </SurfaceTag>
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <div className="rounded-2xl border border-border bg-surface px-4 py-4">
                    <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                      Freshness
                    </p>
                    <p className="mt-2 text-sm text-foreground">{resultDetail.freshnessSummary}</p>
                  </div>
                  <div className="rounded-2xl border border-border bg-surface px-4 py-4">
                    <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                      Provenance
                    </p>
                    <p className="mt-2 text-sm text-foreground">
                      {resultDetail.provenanceSummary}
                    </p>
                  </div>
                </div>

                <div className="rounded-2xl border border-border bg-surface px-4 py-4">
                  <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                    Input Trace Scope
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {resultDetail.inputTraceIds.map((traceId) => (
                      <SurfaceTag key={traceId} tone="default">
                        {traceId}
                      </SurfaceTag>
                    ))}
                  </div>
                </div>

                <div className="rounded-2xl border border-border bg-surface px-4 py-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                      Diagnostics
                    </p>
                    <SurfaceTag
                      tone={
                        resultDetail.diagnostics.some((diagnostic) => diagnostic.blocking)
                          ? "warning"
                          : "default"
                      }
                    >
                      {resultDetail.diagnostics.length} entries
                    </SurfaceTag>
                  </div>

                  <div className="mt-3 space-y-3">
                    {resultDetail.diagnostics.map((diagnostic) => (
                      <div
                        key={`${diagnostic.code}-${diagnostic.message}`}
                        className={cx(
                          "rounded-xl border px-3 py-3",
                          diagnostic.blocking
                            ? "border-amber-500/25 bg-amber-500/10"
                            : "border-border bg-card",
                        )}
                      >
                        <div className="flex flex-wrap items-center gap-2">
                          <SurfaceTag tone={diagnostic.blocking ? "warning" : "default"}>
                            {diagnostic.severity}
                          </SurfaceTag>
                          <span className="text-xs uppercase tracking-[0.14em] text-muted-foreground">
                            {diagnostic.code}
                          </span>
                        </div>
                        <p className="mt-2 text-sm text-foreground">{diagnostic.message}</p>
                      </div>
                    ))}
                    {resultDetail.diagnostics.length === 0 ? (
                      <p className="text-sm text-muted-foreground">
                        No diagnostics were attached to this persisted result detail.
                      </p>
                    ) : null}
                  </div>
                </div>

                <div className="rounded-2xl border border-border bg-surface px-4 py-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                      Artifact References
                    </p>
                    <SurfaceTag tone="default">
                      {resultDetail.artifactRefs.length} refs
                    </SurfaceTag>
                  </div>
                  <div className="mt-3 space-y-3">
                    {resultDetail.artifactRefs.map((artifact) => (
                      <div
                        key={artifact.artifactId}
                        className="rounded-xl border border-border bg-card px-3 py-3"
                      >
                        <div className="flex flex-wrap items-center gap-2">
                          <SurfaceTag tone="default">{artifact.category}</SurfaceTag>
                          <SurfaceTag tone="default">{artifact.viewKind}</SurfaceTag>
                          <SurfaceTag tone="default">{artifact.payloadFormat}</SurfaceTag>
                        </div>
                        <p className="mt-2 text-sm font-medium text-foreground">
                          {artifact.title}
                        </p>
                        <p className="mt-1 text-xs text-muted-foreground">
                          {artifact.payloadLocator ?? "No materialized locator available"}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="mb-3 text-xs uppercase tracking-[0.16em] text-muted-foreground">
                    Payload Preview
                  </p>
                  <ResultPayloadPreview payload={resultDetail.payload} />
                </div>
              </div>
            ) : null}

            {isResultDetailLoading ? (
              <p className="mt-4 text-sm text-muted-foreground">
                Loading persisted result detail…
              </p>
            ) : null}
            {resultDetailErrorMessage ? (
              <p className="mt-4 text-sm text-amber-700">{resultDetailErrorMessage}</p>
            ) : null}
          </SurfacePanel>
        </div>
      )}
    </div>
  );
}
