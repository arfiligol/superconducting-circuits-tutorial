import {
  SurfaceHeader,
  SurfacePanel,
  SurfaceStat,
  SurfaceTag,
} from "@/features/shared/components/surface-kit";
import {
  analysisCategories,
  comparisonRows,
  fitQueue,
} from "@/features/analysis/lib/mock-data";

export function AnalysisWorkspace() {
  return (
    <div className="space-y-4">
      <SurfaceHeader
        eyebrow="Analysis"
        title="Fitting, comparison, and reporting surfaces"
        description="Dense analysis workspace skeleton for consolidating result categories, fit queues, and comparison tables without embedding business workflows in the page layer."
        actions={
          <>
            <SurfaceTag tone="primary">Post-processing shell</SurfaceTag>
            <SurfaceTag>Typed mock context</SurfaceTag>
          </>
        }
      />

      <section className="grid gap-4 xl:grid-cols-[minmax(0,0.78fr)_minmax(0,1.22fr)]">
        <div className="grid gap-4">
          <SurfacePanel
            title="Result Categories"
            description="Category selectors and context cards for downstream fitting and reporting tools."
          >
            <div className="space-y-3">
              {analysisCategories.map((category) => (
                <div
                  key={category.title}
                  className="rounded-2xl border border-border bg-muted/25 px-4 py-3"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="font-medium">{category.title}</p>
                      <p className="mt-1 text-sm text-muted-foreground">{category.focus}</p>
                    </div>
                    <SurfaceTag tone="primary">{category.count}</SurfaceTag>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <SurfaceStat label="Selected Dataset" value="fluxonium-2025-031" tone="primary" />
              <SurfaceStat label="Pinned Baseline" value="baseline_a" />
            </div>
          </SurfacePanel>
        </div>

        <div className="grid gap-4">
          <SurfacePanel
            title="Fit Queue"
            description="Migration-ready queue region for model fitting jobs and review status."
          >
            <div className="space-y-3 text-sm">
              {fitQueue.map((item) => (
                <div
                  key={item.name}
                  className="flex items-center justify-between gap-3 rounded-2xl border border-border bg-muted/25 px-4 py-3"
                >
                  <div>
                    <p className="font-medium">{item.name}</p>
                    <p className="mt-1 text-muted-foreground">{item.model}</p>
                  </div>
                  <SurfaceTag
                    tone={
                      item.status === "ready"
                        ? "success"
                        : item.status === "review"
                          ? "warning"
                          : "default"
                    }
                  >
                    {item.status}
                  </SurfaceTag>
                </div>
              ))}
            </div>
          </SurfacePanel>

          <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
            <SurfacePanel
              title="Comparison Matrix"
              description="Structured placeholder for comparing fitted outputs against baselines."
            >
              <div className="overflow-hidden rounded-2xl border border-border">
                <table className="min-w-full border-collapse text-left text-sm">
                  <thead className="bg-muted/45 text-xs uppercase tracking-[0.18em] text-muted-foreground">
                    <tr>
                      <th className="px-4 py-3">Reference</th>
                      <th className="px-4 py-3">Freq Ratio</th>
                      <th className="px-4 py-3">Decay Ratio</th>
                      <th className="px-4 py-3">State</th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparisonRows.map((row) => (
                      <tr key={row[0]}>
                        {row.map((value) => (
                          <td key={value} className="border-t border-border px-4 py-3">
                            {value}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </SurfacePanel>

            <SurfacePanel
              title="Reporting Notes"
              description="Reserved space for generated summaries and review callouts."
            >
              <div className="space-y-3 text-sm">
                <div className="rounded-2xl border border-border bg-muted/25 px-4 py-3">
                  Summary bundle generation should consume typed fit outputs rather than page state.
                </div>
                <div className="rounded-2xl border border-border bg-muted/25 px-4 py-3">
                  Comparison narratives can later be assembled from backend-provided report fragments.
                </div>
                <div className="rounded-2xl border border-border bg-muted/25 px-4 py-3">
                  Export actions are intentionally deferred until integration decides output formats.
                </div>
              </div>
            </SurfacePanel>
          </div>
        </div>
      </section>
    </div>
  );
}
