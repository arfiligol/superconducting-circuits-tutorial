import {
  characterizationFamilies,
  characterizationRuns,
} from "@/features/characterization/lib/mock-data";

const activeRun = characterizationRuns[0];

export function CharacterizationWorkspace() {
  return (
    <div className="space-y-8">
      <section className="space-y-2">
        <h1 className="text-[2.05rem] font-semibold tracking-tight text-foreground">
          Characterization
        </h1>
        <p className="max-w-4xl text-sm leading-6 text-muted-foreground">
          Analysis families, filters, and result history.
        </p>
      </section>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)]">
        <div className="space-y-4">
          <section className="rounded-[1rem] border border-border bg-card px-5 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
            <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              Analysis Selection
            </h2>
            <div className="mt-4 space-y-3">
              {characterizationFamilies.map((family) => (
                <div key={family.name} className="rounded-[0.8rem] border border-border bg-surface px-4 py-3">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="font-medium text-foreground">{family.name}</p>
                      <p className="mt-1 text-sm text-muted-foreground">{family.mode}</p>
                    </div>
                    <span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary">
                      {family.count} configs
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-[1rem] border border-border bg-card px-5 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
            <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              Filters
            </h2>
            <div className="mt-4 grid gap-3 text-sm md:grid-cols-2">
              <div className="rounded-md border border-border bg-surface px-4 py-3">
                <p className="text-xs text-muted-foreground">Source family</p>
                <p className="mt-1 text-foreground">measurement + imported traces</p>
              </div>
              <div className="rounded-md border border-border bg-surface px-4 py-3">
                <p className="text-xs text-muted-foreground">Fit window</p>
                <p className="mt-1 text-foreground">auto / baseline</p>
              </div>
            </div>
          </section>
        </div>

        <div className="space-y-4">
          <section className="rounded-[1rem] border border-border bg-card px-5 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
            <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              Active Result
            </h2>

            <div className="mt-4 grid gap-3 md:grid-cols-3">
              <div className="rounded-md border border-primary/20 bg-primary/10 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">Run State</p>
                <p className="mt-2 font-semibold text-foreground">{activeRun.state}</p>
              </div>
              <div className="rounded-md border border-border bg-surface px-4 py-3">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">Input Dataset</p>
                <p className="mt-2 font-semibold text-foreground">{activeRun.input}</p>
              </div>
              <div className="rounded-md border border-border bg-surface px-4 py-3">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">Updated</p>
                <p className="mt-2 font-semibold text-foreground">{activeRun.updatedAt}</p>
              </div>
            </div>

            <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,0.88fr)]">
              <div className="rounded-[0.8rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">Result Summary</p>
                <div className="mt-3 space-y-3 text-sm">
                  <div className="rounded-md border border-border bg-background px-4 py-3">
                    Dominant mode: coherence-limited decay with stable low-bias region.
                  </div>
                  <div className="rounded-md border border-border bg-background px-4 py-3">
                    Suggested next action: compare against prior baseline and pin review note.
                  </div>
                </div>
              </div>

              <div className="rounded-[0.8rem] border border-border bg-surface px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">Result History</p>
                <ol className="mt-3 space-y-3 text-sm">
                  {characterizationRuns.map((run) => (
                    <li key={run.name} className="rounded-md border border-border bg-background px-4 py-3">
                      <div className="flex items-center justify-between gap-3">
                        <span className="font-medium text-foreground">{run.name}</span>
                        <span
                          className={[
                            "rounded-full px-2.5 py-1 text-xs font-medium",
                            run.state === "ready"
                              ? "bg-emerald-500/10 text-emerald-300"
                              : run.state === "review"
                                ? "bg-amber-500/10 text-amber-300"
                                : "bg-muted text-muted-foreground",
                          ].join(" ")}
                        >
                          {run.state}
                        </span>
                      </div>
                      <p className="mt-2 text-muted-foreground">{run.updatedAt}</p>
                    </li>
                  ))}
                </ol>
              </div>
            </div>
          </section>
        </div>
      </section>
    </div>
  );
}
