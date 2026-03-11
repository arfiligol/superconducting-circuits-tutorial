import {
  analysisCategories,
  comparisonRows,
  fitQueue,
} from "@/features/analysis/lib/mock-data";

export function AnalysisWorkspace() {
  return (
    <div className="space-y-8">
      <section className="space-y-2">
        <h1 className="text-[2.05rem] font-semibold tracking-tight text-foreground">Analysis</h1>
        <p className="max-w-4xl text-sm leading-6 text-muted-foreground">
          Fitting, comparison, and reporting surfaces.
        </p>
      </section>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)]">
        <div className="space-y-4">
          <section className="rounded-[1rem] border border-border bg-card px-5 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
            <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              Result Categories
            </h2>
            <div className="mt-4 space-y-3">
              {analysisCategories.map((category) => (
                <div key={category.title} className="rounded-[0.8rem] border border-border bg-surface px-4 py-3">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="font-medium text-foreground">{category.title}</p>
                      <p className="mt-1 text-sm text-muted-foreground">{category.focus}</p>
                    </div>
                    <span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary">
                      {category.count}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <div className="rounded-md border border-primary/20 bg-primary/10 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">Selected Dataset</p>
                <p className="mt-2 font-semibold text-foreground">fluxonium-2025-031</p>
              </div>
              <div className="rounded-md border border-border bg-surface px-4 py-3">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">Pinned Baseline</p>
                <p className="mt-2 font-semibold text-foreground">baseline_a</p>
              </div>
            </div>
          </section>
        </div>

        <div className="space-y-4">
          <section className="rounded-[1rem] border border-border bg-card px-5 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
            <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              Fit Queue
            </h2>
            <div className="mt-4 space-y-3 text-sm">
              {fitQueue.map((item) => (
                <div
                  key={item.name}
                  className="flex items-center justify-between gap-3 rounded-[0.8rem] border border-border bg-surface px-4 py-3"
                >
                  <div>
                    <p className="font-medium text-foreground">{item.name}</p>
                    <p className="mt-1 text-muted-foreground">{item.model}</p>
                  </div>
                  <span
                    className={[
                      "rounded-full px-2.5 py-1 text-xs font-medium",
                      item.status === "ready"
                        ? "bg-emerald-500/10 text-emerald-300"
                        : item.status === "review"
                          ? "bg-amber-500/10 text-amber-300"
                          : "bg-muted text-muted-foreground",
                    ].join(" ")}
                  >
                    {item.status}
                  </span>
                </div>
              ))}
            </div>
          </section>

          <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
            <section className="rounded-[1rem] border border-border bg-card px-5 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
              <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                Comparison Matrix
              </h2>
              <div className="mt-4 overflow-hidden rounded-[0.8rem] border border-border">
                <table className="min-w-full border-collapse text-left text-sm">
                  <thead className="bg-surface text-xs uppercase tracking-[0.18em] text-muted-foreground">
                    <tr>
                      <th className="px-4 py-3">Reference</th>
                      <th className="px-4 py-3">Freq Ratio</th>
                      <th className="px-4 py-3">Decay Ratio</th>
                      <th className="px-4 py-3">State</th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparisonRows.map((row) => (
                      <tr key={row[0]} className="bg-card">
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
            </section>

            <section className="rounded-[1rem] border border-border bg-card px-5 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
              <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                Reporting Notes
              </h2>
              <div className="mt-4 space-y-3 text-sm">
                <div className="rounded-[0.8rem] border border-border bg-surface px-4 py-3">
                  Summary bundle generation should consume typed fit outputs rather than page state.
                </div>
                <div className="rounded-[0.8rem] border border-border bg-surface px-4 py-3">
                  Comparison narratives can later be assembled from backend-provided report fragments.
                </div>
                <div className="rounded-[0.8rem] border border-border bg-surface px-4 py-3">
                  Export actions are intentionally deferred until integration decides output formats.
                </div>
              </div>
            </section>
          </div>
        </div>
      </section>
    </div>
  );
}
