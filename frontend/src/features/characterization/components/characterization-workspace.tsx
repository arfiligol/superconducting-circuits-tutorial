import {
  SurfaceHeader,
  SurfacePanel,
  SurfaceStat,
  SurfaceTag,
} from "@/features/shared/components/surface-kit";
import {
  characterizationFamilies,
  characterizationRuns,
} from "@/features/characterization/lib/mock-data";

const activeRun = characterizationRuns[0];

export function CharacterizationWorkspace() {
  return (
    <div className="space-y-4">
      <SurfaceHeader
        eyebrow="Characterization"
        title="Analysis families, filters, and result history"
        description="Practical workspace skeleton for selecting characterization flows, staging inputs, and reviewing result history before real analysis services are connected."
        actions={
          <>
            <SurfaceTag tone="primary">History-aware layout</SurfaceTag>
            <SurfaceTag>Simulation excluded</SurfaceTag>
          </>
        }
      />

      <section className="grid gap-4 xl:grid-cols-[minmax(0,0.78fr)_minmax(0,1.22fr)]">
        <div className="grid gap-4">
          <SurfacePanel
            title="Analysis Selection"
            description="Family selection and filter controls for the characterization queue."
          >
            <div className="space-y-3">
              {characterizationFamilies.map((family) => (
                <div
                  key={family.name}
                  className="rounded-2xl border border-border bg-muted/25 px-4 py-3"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="font-medium">{family.name}</p>
                      <p className="mt-1 text-sm text-muted-foreground">{family.mode}</p>
                    </div>
                    <SurfaceTag tone="primary">{family.count} configs</SurfaceTag>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 rounded-2xl border border-border bg-muted/20 p-4">
              <div className="grid gap-3 text-sm md:grid-cols-2">
                <div>
                  <label className="text-xs uppercase tracking-[0.16em] text-muted-foreground" htmlFor="char-source">
                    Source family
                  </label>
                  <input
                    id="char-source"
                    className="mt-2 w-full rounded-xl border border-border bg-card px-3 py-2"
                    defaultValue="measurement + imported traces"
                    readOnly
                  />
                </div>
                <div>
                  <label className="text-xs uppercase tracking-[0.16em] text-muted-foreground" htmlFor="char-window">
                    Fit window
                  </label>
                  <input
                    id="char-window"
                    className="mt-2 w-full rounded-xl border border-border bg-card px-3 py-2"
                    defaultValue="auto / baseline"
                    readOnly
                  />
                </div>
              </div>
            </div>
          </SurfacePanel>
        </div>

        <div className="grid gap-4">
          <SurfacePanel
            title="Active Result"
            description="Focused detail view for the selected characterization run."
          >
            <div className="grid gap-3 md:grid-cols-3">
              <SurfaceStat label="Run State" value={activeRun.state} tone="primary" />
              <SurfaceStat label="Input Dataset" value={activeRun.input} />
              <SurfaceStat label="Updated" value={activeRun.updatedAt} />
            </div>

            <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,0.88fr)]">
              <div className="rounded-2xl border border-border bg-muted/20 p-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Result Summary
                </p>
                <div className="mt-3 space-y-3 text-sm">
                  <div className="rounded-xl border border-border bg-card px-4 py-3">
                    Dominant mode: coherence-limited decay with stable low-bias region.
                  </div>
                  <div className="rounded-xl border border-border bg-card px-4 py-3">
                    Suggested next action: compare against prior baseline and pin review note.
                  </div>
                </div>
              </div>

              <div className="rounded-2xl border border-border bg-muted/20 p-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  Result History
                </p>
                <ol className="mt-3 space-y-3 text-sm">
                  {characterizationRuns.map((run) => (
                    <li
                      key={run.name}
                      className="rounded-xl border border-border bg-card px-4 py-3"
                    >
                      <div className="flex items-center justify-between gap-3">
                        <span className="font-medium">{run.name}</span>
                        <SurfaceTag
                          tone={
                            run.state === "ready"
                              ? "success"
                              : run.state === "review"
                                ? "warning"
                                : "default"
                          }
                        >
                          {run.state}
                        </SurfaceTag>
                      </div>
                      <p className="mt-2 text-muted-foreground">{run.updatedAt}</p>
                    </li>
                  ))}
                </ol>
              </div>
            </div>
          </SurfacePanel>
        </div>
      </section>
    </div>
  );
}
