import {
  Activity,
  ChevronDown,
  CircuitBoard,
  FlaskConical,
  FolderKanban,
  Play,
  ScrollText,
  WandSparkles,
} from "lucide-react";

type SectionCardProps = Readonly<{
  children: React.ReactNode;
  icon: React.ReactNode;
  title: string;
  description?: string;
  minHeightClassName?: string;
}>;

function SectionCard({
  children,
  icon,
  title,
  description,
  minHeightClassName = "",
}: SectionCardProps) {
  return (
    <section
      className={[
        "rounded-[1.5rem] border border-border bg-card/95 p-6 shadow-sm",
        minHeightClassName,
      ].join(" ")}
    >
      <header className="mb-4 flex items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-surface-elevated text-primary">
          {icon}
        </div>
        <div className="min-w-0">
          <h2 className="text-base font-semibold text-foreground">{title}</h2>
          {description ? (
            <p className="mt-1 text-sm leading-6 text-muted-foreground">{description}</p>
          ) : null}
        </div>
      </header>

      {children}
    </section>
  );
}

function StatusPill({
  label,
  tone = "neutral",
}: Readonly<{ label: string; tone?: "neutral" | "primary" | "warning" }>) {
  const toneClassName =
    tone === "primary"
      ? "border-primary/20 bg-primary/10 text-primary"
      : tone === "warning"
        ? "border-amber-500/20 bg-amber-500/10 text-amber-600 dark:text-amber-300"
        : "border-border bg-surface-elevated text-muted-foreground";

  return (
    <span
      className={[
        "inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-medium uppercase tracking-[0.18em]",
        toneClassName,
      ].join(" ")}
    >
      {label}
    </span>
  );
}

export function SimulationWorkbenchShell() {
  return (
    <div className="flex flex-col gap-6">
      <section className="rounded-[1.5rem] border border-border bg-card/95 p-5 shadow-sm">
        <h1 className="text-[2.1rem] font-semibold tracking-tight text-foreground">
          Circuit Simulation
        </h1>
      </section>

      <section className="rounded-[1.5rem] border border-border bg-card/95 p-5 shadow-sm">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
          <div className="flex min-w-0 flex-1 items-center gap-3 rounded-xl border border-border bg-surface px-4 py-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-surface-elevated text-primary">
              <CircuitBoard size={18} />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
                Active Schema
              </p>
              <p className="truncate text-sm font-medium text-foreground">
                Fluxonium Readout Chain v0.3
              </p>
            </div>
            <button
              type="button"
              disabled
              className="inline-flex items-center gap-2 rounded-xl border border-border bg-surface-elevated px-3 py-2 text-sm text-muted-foreground"
            >
              FloatingQubitWithXYLine
              <ChevronDown size={16} />
            </button>
          </div>

          <div className="flex items-center gap-2">
            <StatusPill label="API pending" />
          </div>
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[minmax(340px,420px)_minmax(0,1fr)]">
        <div className="flex flex-col gap-6">
          <SectionCard
            icon={<FolderKanban size={18} />}
            title="Netlist Configuration"
            description="This follows the same source-form and expansion flow as the NiceGUI schema editor preview."
          >
            <div className="overflow-hidden rounded-[1.25rem] border border-border bg-[#091734] shadow-inner">
              <pre className="overflow-x-auto px-5 py-4 text-sm leading-7 text-slate-100">
{`{
  'name': 'FloatingQubitWithXYLine',
  'components': [
    {'name': 'R50', 'default': 50.0, 'unit': 'Ohm'},
    {'name': 'L_q', 'value_ref': 'L_q', 'unit': 'nH'},
    {'name': 'C_q', 'default': 0.05814, 'unit': 'pF'},
    {'name': 'C_g1', 'default': 0.10254, 'unit': 'pF'},
    {'name': 'C_g2', 'default': 0.10189, 'unit': 'pF'}
  ],
  'topology': [
    ('P1', '1', '0', 1),
    ('R_p1', '1', '0', 'R50'),
    ('P2', '2', '0', 2),
    ('R_p2', '2', '0', 'R50')
  ],
  'parameters': [{'name': 'L_q', 'default': 10.0, 'unit': 'nH'}]
}`}
              </pre>
            </div>
          </SectionCard>

          <SectionCard
            icon={<FlaskConical size={18} />}
            title="Simulation Controls"
            description="Frequency sweep setup, worker dispatch, and termination compensation will land here."
          >
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-xl border border-border bg-surface px-4 py-3">
                <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">
                  Frequency Range
                </p>
                <p className="mt-2 text-sm font-medium text-foreground">4.0 GHz to 8.0 GHz</p>
              </div>
              <div className="rounded-xl border border-border bg-surface px-4 py-3">
                <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">
                  Sweep Samples
                </p>
                <p className="mt-2 text-sm font-medium text-foreground">801 points</p>
              </div>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              <button
                type="button"
                disabled
                className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-sm font-medium text-primary-foreground opacity-80"
              >
                <Play size={16} />
                Run Simulation
              </button>
              <button
                type="button"
                disabled
                className="inline-flex items-center gap-2 rounded-xl border border-border bg-surface-elevated px-4 py-2 text-sm text-muted-foreground"
              >
                <WandSparkles size={16} />
                Run Post Processing
              </button>
            </div>
          </SectionCard>

          <SectionCard
            icon={<Activity size={18} />}
            title="Simulation Log"
            description="The NiceGUI page streams worker status here. This will become the same persistent authority log."
            minHeightClassName="min-h-[280px]"
          >
            <div className="space-y-3">
              {[
                "[21:40:03] Ready for persisted worker dispatch.",
                "[21:40:03] Active design scope will be resolved from the dataset selector.",
                "[21:40:03] Simulation and post-processing status lines will stream here.",
              ].map((line) => (
                <div
                  key={line}
                  className="rounded-xl border border-border bg-surface px-4 py-3 text-sm text-muted-foreground"
                >
                  {line}
                </div>
              ))}
            </div>
          </SectionCard>
        </div>

        <div className="flex flex-col gap-6">
          <SectionCard
            icon={<FlaskConical size={18} />}
            title="Simulation Results"
            description="Raw family switching, result charts, and sweep explorers land here."
            minHeightClassName="min-h-[360px]"
          >
            <div className="flex h-full min-h-[260px] flex-col justify-between rounded-[1.25rem] border border-dashed border-border bg-surface px-5 py-5">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">
                  Result Explorer
                </p>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">
                  This panel will host the same raw result families as NiceGUI: S, Y, Z, gain, and
                  compensated previews, plus the parameter-sweep result view.
                </p>
              </div>
              <div className="mt-6 grid gap-3 sm:grid-cols-3">
                <div className="rounded-xl bg-card px-4 py-3">
                  <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Family</p>
                  <p className="mt-2 text-sm font-medium text-foreground">S-Parameters</p>
                </div>
                <div className="rounded-xl bg-card px-4 py-3">
                  <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Source</p>
                  <p className="mt-2 text-sm font-medium text-foreground">Raw / PTC preview</p>
                </div>
                <div className="rounded-xl bg-card px-4 py-3">
                  <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Status</p>
                  <p className="mt-2 text-sm font-medium text-foreground">Awaiting worker output</p>
                </div>
              </div>
            </div>
          </SectionCard>

          <SectionCard
            icon={<ScrollText size={18} />}
            title="Post Processing Results"
            description="Processed traces, stale-result warnings, and saved-batch history will appear here."
            minHeightClassName="min-h-[320px]"
          >
            <div className="flex min-h-[220px] items-center justify-center rounded-[1.25rem] border border-dashed border-border bg-surface px-5 py-5 text-center">
              <div className="max-w-md">
                <p className="text-sm font-medium text-foreground">
                  Post-processing output is still a placeholder.
                </p>
                <p className="mt-3 text-sm leading-6 text-muted-foreground">
                  The next migration step will wire result tabs, stale-state warnings, and saved
                  output lineage from the worker-backed simulation flow.
                </p>
              </div>
            </div>
          </SectionCard>
        </div>
      </div>
    </div>
  );
}
