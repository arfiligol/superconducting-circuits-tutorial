export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <section className="rounded-[1rem] border border-border bg-card px-5 py-5 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
          Workspace Overview
        </p>
        <h1 className="mt-3 text-[2rem] font-semibold tracking-tight text-foreground">
          Dashboard
        </h1>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-muted-foreground">
          Use the shared header to inspect the active workspace, active dataset, queue activity,
          worker summary slot, and user controls before entering a workflow surface.
        </p>
      </section>

      <section className="grid gap-4 xl:grid-cols-3">
        <div className="rounded-[1rem] border border-border bg-card px-5 py-5">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
            Stable Navigation
          </p>
          <p className="mt-3 text-sm leading-6 text-muted-foreground">
            Sidebar navigation stays focused on durable route families instead of local workflow
            controls.
          </p>
        </div>
        <div className="rounded-[1rem] border border-border bg-card px-5 py-5">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
            Global Context
          </p>
          <p className="mt-3 text-sm leading-6 text-muted-foreground">
            Header triggers carry session-backed workspace, dataset, queue, worker, and user
            context across every page family.
          </p>
        </div>
        <div className="rounded-[1rem] border border-border bg-card px-5 py-5">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
            Workflow Entry
          </p>
          <p className="mt-3 text-sm leading-6 text-muted-foreground">
            Enter Data Browser, Schemas, Schemdraw, Simulation, or Characterization from the same
            shell contract instead of page-local navigation.
          </p>
        </div>
      </section>
    </div>
  );
}
